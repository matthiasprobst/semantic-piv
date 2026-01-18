from piv2rdf import pivlab2rdf


def test_pivlab2rdf():
    filename = "demos/pivlab2rdf/test_pivlab.mat"
    pivlab2rdf(filename, file_uri="http://doi.org/uri/of/file/")