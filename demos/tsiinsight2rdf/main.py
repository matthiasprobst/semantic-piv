import pathlib
from pprint import pprint

import dotenv
from pivpy import io

from demos.pivtxt2rdf.main import txt2rdf
from demos.pivtxt2rdf.utils import download_github_file

dotenv.load_dotenv(pathlib.Path.home() / ".env")


def main():
    filename = pathlib.Path("Run000001.T000.D000.P000.H001.L.vec")
    if not filename.exists():
        url = "https://raw.githubusercontent.com/alexlib/pivpy/master/pivpy/data/Insight/Run000001.T000.D000.P000.H001.L.vec"
        filename = download_github_file(url, target_filename="Run000001.T000.D000.P000.H001.L.vec")

    reader = io.InsightVECReader()
    metadata = reader.read_metadata(filename)
    pprint(metadata.__dict__)
    with open("Run000001.T000.D000.P000.H001.L.attrs", "w", encoding="utf-8") as f:
        for key, value in metadata.__dict__.items():
            f.write(f"{key}: {value}\n")
    txt2rdf(
        input_file="Run000001.T000.D000.P000.H001.L.attrs",
        ontology_file="../pivtxt2rdf/ontologies/pivmeta.ttl",
        prompt_only=False,
        base_uri="http://example.org/",
        llm_url='https://api.openai.com/v1',
        model='gpt-5.2'
    )


if __name__ == "__main__":
    main()
