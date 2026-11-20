# OQUO use cases

Use cases, examples and supporting services for the [Ontology QUality Ontology (OQUO)](https://github.com/tecnomod-um/oquo).

OQUO is a framework-agnostic ontology for describing **quality models** (quality characteristics, subcharacteristics, metrics and measurement scales) and the **results of quality evaluations** (observations, measured values, scale conversions and detected issues). Its modular design separates a common core from the quality models and from the modules that integrate concrete evaluation frameworks, so that the outputs of independently developed tools can be represented, compared and aggregated within a single model.

This repository shows OQUO in practice. It gathers complete, reproducible examples in which real ontologies are evaluated with existing quality frameworks and the results are represented as OQUO-compliant RDF.

## Purpose

The repository aims to:

- **Illustrate how OQUO is used** with different quality models and evaluation frameworks, from the definition of metrics and scales to the representation of evaluation results.
- **Show how a new framework is integrated** by extending OQUO with a module that defines its metrics, raw scales, scale conversions, issue types and software agent, and by converting its native output into OQUO-compliant RDF.
- **Provide reproducible material** for the publications about OQUO, including the outputs of the tools, the generated RDF and the services used to produce it.

## Structure

```
oquo-use-cases/
├── services/                       services to run the evaluation and conversion pipeline
│   ├── docker-compose.yml
│   ├── .env                        ports on which the services are exposed
│   ├── foops/                      FOOPS! server
│   ├── ontoportal/                 OntoPortal appliance with O'FAIRe
│   ├── to-oquo-converter/          converters of the results of the frameworks to OQUO
│   └── oquo-instance-creator-endpoint/
├── FAIR/                           use cases based on the FAIR quality model
│   ├── FOOPS/
│   │   ├── source_results/
│   │   ├── oquo_module/
│   │   └── oquo_compliant_results/
│   └── OFAIRE/
│       ├── ontoportal_data/        ontologies loaded in OntoPortal to be assessed
│       ├── evaluate.sh
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
| `source_results/` | Results of the evaluations as originally returned by the framework (e.g. JSON), and, when available, the versions of the tools used to obtain them. |
| `oquo_module/` | OQUO extension module of the framework: metrics and their association with the characteristics of the quality model, raw scales, conversions from the raw scales into the scale of the quality model, issue types and the software agent of the framework. |
| `oquo_compliant_results/` | The results in `source_results/` expressed as OQUO-compliant RDF. |

The quality models themselves (e.g. `oquo-fair-qm`, `oquo-oquare-qm`) are maintained in the [oquo](https://github.com/tecnomod-um/oquo) repository together with the OQUO core, and are imported by the framework modules through their persistent URLs (PURLs). Frameworks that already provide their own OQUO module, such as [HURON](https://github.com/tecnomod-um/huron), only include their results here. See [How to use OQUO](https://github.com/tecnomod-um/oquo#how-to-use-oquo) for what each kind of module contains.

#### Current use cases

| Quality model | Framework | OQUO module | Evaluated ontologies |
|---|---|---|---|
| FAIR ([`oquo-fair-qm`](https://purl.org/oquo-fair-qm)) | [FOOPS!](https://w3id.org/foops/) 0.4.0 | [`oquo-foops`](FAIR/FOOPS/oquo_module/oquo-foops.owl) (https://purl.org/oquo-foops) | OQUO core |
| FAIR ([`oquo-fair-qm`](https://purl.org/oquo-fair-qm)) | [O'FAIRe](https://github.com/agroportal/fairness) (commit `24def6b`) | [`oquo-ofaire`](FAIR/OFAIRE/oquo_module/oquo-ofaire.owl) (https://purl.org/oquo-ofaire) | OQUO core |

Each `oquo_module` folder also contains an OWL catalog file (`catalog-v001.xml`), used by tools based on the OWL API, such as Protégé, to resolve the imports of the module.

The two frameworks assess the FAIRness of ontologies in different ways: FOOPS! runs tests on the ontology and its metadata, and reports the proportion of tests passed by each check; O'FAIRe answers questions about the metadata of an ontology stored in an OntoPortal repository, and gives credits to each answer. Both modules convert their raw scales into the percentage scale of the FAIR quality model (`oquo-fair-qm:PercentageScale`), so that their results can be compared characteristic by characteristic.

### Services

The `services` folder contains the services needed to evaluate an ontology and obtain its results as OQUO-compliant RDF. All of them are packaged as Docker images and can be started together with Docker Compose.

| Service | Default port | Endpoints | Description |
|---|---|---|---|
| `foops` | 8002 | `POST /assessOntology` | [FOOPS!](https://github.com/oeg-upm/fair_ontologies) server (version 0.4.0), which assesses the FAIRness of an ontology and returns the results as JSON. |
| OntoPortal (`api`, `fairness`…) | 9393 | `GET /ofaire?ontologies=<ACRONYM>&sync` | [OntoPortal](https://ontoportal.org/) appliance with [O'FAIRe](https://github.com/agroportal/fairness), which assesses the FAIRness of the ontologies loaded in it and returns the results as JSON. See [`services/ontoportal`](services/ontoportal/README.md). |
| `to-oquo-converter` | 8001 | `POST /foopsToOquo`, `POST /foopsToOquoModel`, `POST /ofaireToOquo`, `POST /ofaireToOquoModel` | REST service that receives the JSON returned by a framework and returns the results as OQUO-compliant RDF (Turtle), according to the OQUO module of the framework. It relies on the `oquo-instance-creator` service to generate the RDF. |
| `oquo-instance-creator` | 8000 | `POST /toOquoObservation`, `POST /toOquoModel` | [REST service](https://github.com/tecnomod-um/oquo-instance-creator-endpoint) that turns descriptions of measured values into OQUO-compliant RDF. |

For each framework, the converter offers two methods:

- **`/<framework>ToOquo`** returns the results as OQUO observations, each one with its value on the raw scale of its metric.
- **`/<framework>ToOquoModel`** also returns the OQUO module of the framework, together with the ontologies it imports (the FAIR quality model and the OQUO core), and the values converted to the percentage scale of the FAIR quality model by the scale conversions of the module. The result is self-contained: it can be queried with SPARQL without loading any other ontology. The module can be changed with the `modelIRI` parameter; by default, it is `oquo-foops` or `oquo-ofaire`.

The results are attributed to the software agent of the framework, defined in its module (`oquo-foops:foops-software-agent`, `oquo-ofaire:ofaire-software-agent`), following the [provenance model of OQUO](https://github.com/tecnomod-um/oquo#provenance).

The evaluation pipelines are:

```
 FOOPS!
 ontology URI ──▶ foops ──JSON──▶ to-oquo-converter ──▶ oquo-instance-creator
                                   (/foopsToOquo…)              │
                                                                └──▶ OQUO-compliant RDF (Turtle)

 O'FAIRe
 ontology ──▶ OntoPortal (loaded at start) ──JSON──▶ to-oquo-converter ──▶ oquo-instance-creator
              /ofaire                               (/ofaireToOquo…)             │
                                                                                 └──▶ OQUO-compliant RDF (Turtle)
```

#### Running the services

Requirements:

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose 2.24 or later.
- At least 8 GB of RAM available for Docker, for OntoPortal.

```bash
cd services
docker compose up -d --build --wait
```

The first start builds the images, and loads and processes in OntoPortal the ontologies described in `FAIR/OFAIRE/ontoportal_data/`, which can take several minutes. `--wait` returns once all the services are ready. See [`services/ontoportal`](services/ontoportal/README.md) for how to add ontologies to OntoPortal and other options of the appliance.

The ports on which the services are exposed are defined in the `services/.env` file:

```dotenv
OQUO_INSTANCE_CREATOR_PORT=8000
TO_OQUO_CONVERTER_PORT=8001
FOOPS_PORT=8002
```

and the port of the OntoPortal API in `services/ontoportal/ontoportal.env` (`NGINX_API_PORT`, 9393 by default).

Changing these values only changes the ports published on the host. Inside the Docker Compose network, the services always communicate through their internal ports, so the converter reaches the instance creator at `http://oquo-instance-creator:8000` regardless of the published ports.

#### Examples

The examples below use the default ports.

**FOOPS!**

1. Assess an ontology:

   ```bash
   curl -X POST http://localhost:8002/assessOntology \
        -H "Content-Type: application/json;charset=UTF-8" \
        -d '{"ontologyUri": "https://w3id.org/okn/o/sd"}' \
        -o foops_results.json
   ```

   The assessment may take some time, since FOOPS! retrieves the ontology and queries external registries.

2. Convert the results into OQUO-compliant RDF:

   ```bash
   curl -X POST http://localhost:8001/foopsToOquo \
        -H "Content-Type: application/json" \
        -d @foops_results.json \
        -o oquo_results.ttl
   ```

   or, to also get the OQUO module and the values on the scale of the FAIR quality model:

   ```bash
   curl -X POST http://localhost:8001/foopsToOquoModel \
        -H "Content-Type: application/json" \
        -d @foops_results.json \
        -o oquo_model.ttl
   ```

3. Both steps at once:

   ```bash
   curl -s -X POST http://localhost:8002/assessOntology \
        -H "Content-Type: application/json;charset=UTF-8" \
        -d '{"ontologyUri": "https://w3id.org/okn/o/sd"}' \
   | curl -s -X POST http://localhost:8001/foopsToOquoModel \
        -H "Content-Type: application/json" \
        -d @- \
        -o oquo_model.ttl
   ```

**O'FAIRe**

O'FAIRe assesses the ontologies loaded in OntoPortal, identified by their acronym. The ontologies to load are described in `FAIR/OFAIRE/ontoportal_data/` (e.g. `OQUO-CORE.json` for the OQUO core).

1. Assess an ontology:

   ```bash
   curl -s "http://localhost:9393/ofaire?ontologies=OQUO-CORE&sync" -o ofaire_results.json
   ```

2. Convert the results into OQUO-compliant RDF:

   ```bash
   curl -X POST http://localhost:8001/ofaireToOquo \
        -H "Content-Type: application/json" \
        -d @ofaire_results.json \
        -o oquo_results.ttl
   ```

   or, to also get the OQUO module and the values on the scale of the FAIR quality model, use `/ofaireToOquoModel`. The IRI of the assessed ontology is taken from the results of O'FAIRe; if it is missing, give it in the `ontologyIRI` parameter.

`FAIR/OFAIRE/evaluate.sh` assesses the OQUO core with O'FAIRe and saves the results in `source_results/`, together with the versions of the ontology, OntoPortal, O'FAIRe and the Docker images used.

The instance creator can also be called directly to generate OQUO-compliant RDF from any other source of results; see its [API reference](https://github.com/tecnomod-um/oquo-instance-creator-endpoint#api-reference).

## Reproducibility

The use cases are designed to be reproducible:

- The original outputs of the frameworks are kept, so that the OQUO-compliant RDF can be regenerated and checked against them.
- The versions of the frameworks are fixed (FOOPS! 0.4.0, O'FAIRe at a given commit), all the services used in the pipeline are provided as Docker images, and the versions used in each run are recorded (e.g. `FAIR/OFAIRE/source_results/environment.txt`).
- OQUO modules are imported through their PURLs, so that they can be moved to other repositories without affecting the ontologies that import them.
- The OQUO-compliant results can be validated with the [SHACL shapes of OQUO](https://github.com/tecnomod-um/oquo/tree/main/SHACL).

## Related resources

| Resource | Description |
|---|---|
| [oquo](https://github.com/tecnomod-um/oquo) | OQUO core and quality models (e.g. OQuaRE, FAIR). |
| [oquo-instance-creator-endpoint](https://github.com/tecnomod-um/oquo-instance-creator-endpoint) | REST service that turns evaluation results into OQUO-compliant RDF. |
| [oquo-instance-creator](https://github.com/tecnomod-um/oquo-instance-creator) | Java library behind the REST service. |
| [HURON](https://github.com/tecnomod-um/huron) | Framework for assessing the human readability of ontologies, with its own OQUO module. |
| [FOOPS!](https://github.com/oeg-upm/fair_ontologies) | Ontology pitfall scanner for the FAIR principles. |
| [O'FAIRe](https://github.com/agroportal/fairness) | Ontology FAIRness evaluator of the OntoPortal repositories. |
| [ontoportal_docker](https://github.com/ontoportal-lirmm/ontoportal_docker) | Docker appliance of OntoPortal, on which the OntoPortal service is based. |
| [QASAR](https://semantics.inf.um.es/qasar) | Ontology quality assurance platform whose data model is OQUO. |

## Status

This repository is under active development. Quality models, frameworks and use cases will be added progressively.

## How to cite

If you use OQUO, please cite:

> Abad-Navarro, F., Duque-Ramos, A., Quesada-Martínez, M., Juanes-Cortés, B. and Fernández-Breis, J. T. (2026). OQUO: Towards a Unified Semantic Model of Ontology Quality. In *Proceedings of the 18th International Joint Conference on Knowledge Discovery, Knowledge Engineering and Knowledge Management (IC3K 2026) - Volume 2: KEOD*, pages 1037-1044. SciTePress. https://doi.org/10.5220/0015451300004985

## License

See the [LICENSE](LICENSE) file. FOOPS!, O'FAIRe and OntoPortal are distributed under their own licenses; see their repositories.

## Contact

[TECNOMOD research group](https://github.com/tecnomod-um), Universidad de Murcia.