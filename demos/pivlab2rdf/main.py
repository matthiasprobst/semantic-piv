import pathlib

import dotenv
import h5rdmtoolbox as h5tbx
from pivpy import io

from demos.pivtxt2rdf.main import txt2rdf
from demos.pivtxt2rdf.utils import download_github_file

dotenv.load_dotenv(pathlib.Path.home() / ".env")


def main():
    filename = pathlib.Path("test_pivlab.mat")
    if not filename.exists():
        url = "https://raw.githubusercontent.com/alexlib/pivpy/master/pivpy/data/pivlab/test_pivlab.mat"
        filename = download_github_file(url, target_filename="test_pivlab.mat")
    ds = io.load_pivlab(filename)
    with h5tbx.File(filename) as h5:
        h5.dumps(filename)
    print(ds.attrs)
    with open("test_pivlab.attrs", "w", encoding="utf-8") as f:
        for key, value in ds.attrs.items():
            f.write(f"{key}: {value}\n")
    txt2rdf(
        input_file="test_pivlab.attrs",
        ontology_file="../pivtxt2rdf/ontologies/pivmeta.ttl",
        prompt_only=False,
        base_uri="http://example.org/",
        llm_url='https://api.openai.com/v1',
        model='gpt-5.2'
    )


if __name__ == "__main__":
    main()
