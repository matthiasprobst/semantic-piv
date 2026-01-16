# semantic-piv 🌊

**Transform your PIV data into FAIR-compliant semantic metadata using AI**

Automatically extract structured, machine-readable metadata from your Particle Image Velocimetry experiments and convert it to RDF format for enhanced data sharing and discovery.

---

## 🎯 Why semantic-piv?

As a PIV researcher, you know the challenge of making your valuable experimental data **Findable, Accessible, Interoperable, and Reusable** (FAIR). Writing semantic metadata is time-consuming and requires expertise that many experimentalists don't have.

**semantic-piv** solves this by:
- 🤖 **Automatically extracting** experimental metadata from your existing text descriptions
- 🧠 **Using AI** (OpenAI GPT) to understand your PIV setup and parameters
- 📊 **Generating standards-compliant** RDF metadata using the PIVMeta ontology
- 🔍 **Making your data discoverable** in semantic data repositories
- ⚡ **Saving hours** of manual metadata writing

---

## 🚀 Quick Start

Transform your PIV experiment description into semantic metadata in minutes:

```bash
# Navigate to the demo
cd demos/pivtxt2rdf

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your_key_here" > .env

# Convert your PIV description to RDF
python main.py ./data/piv_challenge_01_case_a.txt ./ontologies/pivmeta.ttl
```

**Result**: Your PIV data is now described in rich, machine-readable RDF format ready for publication!

---

## 📋 What It Does

semantic-piv reads your PIV experiment descriptions and automatically extracts:

- **Experimental Setup** - Camera specifications, lighting configuration, seeding particles
- **Flow Parameters** - Velocity ranges, Reynolds numbers, flow conditions  
- **Measurement Details** - Image resolution, field of view, timing parameters
- **Equipment Information** - Camera models, lens specifications, laser details
- **Research Context** - Study objectives, facility information, investigator details

### Input Example
```
Strong vortex (provided by Kaehler) < real > [1280 x 1024]
Camera: PCO SensiCam, 1280x1024 pixel, 6.7 μm pixel size
Study: Wake vortex formation behind DLR ALVAST half model
U=60 m/s, measurement position 1.64 m behind wing tip
```

### Output Example
```turtle
@prefix piv: <https://matthiasprobst.github.io/pivmeta#> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<http://example.org/case-a> a piv:PIVDataset ;
  dcterms:title "Strong vortex experiment" ;
  dcterms:description "Wake vortex formation behind transport aircraft" ;
  piv:hasSetup _:setup ;
  piv:flowSpeed "60"^^xsd:decimal ;
  piv:measurementPosition "1.64"^^xsd:decimal .

_:setup a piv:ExperimentalSetup ;
  piv:hasCamera _:camera .

_:camera a piv:DigitalCamera ;
  piv:model "PCO SensiCam" ;
  piv:resolution "1280x1024" ;
  piv:pixelSize "6.7"^^xsd:decimal .
```

---

## 🧪 Perfect For

### PIV Challenge Datasets
Automatically generate metadata for PIV Challenge cases to make them FAIR-compliant.

### Research Groups
Standardize metadata generation across your team's PIV experiments.

### Data Repositories  
Enhance your institutional PIV collections with semantic metadata for better discovery.

### Journal Publications
Include machine-readable metadata alongside your published PIV datasets.

---

## 🏗️ How It Works

1. **Text Analysis** - AI reads your PIV experiment description
2. **Semantic Extraction** - Identifies key experimental parameters and relationships  
3. **Ontology Mapping** - Maps extracted information to PIVMeta ontology concepts
4. **RDF Generation** - Creates structured, standards-compliant metadata
5. **Validation** - Ensures output meets SHACL validation rules

---

## 📊 Supported Features

- ✅ **PIVMeta Ontology** - Standard vocabulary for PIV experiments
- ✅ **SHACL Validation** - Ensures metadata quality and consistency  
- ✅ **Multiple Input Formats** - Text files, HTML, structured descriptions
- ✅ **Custom Ontologies** - Use your own domain-specific ontologies
- ✅ **Batch Processing** - Handle multiple PIV datasets efficiently

---

## 🔧 Requirements

- Python 3.13+
- OpenAI API key
- Basic PIV experiment description (text format)

---

## 📚 Learn More

- **[Demo Walkthrough](demos/pivtxt2rdf/README.md)** - Detailed tutorial and examples
- **[PIVMeta Ontology](https://matthiasprobst.github.io/pivmeta/)** - Understand the semantic model
- **[FAIR Principles](https://www.go-fair.org/fair-principles/)** - Why semantic metadata matters

---

## 🤝 Contributing

This project is in early development and welcomes contributions from the PIV community! 

- **Researchers** - Help us improve metadata extraction for your specific PIV applications
- **Developers** - Add support for new input formats and ontologies  
- **Domain Experts** - Refine the PIVMeta ontology and validation rules

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🌟 Transform Your PIV Data Today

Stop spending hours writing metadata. Let AI do the work while you focus on what matters most - your fluid dynamics research.

**Get started in minutes with our interactive demo!** 🚀