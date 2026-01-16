"""
This demo show how to convert text-based PIV information into RDF format using a particular ontology and AI
"""
import os
import pathlib
import sys

import click
import dotenv
from openai import OpenAI  # For API compatibility
from pyshacl import validate
from rdflib import Graph

dotenv.load_dotenv(".env")

# read the system prompt:
with open(pathlib.Path(__file__).parent / 'SYSTEM_PROMPT.txt', 'r', encoding='utf-8') as f:
    SYSTEM_PROMPT = f.read()

def _get_token():
    token = os.getenv('CHATGPT_TOKEN') or os.getenv('OPENAI_API_KEY')
    if not token:
        print("Error: Please set CHATGPT_TOKEN or OPENAI_API_KEY in your environment.")
        sys.exit(1)
    return token


@click.command()
@click.argument('input_file')
@click.argument('ontology_file')
@click.option("--prompt-only", is_flag=True, help="Only output the LLM prompt and exit")
@click.option("--base-uri", default="http://example.org/", help="Base URI for minting IRIs")
@click.option('--llm-url',
              default='https://api.openai.com/v1',
              help='LLM API base URL (default: OpenAI ChatGPT API https://api.openai.com/v1)')
@click.option('--model',
              default='gpt-5.2',
              help='LLM model name (default: ChatGPT-like gpt-5.2)')
def main(input_file, ontology_file, prompt_only, base_uri, llm_url, model):
    # Read files
    with open(input_file, 'r', encoding='utf-8') as f:
        text_content = f.read()

    ont_graph = Graph().parse(ontology_file, format='turtle')

    # LLM prompt for constrained RDF generation
    USER_PROMPT = f"""
BASE_URI (for minting IRIs; optional):
{base_uri}

TEXT INPUT (only source of facts):
{text_content}

TASK:
- Convert TEXT INPUT into Turtle RDF instance data.
- Extract PIV case metadata AND provenance/curation metadata when present:
  - case title/name/identifier (e.g., "Open Package Case A")
  - description/notes
  - dates (e.g., 26.10.2000)
  - contact/author/contributor if an email/name exists (use ontology-allowed terms only)
  - facility/location/experiment context (e.g., DNW-LLF, model, U=60 m/s, FOV)
  - camera characteristics table
- Use BASE_URI when minting IRIs; otherwise prefer blank nodes.
- Output ONLY Turtle now.
"""

    if prompt_only:
        with open('llm_system_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(SYSTEM_PROMPT)
        with open('llm_user_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(USER_PROMPT)
        print("LLM prompt saved to llm_prompt.txt")
        sys.exit(0)

    # Call LLM
    api_token = _get_token()
    client = OpenAI(base_url=llm_url, api_key=api_token)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
        temperature=0.1,  # Low for determinism
    )
    ttl_str = response.choices[0].message.content.strip()


    with open('llm_generated_output.ttl', 'w', encoding='utf-8') as f:
        f.write(ttl_str)

    # Parse and validate RDF
    data_graph = Graph()
    try:
        data_graph.parse(data=ttl_str, format='turtle')
    except Exception as e:
        print(f"RDF parse error: {e}")
        sys.exit(1)

    # Merge ontology for validation context
    full_graph = ont_graph + data_graph

    conforms, v_graph, v_text = validate(
        full_graph,
        shacl_graph=ont_graph,  # Assume ontology includes SHACL
        inference="rdfs",
        abort_on_first=False
    )

    print("\nSHACL Validation:", "PASS" if conforms else "FAIL")
    if not conforms:
        with open('shacl_validation_report.ttl', 'w', encoding='utf-8') as f:
            f.write(v_graph.serialize(format='turtle'))
        with open('shacl_validation_report.txt', 'w', encoding='utf-8') as f:
            f.write(v_text)
        print("Validation report saved to shacl_validation_report.ttl and .txt")


    print(f"Please find the output file at 'llm_generated_output.ttl'. Next, you may check the TTL file by inserting "
          f"it RDF playgrounds like here: https://rdfplayground.dcc.uchile.cl/")
    # # Output final TTL
    # final_ttl = full_graph.serialize(format='turtle')
    # print("\nFinal Validated RDF (TTL):\n", final_ttl)
    #
    # # Save
    # input_filename = pathlib.Path(input_file).stem
    # output_filename = f"{input_filename}.ttl"
    # with open(output_filename, 'w', encoding="utf-8") as f:
    #     f.write(final_ttl)
    # print(f"\nSaved to {output_filename}")


if __name__ == '__main__':
    """example usage:
    
    python .\main.py .\data\piv_challenge_01_case_a.txt .\ontologies\pivmeta.ttl
    
    """
    main(["./data/piv_challenge_01_case_a.txt", "./ontologies/pivmeta.ttl"])
