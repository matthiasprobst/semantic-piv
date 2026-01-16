# pivtxt2rdf

## Idea
- Often PIV data is shared in text format, see for example the PIV Challenge datasets (https://www.pivchallenge.org/)
- Using an ontology in combination with an LLM, we can extract semantic metadata from text input and convert it to RDF format
- Inspect the resulting RDF to see how the PIVMeta ontology can be used to describe PIV experiments
- Publish it (after carful review) alongside the original data to improve its FAIRness on your data repository

This demo shows how to use a simple Python script to convert PIV text data into RDF using the PIVMeta ontology.

## Next steps
- Allow more input formats (e.g., CSV, XML)
- Improve the LLM prompt for better metadata extraction
- Use MCP server specialize on certain formats or PIV software


## Example usage:

1. Navigate to this directory:
   ```bash
   cd demos/pivtxt2rdf
   ```
   
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Provide a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
5. Run the conversion script (call `-h` for help):
   ```bash
   python .\main.py .\data\piv_challenge_01_case_a.html .\ontologies\pivmeta.ttl
    ```