"""Convert an Insight-style .vec file header into RDF/Turtle using the PIVMeta ontology.

This is a deterministic alternative to the LLM-based demo in main.py:
- reads a .vec file
- extracts metadata from the first header line (TITLE/VARIABLES/DATASETAUXDATA/ZONE)
- emits RDF instance data (Turtle)
- optionally validates against the provided ontology graph via pySHACL

Example:
  python vec2rdf.py \
    ../../.pivpy-src/pivpy/data/day2/day2a005000.T000.D000.P003.H001.L.vec \
    ./ontologies/pivmeta.ttl \
    --base-uri http://example.org/
"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

import click
from pyshacl import validate
from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from pivpy.io import parse_header


PIV = Namespace("https://matthiasprobst.github.io/pivmeta#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
M4I = Namespace("http://w3id.org/nfdi4ing/metadata4ing#")
OBO = Namespace("http://purl.obolibrary.org/obo/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")


_AUX_RE = re.compile(r"DATASETAUXDATA\s+(?P<key>[A-Za-z0-9_]+)=\"(?P<value>[^\"]*)\"")
_TITLE_RE = re.compile(r"TITLE=\"(?P<value>[^\"]*)\"")
_ZONE_RE = re.compile(r"ZONE\s+I=(?P<I>\d+),\s*J=(?P<J>\d+)")
_VARS_BLOCK_RE = re.compile(r"\bVARIABLES\s*=\s*(?P<block>.*?)(?:\bDATASETAUXDATA\b|\bZONE\b)", re.IGNORECASE)
_QUOTED_RE = re.compile(r"\"([^\"]+)\"")


def _safe_slug(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "resource"


def _maybe_number(value: str) -> tuple[bool, Any]:
    v = value.strip()
    if v == "":
        return False, value
    try:
        return True, float(v)
    except ValueError:
        return False, value


def _add_metric(g: Graph, distribution: URIRef | BNode, label: str, value: str) -> None:
    is_number, parsed = _maybe_number(value)
    metric = BNode()

    if is_number:
        g.add((metric, RDF.type, M4I.NumericalVariable))
        g.add((metric, SKOS.prefLabel, Literal(label)))
        g.add((metric, M4I.hasNumericalValue, Literal(parsed, datatype=XSD.decimal)))
    else:
        g.add((metric, RDF.type, M4I.TextVariable))
        g.add((metric, SKOS.prefLabel, Literal(label)))
        g.add((metric, M4I.hasValue, Literal(str(parsed))))

    g.add((distribution, PIV.hasMetric, metric))


def _extract_header_kv(filepath: str) -> dict[str, str]:
    """Extract key/value metadata from the first header line.

    Works for Insight-style Tecplot .vec headers like:
      TITLE="..." VARIABLES="X pixel", ... DATASETAUXDATA Foo="bar" ... ZONE I=.., J=..
    """
    p = pathlib.Path(filepath)
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        header_line = ""
        for line in f:
            if line.strip() == "":
                continue
            header_line = line.strip("\n")
            break

    kv: dict[str, str] = {}

    m = _TITLE_RE.search(header_line)
    if m:
        kv["TITLE"] = m.group("value")

    for m in _AUX_RE.finditer(header_line):
        kv[m.group("key")] = m.group("value")

    m = _ZONE_RE.search(header_line)
    if m:
        kv["ZONE_I"] = m.group("I")
        kv["ZONE_J"] = m.group("J")

    return kv


def _extract_variables_and_units(header_line: str) -> tuple[list[str], list[str]]:
    """Extract variable names and optional units from the VARIABLES=... header block.

    Example quoted entries: "X pixel", "CHC"
    Returns (variables, units) where units may be empty strings.
    """
    m = _VARS_BLOCK_RE.search(header_line)
    if not m:
        return [], []
    block = m.group("block")
    quoted = _QUOTED_RE.findall(block)
    variables: list[str] = []
    units: list[str] = []
    for item in quoted:
        parts = item.split()
        if not parts:
            continue
        variables.append(parts[0])
        units.append(parts[1] if len(parts) > 1 else "")
    return variables, units


@click.command()
@click.argument("vec_file")
@click.argument("ontology_file")
@click.option("--output", default="vec_generated_output.ttl", show_default=True, help="Output Turtle file")
@click.option("--base-uri", default="http://example.org/", show_default=True, help="Base URI for minting IRIs")
@click.option("--validate/--no-validate", "do_validate", default=True, show_default=True, help="Run pySHACL validation")
@click.option("--show-header", is_flag=True, help="Print extracted header metadata and exit")
def main(vec_file: str, ontology_file: str, output: str, base_uri: str, do_validate: bool, show_header: bool) -> None:
    vec_path = pathlib.Path(vec_file)
    if not vec_path.exists():
        raise click.ClickException(f"VEC file not found: {vec_file}")

    ont_path = pathlib.Path(ontology_file)
    if not ont_path.exists():
        raise click.ClickException(f"Ontology file not found: {ontology_file}")

    # Extract header metadata using pivpy (variables/units/grid size/delta_t) and a simple aux parser.
    _, _, rows, cols, delta_t, frame, header_line = parse_header(vec_path)
    variables, units = _extract_variables_and_units(header_line)
    header_kv = _extract_header_kv(str(vec_path))

    if show_header:
        click.echo("# parsed from header")
        click.echo(f"variables={variables}")
        click.echo(f"units={units}")
        click.echo(f"rows={rows} cols={cols} frame={frame} delta_t={delta_t}")
        click.echo("\n# header key/value")
        for k in sorted(header_kv.keys()):
            click.echo(f"{k}={header_kv[k]}")
        sys.exit(0)

    # Load ontology (for validation context + prefix bindings)
    ont_graph = Graph().parse(ont_path, format="turtle")

    # Build instance RDF
    g = Graph()

    # Reuse ontology prefixes where possible to keep output readable.
    g.namespace_manager = ont_graph.namespace_manager

    dataset_iri = URIRef(base_uri.rstrip("/") + "/" + _safe_slug(vec_path.stem))
    setup = BNode()
    distribution = BNode()
    piv_data_type = BNode()

    g.add((dataset_iri, RDF.type, PIV.PIVDataset))
    g.add((dataset_iri, DCTERMS.title, Literal(vec_path.stem)))

    if "TITLE" in header_kv and header_kv["TITLE"].strip():
        g.add((dataset_iri, DCTERMS.description, Literal(header_kv["TITLE"])))

    # OWL restriction in the ontology: ImageVelocimetryDataset must have some piv:Setup.
    g.add((dataset_iri, PIV.hasSetup, setup))
    g.add((setup, RDF.type, PIV.Setup))

    # Create a distribution node and attach header-derived metrics.
    # The ontology defines piv:hasMetric on piv:ImageVelocimetryDistribution.
    g.add((dataset_iri, OBO.BFO_0000051, distribution))  # dataset "has part" distribution
    g.add((distribution, RDF.type, PIV.ImageVelocimetryDistribution))

    # OWL restriction: ImageVelocimetryDistribution must have some piv:PIVDataType.
    g.add((distribution, PIV.hasPIVDataType, piv_data_type))
    g.add((piv_data_type, RDF.type, PIV.PIVDataType))

    # Add basic extracted metadata as metrics/variables.
    if rows is not None:
        _add_metric(g, distribution, "rows", str(rows))
    if cols is not None:
        _add_metric(g, distribution, "cols", str(cols))

    _add_metric(g, distribution, "frame", str(frame))
    _add_metric(g, distribution, "delta_t", str(delta_t))

    if variables:
        _add_metric(g, distribution, "variables", ",".join(variables))
    if units:
        _add_metric(g, distribution, "units", ",".join(units))

    # Add every DATASETAUXDATA and other extracted header fields.
    for k, v in sorted(header_kv.items()):
        if k == "TITLE":
            continue
        _add_metric(g, distribution, k, v)

    # Serialize
    out_path = pathlib.Path(output)
    out_path.write_text(g.serialize(format="turtle"), encoding="utf-8")

    click.echo(f"Wrote Turtle to {out_path}")

    if do_validate:
        # Merge ontology for validation context (same approach as the LLM demo).
        full_graph = ont_graph + g
        conforms, v_graph, v_text = validate(
            full_graph,
            shacl_graph=ont_graph,  # if the ontology contains SHACL shapes
            inference="rdfs",
            abort_on_first=False,
        )

        click.echo("\nSHACL Validation: " + ("PASS" if conforms else "FAIL"))
        if not conforms:
            pathlib.Path("shacl_validation_report_vec.ttl").write_text(
                v_graph.serialize(format="turtle"), encoding="utf-8"
            )
            pathlib.Path("shacl_validation_report_vec.txt").write_text(v_text, encoding="utf-8")
            click.echo("Validation report saved to shacl_validation_report_vec.ttl and .txt")




if __name__ == "__main__":
    main()
