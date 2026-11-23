# FOOPS! use case

Assessment of the FAIRness of the OQUO core with [FOOPS!](https://w3id.org/foops/) 0.4.0, and representation of its results as OQUO-compliant RDF, according to the [FAIR quality model](../README.md#the-fair-quality-model).

FOOPS! runs a set of checks on an ontology and its metadata, each one associated with a FAIR principle, and reports the proportion of tests passed by each check. The [`oquo-foops`](oquo_module/oquo-foops.owl) module (`https://purl.org/oquo-foops`) defines:

- one metric per check of FOOPS!, associated with the characteristic of the FAIR quality model it measures;
- the raw scale of each metric (the proportion of tests passed, from 0 to 1), and its conversion to the percentage scale of the FAIR quality model;
- one issue type per check, for the checks that fail;
- the software agent of FOOPS! (`oquo-foops:foops-software-agent`), to which the results are attributed.

## Contents

| File or folder | Content |
|---|---|
| `evaluate.sh` | Script that assesses the OQUO core and converts the results into OQUO-compliant RDF. |
| `source_results/` | Results of FOOPS! for the OQUO core, as returned by the service (`foops_results.json`), and the versions used to obtain them (`environment.txt`). |
| `oquo_module/` | The `oquo-foops` module. |
| `oquo_compliant_results/` | The results as OQUO-compliant RDF (`oquo_model.ttl`). |

## Reproducing the results

The evaluated ontology is version 2.2.2 of the OQUO core (`https://purl.org/oquo-core/v2.2.2`).

1. Start the services (see the [main README](../../README.md#running-the-services)):

   ```bash
   cd services
   docker compose up -d --build --wait
   ```

2. From this folder, assess the ontology with FOOPS!:

   ```bash
   curl -X POST http://localhost:8002/assessOntology \
        -H "Content-Type: application/json;charset=UTF-8" \
        -d '{"ontologyUri": "https://purl.org/oquo-core/v2.2.2"}' \
        -o source_results/foops_results.json
   ```

   The assessment may take some time, since FOOPS! retrieves the ontology and queries external registries.

3. Convert the results into OQUO-compliant RDF:

   ```bash
   curl -X POST http://localhost:8001/foopsToOquoModel \
        -H "Content-Type: application/json" \
        -d @source_results/foops_results.json \
        -o oquo_compliant_results/oquo_model.ttl
   ```

The commands use the default ports of the services; if you changed them in `services/.env`, change them here too.

Both steps are run by `evaluate.sh`, which reads the ports from `services/.env` and also records in `source_results/environment.txt` the versions used: the ontology and the checksum of its content, and the digests of the Docker images.

```bash
./evaluate.sh
```

It assesses the OQUO core 2.2.2 by default; to assess another ontology, give its IRI: `./evaluate.sh https://w3id.org/okn/o/sd`.

`oquo_model.ttl` contains, besides the results of FOOPS!:

- the `oquo-foops` module and the ontologies it imports (the FAIR quality model and the OQUO core), so that it can be queried without loading any other ontology;
- the results converted to the percentage scale of the FAIR quality model, linked to the original values with `prov:wasDerivedFrom`.

To obtain only the results of FOOPS!, without the module or the converted values, use `/foopsToOquo` instead of `/foopsToOquoModel`.

Some checks of FOOPS! depend on external services, such as the resolution of the ontology IRI or its presence in metadata registries, so a new assessment may give different results from the ones in this folder if those services change.