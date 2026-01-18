import pathlib

import dotenv
import h5py
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

    pivlab_prompt = """Below you find the metadata content of a PIVlab .mat file 'test_pivlab.mat' containing Particle Image Velocimetry data. 
The file includes metadata attributes that describe the experimental setup, measurement parameters, and processing details. 
Interpret the dataset values as m4i:NumericalVariable where applicable and add the min max values.

"""
    with h5tbx.File(filename) as h5:
        root_attrs = h5.attrs
        if root_attrs:
            pivlab_prompt += "Root attributes:\n"
            for key, value in root_attrs.items():
                pivlab_prompt += f"- {key}: {value}\n"
            pivlab_prompt += "\n"
        for dataset_name, dataset in h5.items():
            if isinstance(dataset, h5py.Dataset):
                data = dataset.values[()]
                try:
                    pivlab_prompt += f"Dataset '{dataset_name}' data type: {data.dtype}, shape: {data.shape}\n"
                    pivlab_prompt += f"Dataset '{dataset_name}' min value {data.min()}:\n"
                    pivlab_prompt += f"Dataset '{dataset_name}' max value {data.max()}:\n"
                    pivlab_prompt += f"Dataset '{dataset_name}' mean value {data.mean()}:\n"
                except Exception:
                    pass
                dataset_attrs = dataset.attrs
                if not dataset_attrs:
                    pivlab_prompt += f"Dataset '{dataset_name}' attributes:\n"
                    for key, value in dataset.attrs.items():
                        pivlab_prompt += f"- {key}: {value}\n"
                    pivlab_prompt += "\n"
        for group in h5.get_groups():
            group_name = group.name
            group_attrs = group.attrs
            if group_attrs:
                pivlab_prompt += f"Group '{group_name}' attributes:\n"
                for key, value in group.attrs.items():
                    pivlab_prompt += f"- {key}: {value}\n"
                pivlab_prompt += "\n"
                for dataset_name, dataset in group.items():
                    if isinstance(dataset, h5py.Dataset):
                        pivlab_prompt += f"Dataset '{dataset_name}' attributes:\n"
                        for key, value in dataset.attrs.items():
                            pivlab_prompt += f"- {key}: {value}\n"
                        pivlab_prompt += "\n"
    print(pivlab_prompt)
    with open("test_pivlab.attrs", "w", encoding="utf-8") as f:
        f.write(pivlab_prompt)
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
