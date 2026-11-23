#!/usr/bin/env bash
# Assesses the FAIRness of an ontology with FOOPS! and converts the results into
# OQUO-compliant RDF.
#
# Usage: ./evaluate.sh [ontology IRI]
#   By default, the ontology assessed is version 2.2.2 of the OQUO core.
#
# Requires the services to be running:
#   cd services && docker compose up -d --build --wait
#
# Outputs:
#   source_results/foops_results.json        FOOPS! results, as returned by the service
#   source_results/environment.txt           versions used (ontology, FOOPS! image)
#   oquo_compliant_results/oquo_model.ttl    results as OQUO-compliant RDF, with the
#                                            oquo-foops module and the converted values
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SERVICES="$ROOT/services"

ONTOLOGY_IRI="${1:-https://purl.org/oquo-core/v2.2.2}"
SOURCE_RESULTS="$HERE/source_results"
OQUO_RESULTS="$HERE/oquo_compliant_results"

# Ports published by the services (services/.env), with their default values
env_value() {
  grep -E "^$1=" "$SERVICES/.env" 2>/dev/null | cut -d= -f2 || true
}
FOOPS_PORT="$(env_value FOOPS_PORT)"; FOOPS_PORT="${FOOPS_PORT:-8002}"
CONVERTER_PORT="$(env_value TO_OQUO_CONVERTER_PORT)"; CONVERTER_PORT="${CONVERTER_PORT:-8001}"

mkdir -p "$SOURCE_RESULTS" "$OQUO_RESULTS"

echo "[+] Assessing $ONTOLOGY_IRI with FOOPS! (this may take some time)"
curl -fsS -X POST "http://localhost:$FOOPS_PORT/assessOntology" \
     -H "Content-Type: application/json;charset=UTF-8" \
     -d "{\"ontologyUri\": \"$ONTOLOGY_IRI\"}" \
     -o "$SOURCE_RESULTS/foops_results.json"
echo "[+] Results saved in $SOURCE_RESULTS/foops_results.json"

echo "[+] Converting the results into OQUO-compliant RDF"
curl -fsS -X POST "http://localhost:$CONVERTER_PORT/foopsToOquoModel" \
     -H "Content-Type: application/json" \
     -d @"$SOURCE_RESULTS/foops_results.json" \
     -o "$OQUO_RESULTS/oquo_model.ttl"
echo "[+] OQUO-compliant results saved in $OQUO_RESULTS/oquo_model.ttl"

# Ontology assessed and the checksum of its content, as served when assessed
ontology_sha256="$(curl -fsSL -H "Accept: application/rdf+xml, text/turtle;q=0.9, */*;q=0.5" "$ONTOLOGY_IRI" \
                   | sha256sum | cut -d' ' -f1)"
{
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ontology: $ONTOLOGY_IRI"
  echo "ontology sha256: $ontology_sha256"
  echo "images:"
  (cd "$SERVICES" && docker compose config --images) | sort -u | while read -r image; do
    digest="$(docker image inspect --format '{{range .RepoDigests}}{{.}} {{end}}' "$image" 2>/dev/null | awk '{print $1}')"
    echo "  $image -> ${digest:-built locally}"
  done
} >"$SOURCE_RESULTS/environment.txt"
echo "[+] Versions saved in $SOURCE_RESULTS/environment.txt"
