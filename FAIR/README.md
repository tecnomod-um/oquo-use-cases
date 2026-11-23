# FAIR use cases

Use cases of OQUO based on the **FAIR quality model**, in which ontologies are evaluated with FAIR assessment tools and their results are represented as OQUO-compliant RDF.

## The FAIR quality model

The FAIR quality model ([`oquo-fair-qm`](https://purl.org/oquo-fair-qm), `https://purl.org/oquo-fair-qm`) represents the [FAIR Guiding Principles](https://doi.org/10.1038/sdata.2016.18) as a quality model of OQUO:

- The four FAIR principles (Findable, Accessible, Interoperable and Reusable) are quality characteristics, and their sub-principles (F1–F4, A1, A1.1, A1.2, A2, I1–I3, R1, R1.1–R1.3) are their subcharacteristics.
- Characteristics and subcharacteristics are measured on a percentage scale of degree of compliance (`oquo-fair-qm:PercentageScale`, from 0 to 100).

The quality model is maintained in the [oquo](https://github.com/tecnomod-um/oquo) repository, together with the OQUO core, and is imported by the modules of the frameworks below through its persistent URL.

## Use cases

| Folder | Framework | OQUO module | Evaluated ontologies |
|---|---|---|---|
| [`FOOPS/`](FOOPS/) | [FOOPS!](https://w3id.org/foops/) 0.4.0 | [`oquo-foops`](FOOPS/oquo_module/oquo-foops.owl) (`https://purl.org/oquo-foops`) | OQUO core |
| [`OFAIRE/`](OFAIRE/) | [O'FAIRe](https://github.com/agroportal/fairness) | [`oquo-ofaire`](OFAIRE/oquo_module/oquo-ofaire.owl) (`https://purl.org/oquo-ofaire`) | OQUO core |

The two frameworks assess the FAIRness of ontologies in different ways:

- **FOOPS!** runs a set of checks on the ontology and its metadata, each one associated with a FAIR principle, and reports the proportion of tests passed by each check.
- **O'FAIRe** answers a set of questions about the metadata of an ontology stored in an OntoPortal repository, each one associated with a FAIR principle, and gives a number of credits to each answer.

Each module defines the metrics of its framework (the checks of FOOPS!, the questions of O'FAIRe), associates them with the characteristics of the FAIR quality model, and define scale conversions between their raw scales into the percentage scale of the model. This makes the results of the two frameworks comparable, characteristic by characteristic.

Each framework folder contains:

| Folder | Content |
|---|---|
| `source_results/` | Results of the evaluations as originally returned by the framework (JSON). |
| `oquo_module/` | OQUO module of the framework: metrics, raw scales, scale conversions, issue types (FOOPS!) and software agent. |
| `oquo_compliant_results/` | The results in `source_results/` expressed as OQUO-compliant RDF. |
| `evaluate.sh` | Script that assesses the OQUO core with the framework and converts the results into OQUO-compliant RDF. |

`OFAIRE/` also contains `ontoportal_data/`, with the descriptions of the ontologies loaded in OntoPortal to be assessed by O'FAIRe.

## Running the evaluations

The services that evaluate the ontologies and convert the results into OQUO-compliant RDF are in the [`services`](../services/) folder. See the [main README](../README.md#services) for how to start them and for examples with both frameworks.
