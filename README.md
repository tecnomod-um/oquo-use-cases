# OQUO use cases

Use cases, examples and supporting modules for the [Ontology QUality Ontology (OQUO)](https://github.com/tecnomod-um/oquo).

OQUO is a framework-agnostic ontology for describing **quality models** (quality characteristics, subcharacteristics, metrics and measurement scales) and the **results of quality evaluations** (observations, measured values, scale conversions and detected issues). Its modular design separates a common core from the quality models and from the modules that integrate concrete evaluation frameworks, so that the outputs of independently developed tools can be represented, compared and aggregated within a single model.

This repository shows OQUO in practice. It gathers complete, reproducible examples in which real ontologies are evaluated with existing quality frameworks and the results are represented as OQUO-compliant RDF and queried with SPARQL.

## Purpose

The repository aims to:

- **Illustrate how OQUO is used** with different quality models and evaluation frameworks, from the definition of metrics and scales to the querying of evaluation results.
- **Show how a new framework is integrated** by extending OQUO with a module that defines its metrics, raw scales, scale conversions and issue types.
- **Provide reproducible material** for the publications about OQUO, including the evaluated ontologies, the raw outputs of the tools, the generated RDF and the queries used to obtain the reported results.

## Structure

The repository is organised by quality model. Each quality model has its own folder, which contains the framework modules that measure it and the use cases built on it.

```
oquo-use-cases/
├── FAIR/                    use cases based on the FAIR quality model (oquo-fair-qm)
│   └── framework_modules/
│       └── oquo-foops.owl
├── OQuaRE/                  use cases based on the OQuaRE quality model (oquo-oquare-qm)
│   └── framework_modules/
├── LICENSE
└── README.md
```

The quality models themselves (e.g. `oquo-fair-qm`, `oquo-oquare-qm`) are maintained in the [oquo](https://github.com/tecnomod-um/oquo) repository together with the OQUO core, and are imported by the modules of this repository through their PURLs.

### Framework modules

The `framework_modules` folder of each quality model contains OQUO extension modules for frameworks that do not provide their own OQUO module. Each module imports a quality model and defines the metrics of the framework, the raw scale of each metric, the conversions from the raw scales into the scale of the quality model, and the types of issues the framework can report.

| Quality model | Module | IRI | Description |
|---|---|---|---|
| FAIR (`oquo-fair-qm`) | [`oquo-foops`](FAIR/framework_modules/oquo-foops.owl) | https://purl.org/oquo-foops | Metrics and issues of [FOOPS!](https://w3id.org/foops/), an ontology pitfall scanner for the FAIR principles. |

Frameworks that already provide their own OQUO module, such as [HURON](https://github.com/tecnomod-um/huron), are not included here and are imported from their own repositories.

Modules are identified by persistent URLs (PURLs), so they can be moved to other repositories without affecting the ontologies that import them.

### Use cases

Use cases will be stored in the folder of the quality model they are based on, one folder per use case, and will follow the same structure:

| Folder / file | Content |
|---|---|
| `README.md` | Goal of the use case, OQUO modules involved, key queries and expected results. |
| `ontologies.csv` | Ontologies evaluated, with their exact versions, download URLs and checksums. |
| `raw/` | Outputs of the evaluation tools, as returned by them. |
| `rdf/` | OQUO-compliant RDF generated from the raw outputs. |
| `queries/` | SPARQL queries used in the use case. |
| `results/` | Results of the queries, and the tables and figures derived from them. |
| `run.sh` | Script that reproduces the use case from the raw outputs to the results. |

## Related resources

| Resource | Description |
|---|---|
| [oquo](https://github.com/tecnomod-um/oquo) | OQUO core and quality models (e.g. OQuaRE, FAIR). |
| [oquo-instance-creator-endpoint](https://github.com/tecnomod-um/oquo-instance-creator-endpoint) | REST service that turns evaluation results into OQUO-compliant RDF. |
| [oquo-instance-creator](https://github.com/tecnomod-um/oquo-instance-creator) | Java library behind the REST service. |
| [HURON](https://github.com/tecnomod-um/huron) | Framework for assessing the human readability of ontologies, with its own OQUO module. |
| [QASAR](https://semantics.inf.um.es/qasar) | Ontology quality assurance platform whose data model is OQUO. |

## Reproducibility

The use cases are designed to be reproducible:

- OQUO modules are imported through their PURLs and resolved to specific released versions, so that the examples keep working as the modules evolve.
- The exact version of every evaluated ontology is recorded, together with a checksum.
- The raw outputs of the tools are kept, so that the RDF can be regenerated and checked against them.

## Status

This repository is under active development. Modules and use cases will be added progressively.

## How to cite

Citation information will be added when the associated publication is available.

## License

See the [LICENSE](LICENSE) file.

## Contact

[TECNOMOD research group](https://github.com/tecnomod-um), Universidad de Murcia.