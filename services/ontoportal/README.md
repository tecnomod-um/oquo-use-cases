# OntoPortal with O'FAIRe

A local [OntoPortal](https://ontoportal.org/) appliance with [O'FAIRe](https://github.com/agroportal/fairness), used to assess the FAIRness of ontologies in a reproducible way. It is based on [ontoportal_docker](https://github.com/ontoportal-lirmm/ontoportal_docker), whose files are copied, unmodified, into [`ontoportal_docker/`](ontoportal_docker/) (see [Versions](#versions)), and it is part of the services started by [`services/docker-compose.yml`](../docker-compose.yml).

## Requirements

- Docker with Docker Compose 2.24 or later (`include` and `!override` are used).
- At least 8 GB of RAM available for Docker. Some images (Virtuoso, mgrep) are only published for `amd64`, so on ARM machines (e.g. Apple silicon) they run under emulation and more slowly.

## Usage

```bash
cd services
docker compose up -d --build --wait
```

The first time, this builds O'FAIRe, loads and processes the ontologies, and only returns once they are loaded, which can take several minutes. The ontologies stay loaded afterwards, in the volumes of the appliance, and later starts only load the ontologies that have been added since.

O'FAIRe is then available at:

```
http://localhost:9393/ofaire?ontologies=<ACRONYM>&sync
```

Only the API and O'FAIRe are started. To start the web UI too (at `http://localhost:8080`), add `--profile ui`.

To remove all the data of the appliance and load the ontologies from scratch:

```bash
docker compose down --volumes
```

## Ontologies

The appliance loads every ontology described in the directory given in `ONTOPORTAL_DATA_DIR` (`ontoportal.env`), by default [`FAIR/OFAIRE/ontoportal_data/`](../../FAIR/OFAIRE/ontoportal_data/). Each ontology is described by an `<ACRONYM>.json` file with its metadata and the metadata of its submission (see [`data/ontologies/STY.json`](https://github.com/ontoportal-lirmm/ontoportal_docker/blob/da4f2a6c9ee3be691d279d34f20088f660775bc8/data/ontologies/STY.json) in ontoportal_docker for the format), and is obtained from:

- `"submission"."pullLocation"`: a URL, such as the version IRI of the ontology, from which it is downloaded on every start. The pullLocation is also stored as metadata of the submission, as in any ontology submitted by URL to an OntoPortal repository.
- `"file"`: a file in the same directory, if no URL is available.

To add an ontology, add its JSON file to the directory and start the services again. To change an ontology that is already loaded (e.g. to assess another version, changing `pullLocation` and `version` in its JSON), remove the data of the appliance first, so that all the ontologies are loaded again:

```bash
docker compose down --volumes
docker compose up -d --build --wait
```

OntoPortal cannot load a new submission of an ontology that already exists with the loading script of the appliance (`bin/ncbo_ontology_load`).

## Files

| File | Content |
|---|---|
| `ontoportal.env` | Configuration of the appliance: the [`.env.sample`](https://github.com/ontoportal-lirmm/ontoportal_docker/blob/da4f2a6c9ee3be691d279d34f20088f660775bc8/.env.sample) of ontoportal_docker with the changes listed at its top (ports, O'FAIRe without cache, data directory and O'FAIRe commit). |
| `compose.override.yml` | Changes to the appliance of ontoportal_docker, applied on top of its `docker-compose.yml`. |
| `provision.sh` | Loads the ontologies; run by the `ncbo_cron` container before the cron. |
| `fairness.Dockerfile` | Builds O'FAIRe at the commit given in `FAIRNESS_COMMIT` (the upstream Dockerfile only accepts branches and tags), and makes its Tomcat respond in UTF-8. |
| `ontoportal_docker/` | Files of ontoportal_docker used by `compose.override.yml` (its `docker-compose.yml` and the configuration of `ncbo_cron`, `fairness` and `nginx`), copied unmodified. Its origin is recorded in `ontoportal_docker/UPSTREAM.md`. |

All the changes to the appliance are made in the files above; the files in `ontoportal_docker/` are not modified.

## Versions

- **ontoportal_docker:** files copied from [ontoportal_docker](https://github.com/ontoportal-lirmm/ontoportal_docker) at commit [`da4f2a6`](https://github.com/ontoportal-lirmm/ontoportal_docker/tree/da4f2a6c9ee3be691d279d34f20088f660775bc8) (2026-11-05), recorded in `ontoportal_docker/UPSTREAM.md`.
- **O'FAIRe:** `FAIRNESS_COMMIT` in `ontoportal.env`.
- **OntoPortal images:** `API_TAG` and `NCBO_CRON_TAG` in `ontoportal.env`. They default to `master`, which changes over time. The use cases record the digest of every image used in each run (e.g. `FAIR/OFAIRE/source_results/environment.txt`), which can be pinned as `API_TAG=master@sha256:<digest>`.