import pathlib

import h5rdmtoolbox as h5tbx
import rdflib
from pivmetalib import pivmeta
from pivmetalib import sd


def pivlab2rdf(mat_filename: str, file_uri: str = "http://example.org/") -> None:
    """Deterministic conversion of a PIVlab .mat file to RDF Turtle format.

    Note: This is work in progress. The file has not much metadata, so the user may very likely
    pass a log of additional info here. Also we should write a piv2rdf function, which
    takes all info as arguments and the specialized functions like this one just extract
    the info from the file format and then call the generic piv2rdf function.
    """
    h5ttl = h5tbx.serialize(mat_filename, format='turtle', file_uri=file_uri)
    ttl_filename = pathlib.Path(mat_filename).with_suffix('.ttl')

    g = rdflib.Graph().parse(data=h5ttl, format="ttl")

    piv_software = sd.Software(
        id=rdflib.URIRef(file_uri + "pivlab_software"),
        name="PIVlab",
        url=rdflib.URIRef("https://pivlab.blogspot.com/p/download.html")
    )
    piv_setup = pivmeta.pivsetup.ExperimentalSetup(
        id=rdflib.URIRef(file_uri + "experimental_setup"),
        uses_analysis_software=piv_software
    )

    g = g + rdflib.Graph().parse(data=piv_setup.serialize(format="ttl"), format="ttl")

    dist = pivmeta.distribution.ImageVelocimetryDistribution(
        id=rdflib.URIRef(file_uri + pathlib.Path(mat_filename).name))
    ds = pivmeta.distribution.ImageVelocimetryDataset(id=rdflib.URIRef(file_uri + "dataset"),
                                                      distribution=dist)

    ds_ttl = ds.serialize(format="ttl")
    g = g + rdflib.Graph().parse(data=ds_ttl, format="ttl")

    with open(ttl_filename, 'w', encoding='utf-8') as f:
        f.write(g.serialize(format='turtle'))
    print(f"RDF data saved to {ttl_filename}")
