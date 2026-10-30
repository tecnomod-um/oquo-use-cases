# OQUO use cases

Use cases, examples and supporting services for the [Ontology QUality Ontology (OQUO)](https://github.com/tecnomod-um/oquo).

OQUO is a framework-agnostic ontology for describing **quality models** (quality characteristics, subcharacteristics, metrics and measurement scales) and the **results of quality evaluations** (observations, measured values, scale conversions and detected issues). Its modular design separates a common core from the quality models and from the modules that integrate concrete evaluation frameworks, so that the outputs of independently developed tools can be represented, compared and aggregated within a single model.

This repository shows OQUO in practice. It gathers complete, reproducible examples in which real ontologies are evaluated with existing quality frameworks and the results are represented as OQUO-compliant RDF.

## Purpose

The repository aims to:

- **Illustrate how OQUO is used** with different quality models and evaluation frameworks, from the definition of metrics and scales to the representation of evaluation results.
- **Show how a new framework is integrated** by extending OQUO with a module that defines its metrics, raw scales, scale conversions and issue types, and by converting its native output into OQUO-compliant RDF.
- **Provide reproducible material** for the publications about OQUO, including the outputs of the tools, the generated RDF and the services used to produce it.

## Structure

```
oquo-use-cases/
├── endpoints/                      services to run the evaluation and conversion pipeline
│   ├── docker-compose.yml
│   ├── .env                        ports on which the services are exposed
│   ├── foops/
│   ├── foops-to-oquo-converter/
│   └── oquo-instance-creator-endpoint/
├── FAIR/                           use cases based on the FAIR quality model
│   └── FOOPS/
│       ├── source_results/
│       ├── oquo_module/
│       └── oquo_compliant_results/
├── OQuaRE/                         use cases based on the OQuaRE quality model (in preparation)
├── LICENSE
└── README.md
```

### Quality models and frameworks

The repository is organised by quality model. Each quality model has its own folder (`FAIR`, `OQuaRE`), which contains one folder per evaluation framework used to measure it. Every framework folder follows the same structure:

| Folder | Content |
|---|---|
| `source_results/` | Results of the evaluations as originally returned by the framework (e.g. JSON). |
| `oquo_module/` | OQUO extension module of the framework: metrics and their association with the characteristics of the quality model, raw scales, conversions from the raw scales into the scale of the quality model, and issue types. |
| `oquo_compliant_results/` | The results in `source_results/` expressed as OQUO-compliant RDF. |

The quality models themselves (e.g. `oquo-fair-qm`, `oquo-oquare-qm`) are maintained in the [oquo](https://github.com/tecnomod-um/oquo) repository together with the OQUO core, and are imported by the framework modules through their persistent URLs (PURLs). Frameworks that already provide their own OQUO module, such as [HURON](https://github.com/tecnomod-um/huron), only include their results here.

#### Current use cases

| Quality model | Framework | OQUO module | Evaluated ontologies |
|---|---|---|---|
| FAIR ([`oquo-fair-qm`](https://purl.org/oquo-fair-qm)) | [FOOPS!](https://w3id.org/foops/) 0.4.0 | [`oquo-foops`](FAIR/FOOPS/oquo_module/oquo-foops.owl) (https://purl.org/oquo-foops) | OQUO core |

The `oquo_module` folder also contains an OWL catalog file (`catalog-v001.xml`), used by tools based on the OWL API, such as Protégé, to resolve the imports of the module.

### Endpoints

The `endpoints` folder contains the services needed to evaluate an ontology and obtain its results as OQUO-compliant RDF. All of them are packaged as Docker images and can be started together with Docker Compose.

| Service | Default port | Endpoint | Description |
|---|---|---|---|
| `foops` | 8002 | `POST /assessOntology` | [FOOPS!](https://github.com/oeg-upm/fair_ontologies) server (version 0.4.0), which assesses the FAIRness of an ontology and returns the results as JSON. |
| `foops-to-oquo-converter` | 8001 | `POST /foopsToOquo` | REST service that receives the JSON returned by FOOPS! and returns the results as OQUO-compliant RDF (Turtle), according to the `oquo-foops` module. It relies on the `oquo-instance-creator` service to generate the RDF. |
| `oquo-instance-creator` | 8000 | `POST /toOquoObservation` | [REST service](https://github.com/tecnomod-um/oquo-instance-creator-endpoint) that turns descriptions of measured values into OQUO-compliant RDF. |

The evaluation pipeline is:

```
 ontology URI ──▶ foops ──JSON──▶ foops-to-oquo-converter ──▶ oquo-instance-creator
                                          │
                                          └──▶ OQUO-compliant RDF (Turtle)
```

#### Running the services

Requirements: [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

```bash
cd endpoints
docker compose up --build
```

The ports on which the services are exposed are defined in the `endpoints/.env` file:

```dotenv
OQUO_INSTANCE_CREATOR_PORT=8000
FOOPS_TO_OQUO_CONVERTER_PORT=8001
FOOPS_PORT=8002
```

Changing these values only changes the ports published on the host. Inside the Docker Compose network, the services always communicate through their internal ports, so the converter reaches the instance creator at `http://oquo-instance-creator:8000/toOquoObservation` regardless of the published ports.

#### Examples

The examples below use the default ports.

**1. Assess an ontology with FOOPS!**

```bash
curl -X POST http://localhost:8002/assessOntology \
     -H "Content-Type: application/json;charset=UTF-8" \
     -d '{"ontologyUri": "https://w3id.org/okn/o/sd"}' \
     -o foops_results.json
```

The assessment may take some time, since FOOPS! retrieves the ontology and queries external registries.

**2. Convert the FOOPS! results into OQUO-compliant RDF**

```bash
curl -X POST http://localhost:8001/foopsToOquo \
     -H "Content-Type: application/json" \
     -d @foops_results.json \
     -o oquo_results.ttl
```

**3. Both steps at once**

```bash
curl -s -X POST http://localhost:8002/assessOntology \
     -H "Content-Type: application/json;charset=UTF-8" \
     -d '{"ontologyUri": "https://w3id.org/okn/o/sd"}' \
| curl -s -X POST http://localhost:8001/foopsToOquo \
     -H "Content-Type: application/json" \
     -d @- \
     -o oquo_results.ttl
```

The instance creator can also be called directly to generate OQUO-compliant RDF from any other source of results; see its [API reference](https://github.com/tecnomod-um/oquo-instance-creator-endpoint#api-reference).

## Reproducibility

The use cases are designed to be reproducible:

- The original outputs of the frameworks are kept, so that the OQUO-compliant RDF can be regenerated and checked against them.
- The versions of the frameworks are fixed (e.g. FOOPS! 0.4.0), and all the services used in the pipeline are provided as Docker images.
- OQUO modules are imported through their PURLs, so that they can be moved to other repositories without affecting the ontologies that import them.

## Related resources

| Resource | Description |
|---|---|
| [oquo](https://github.com/tecnomod-um/oquo) | OQUO core and quality models (e.g. OQuaRE, FAIR). |
| [oquo-instance-creator-endpoint](https://github.com/tecnomod-um/oquo-instance-creator-endpoint) | REST service that turns evaluation results into OQUO-compliant RDF. |
| [oquo-instance-creator](https://github.com/tecnomod-um/oquo-instance-creator) | Java library behind the REST service. |
| [HURON](https://github.com/tecnomod-um/huron) | Framework for assessing the human readability of ontologies, with its own OQUO module. |
| [FOOPS!](https://github.com/oeg-upm/fair_ontologies) | Ontology pitfall scanner for the FAIR principles. |
| [QASAR](https://semantics.inf.um.es/qasar) | Ontology quality assurance platform whose data model is OQUO. |

## Status

This repository is under active development. Quality models, frameworks and use cases will be added progressively.

## How to cite

Citation information will be added when the associated publication is available.

## License

See the [LICENSE](LICENSE) file. FOOPS! is distributed under its own license; see its [repository](https://github.com/oeg-upm/fair_ontologies).

## Contact

[TECNOMOD research group](https://github.com/tecnomod-um), Universidad de Murcia.