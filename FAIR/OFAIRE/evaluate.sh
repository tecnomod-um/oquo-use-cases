#!/usr/bin/env bash
# Assesses the FAIRness of the OQUO core with O'FAIRe.
#
# Requires the services to be running, with the OQUO core loaded in OntoPortal:
#   cd services && docker compose up -d --wait
#
# Outputs:
#   source_results/ofaire_results.json       O'FAIRe results, as returned by the service
#   source_results/environment.txt          versions used (ontology, appliance, O'FAIRe, images)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SERVICES="$ROOT/services"
ONTOPORTAL="$SERVICES/ontoportal"

ACRONYM="OQUO-CORE"
DATA="$HERE/ontoportal_data"
RESULTS="$HERE/source_results"
API_PORT="$(grep -E '^NGINX_API_PORT=' "$ONTOPORTAL/ontoportal.env" | cut -d= -f2)"

mkdir -p "$RESULTS"

echo "[+] Assessing $ACRONYM with O'FAIRe"
curl -fsS "http://localhost:$API_PORT/ofaire?ontologies=$ACRONYM&sync" \
  | python3 -m json.tool >"$RESULTS/ofaire_results.json"
echo "[+] Results saved in $RESULTS/ofaire_results.json"

# Ontology assessed: its pullLocation (or local file) and the checksum of its content
read -r ontology_source ontology_sha256 < <(python3 - "$DATA/$ACRONYM.json" <<'PY'
import hashlib, json, os, sys, urllib.request
path = sys.argv[1]
metadata = json.load(open(path))
if metadata.get("file"):
    source = os.path.join(os.path.dirname(path), metadata["file"])
    content = open(source, "rb").read()
else:
    source = metadata["submission"]["pullLocation"]
    request = urllib.request.Request(source, headers={"Accept": "application/rdf+xml, text/turtle;q=0.9, */*;q=0.5"})
    content = urllib.request.urlopen(request).read()
print(source, hashlib.sha256(content).hexdigest())
PY
)
{
  echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ontology: $ontology_source"
  echo "ontology sha256: $ontology_sha256"
  echo "ontoportal_docker commit: $(git -C "$ONTOPORTAL/ontoportal_docker" rev-parse HEAD)"
  echo "O'FAIRe commit: $(grep -E '^FAIRNESS_COMMIT=' "$ONTOPORTAL/ontoportal.env" | cut -d= -f2)"
  echo "images:"
  (cd "$SERVICES" && docker compose config --images) | sort -u | while read -r image; do
    digest="$(docker image inspect --format '{{index .RepoDigests 0}}' "$image" 2>/dev/null || echo "built locally")"
    echo "  $image -> $digest"
  done
} >"$RESULTS/environment.txt"
echo "[+] Versions saved in $RESULTS/environment.txt"

# convert the results into OQUO-compliant RDF
curl -fsS -X POST http://localhost:8001/ofaireToOquoModel -H "Content-Type: application/json" \
    -d @"$RESULTS/ofaire_results.json" -o "$HERE/oquo_compliant_results/oquo_model.ttl"
