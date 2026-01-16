from demos.pivtxt2rdf.utils import download_github_file
import pathlib

from pivpy import io
from demos.pivtxt2rdf.main import txt2rdf
import dotenv

dotenv.load_dotenv(pathlib.Path.home() / ".env")

def main():
    filename = pathlib.Path("B00001.vc7")
    if not filename.exists():
        url = "https://raw.githubusercontent.com/alexlib/pivpy/master/pivpy/data/PIVMAT_jet/B00001.VC7"
        filename = download_github_file(url, target_filename="B00001.vc7")
    ds = io.read_piv(filename)
    print(ds.attrs)
    with open("B00001.attrs", "w", encoding="utf-8") as f:
        for key, value in ds.attrs.items():
            f.write(f"{key}: {value}\n")
    txt2rdf(
        input_file="B00001.attrs",
        ontology_file="../pivtxt2rdf/ontologies/pivmeta.ttl",
        prompt_only=False,
        base_uri="http://example.org/",
        llm_url='https://api.openai.com/v1',
        model='gpt-5.2'
    )


if __name__ == "__main__":
    main()
