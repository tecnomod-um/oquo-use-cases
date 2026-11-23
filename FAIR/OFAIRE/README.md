# O'FAIRe use case

Assessment of the FAIRness of the OQUO core with [O'FAIRe](https://github.com/agroportal/fairness), and representation of its results as OQUO-compliant RDF, according to the [FAIR quality model](../README.md#the-fair-quality-model).

O'FAIRe (Ontology FAIRness Evaluator) assesses the ontologies stored in an [OntoPortal](https://ontoportal.org/) repository. It answers a set of questions about each ontology, mainly about its metadata, each one associated with a FAIR principle, and gives a number of credits to each answer. The [`oquo-ofaire`](oquo_module/oquo-ofaire.owl) module (`https://purl.org/oquo-ofaire`) defines:

- one metric per question of O'FAIRe, associated with the characteristic of the FAIR quality model it measures;
- the raw scale of each metric, an ordinal scale whose categories are the numbers of credits that O'FAIRe can give to the question, and its conversion to the percentage scale of the FAIR quality model;
- the software agent of O'FAIRe (`oquo-ofaire:ofaire-software-agent`), to which the results are attributed.

O'FAIRe does not report issues, so the module defines no issue types.

## Contents

| File or folder | Content |
|---|---|
| `ontoportal_data/` | Descriptions of the ontologies loaded in OntoPortal to be assessed, one JSON file per ontology. `OQUO-CORE.json` describes the OQUO core, downloaded from its version IRI (`https://purl.org/oquo-core/v2.2.2`). |
| `evaluate.sh` | Script that assesses the OQUO core and converts the results into OQUO-compliant RDF. |
| `source_results/` | Results of O'FAIRe for the OQUO core, as returned by the service (`ofaire_results.json`), and the versions of the tools used to obtain them (`environment.txt`). |
| `oquo_module/` | The `oquo-ofaire` module, with an OWL catalog (`catalog-v001.xml`) to resolve its imports in Protégé. |
| `oquo_compliant_results/` | The results as OQUO-compliant RDF, with the `oquo-ofaire` module and the converted values (`oquo_model.ttl`). |

## Reproducing the results

The evaluated ontology is version 2.2.2 of the OQUO core (`https://purl.org/oquo-core/v2.2.2`).

First, start the services (see the [main README](../../README.md#running-the-services)):

```bash
cd services
docker compose up -d --build --wait
```

The first start loads and processes in OntoPortal the ontologies described in `ontoportal_data/`, which can take several minutes. `--wait` returns once they are loaded.

Then, from this folder, assess the ontology with O'FAIRe. The ontology is identified by its acronym in OntoPortal, which is the name of its JSON file in `ontoportal_data/`:

```bash
curl -s "http://localhost:9393/ofaire?ontologies=OQUO-CORE&sync" -o source_results/ofaire_results.json
```

Finally, convert the results into OQUO-compliant RDF:

```bash
curl -X POST http://localhost:8001/ofaireToOquoModel \
     -H "Content-Type: application/json" \
     -d @source_results/ofaire_results.json \
     -o oquo_compliant_results/oquo_model.ttl
```

Both steps are run by `evaluate.sh`, which also records in `source_results/environment.txt` the versions used: the ontology and the checksum of its content, the commits of ontoportal_docker and O'FAIRe, and the digests of the Docker images.

```bash
./evaluate.sh
```

The commands use the default ports of the services; if you changed them in `services/.env` or `services/ontoportal/ontoportal.env`, change them here too.

`oquo_model.ttl` contains, besides the results of O'FAIRe:

- the `oquo-ofaire` module and the ontologies it imports (the FAIR quality model and the OQUO core), so that it can be queried without loading any other ontology;
- the results converted to the percentage scale of the FAIR quality model, linked to the original values with `prov:wasDerivedFrom`.

To obtain only the results of O'FAIRe, without the module or the converted values, use `/ofaireToOquo` instead of `/ofaireToOquoModel`. The IRI of the assessed ontology is taken from the results of O'FAIRe; if it is missing, give it in the `ontologyIRI` parameter of the converter.

## Assessing another version or another ontology

OntoPortal loads each ontology only the first time it starts. To assess another version of the OQUO core, change `pullLocation` and `version` in `ontoportal_data/OQUO-CORE.json`, and to assess another ontology, add its JSON file to `ontoportal_data/`. Then remove the data of OntoPortal, so that the ontologies are loaded again, and start the services:

```bash
cd services
docker compose down --volumes
docker compose up -d --build --wait
```

See [`services/ontoportal`](../../services/ontoportal/README.md) for the format of the JSON files.
