import pathlib
import subprocess
import sys
import tempfile

from rdflib import Graph, Namespace, RDF, URIRef


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEMO = ROOT / "demos" / "pivtxt2rdf"

VEC_FILE = DEMO / "data" / "sample_insight.vec"
ONTOLOGY = DEMO / "ontologies" / "pivmeta.ttl"
SCRIPT = DEMO / "vec2rdf.py"

PIV = Namespace("https://matthiasprobst.github.io/pivmeta#")


def test_vec2rdf_cli_generates_valid_turtle_and_passes_shacl():
    assert VEC_FILE.exists(), "Missing test fixture .vec file"
    assert ONTOLOGY.exists(), "Missing ontology file"
    assert SCRIPT.exists(), "Missing vec2rdf script"

    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "out.ttl"
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(VEC_FILE),
                str(ONTOLOGY),
                "--base-uri",
                "http://example.org/",
                "--output",
                str(out),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )

        assert proc.returncode == 0, f"vec2rdf failed: {proc.stdout}\n{proc.stderr}"
        assert out.exists(), "Expected Turtle output file not created"
        assert "SHACL Validation: PASS" in proc.stdout

        g = Graph().parse(out, format="turtle")
        dataset_iri = URIRef("http://example.org/" + VEC_FILE.stem)

        assert (dataset_iri, RDF.type, PIV.PIVDataset) in g
        # Ensure the minimum structural links exist.
        assert any(g.objects(dataset_iri, PIV.hasSetup))


def test_vec2rdf_show_header_prints_expected_keys():
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(VEC_FILE), str(ONTOLOGY), "--show-header"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "Application=PIV" in proc.stdout
    assert "SourceImageWidth=4008" in proc.stdout


def test_compact_turtle_file_preserves_triple_count():
    # Import demo utils by path (demo isn't a Python package).
    utils_path = DEMO / "utils.py"
    sys.path.insert(0, str(DEMO))
    try:
        import utils  # type: ignore

        g1 = Graph().parse(ONTOLOGY, format="turtle")
        compacted = utils.compact_turtle_file(str(ONTOLOGY))
        g2 = Graph().parse(data=compacted, format="turtle")
        assert len(g1) == len(g2)
    finally:
        if str(DEMO) in sys.path:
            sys.path.remove(str(DEMO))
