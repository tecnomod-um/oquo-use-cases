#!/usr/bin/env bash
# Provisioning of the OntoPortal appliance, run by the ncbo_cron container
# before the cron itself (see compose.override.yml).
#
# 1. Creates the admin user, the first time.
# 2. Loads and processes every ontology described in ONTOPORTAL_DATA_DIR
#    (mounted at /srv/ontoportal/data/ontologies-src): one <ACRONYM>.json per
#    ontology, with the metadata of the ontology and its submission. The
#    ontology is obtained from:
#      - "file": a file of the same directory, or
#      - "submission"."pullLocation": a URL (e.g. the version IRI of the
#        ontology), downloaded on every start.
#    An ontology is loaded again, as a new submission, only when its JSON or
#    its content have changed since it was last loaded.
# 3. Marks the provisioning as done (the healthcheck of ncbo_cron), and runs
#    the command it receives (the cron).
#
# bin/ncbo_ontology_load reads the ontologies from /srv/ontoportal/data/ontologies,
# a volume where this script writes the JSON and the ontology file of each one.
# The state is kept in the repository volume, so it survives restarts and is
# removed with 'docker compose down --volumes'.
set -euo pipefail

SOURCE_DIR=/srv/ontoportal/data/ontologies-src
ONTOLOGIES_DIR=/srv/ontoportal/data/ontologies
STATE_DIR=/srv/ontoportal/data/repository/.oquo-provisioning
mkdir -p "$STATE_DIR" "$ONTOLOGIES_DIR"
rm -f "$STATE_DIR/ready"

if [ ! -f "$STATE_DIR/admin" ]; then
  echo "[provision] Creating the admin user"
  bundle exec rake "user:create[admin,admin@nodomain.org,password]"
  bundle exec rake "user:adminify[admin]"
  touch "$STATE_DIR/admin"
fi

# Copies <ACRONYM>.json and its ontology into ONTOLOGIES_DIR, downloading the
# ontology from its pullLocation when the JSON names no file.
prepare() {
  ruby -rjson -ropen-uri -rfileutils -e '
    source_json, target_dir = ARGV
    acronym = File.basename(source_json, ".json")
    metadata = JSON.parse(File.read(source_json))
    url = metadata.dig("submission", "pullLocation")
    if metadata["file"]
      FileUtils.cp(File.join(File.dirname(source_json), metadata["file"]), target_dir)
    elsif url
      extension = { "OWL" => ".owl", "OBO" => ".obo", "SKOS" => ".rdf", "UMLS" => ".ttl" }.fetch(metadata["hasOntologyLanguage"], "")
      metadata["file"] = "#{acronym}#{extension}"
      URI.open(url, "Accept" => "application/rdf+xml, text/turtle;q=0.9, */*;q=0.5") do |remote|
        File.binwrite(File.join(target_dir, metadata["file"]), remote.read)
      end
    else
      abort "#{source_json}: neither \"file\" nor \"submission\".\"pullLocation\" is given"
    end
    File.write(File.join(target_dir, "#{acronym}.json"), JSON.pretty_generate(metadata))
    print metadata["file"]
  ' "$1" "$ONTOLOGIES_DIR"
}

shopt -s nullglob
for source_json in "$SOURCE_DIR"/*.json; do
  acronym="$(basename "$source_json" .json)"
  echo "[provision] Preparing $acronym"
  file="$(prepare "$source_json")"
  checksum="$(cat "$ONTOLOGIES_DIR/$acronym.json" "$ONTOLOGIES_DIR/$file" | sha256sum | cut -d' ' -f1)"

  if [ "$(cat "$STATE_DIR/$acronym" 2>/dev/null || true)" = "$checksum" ]; then
    echo "[provision] $acronym is already loaded and up to date"
    continue
  fi

  echo "[provision] Loading $acronym"
  bundle exec bin/ncbo_ontology_load --admin-user admin "$acronym"
  echo "[provision] Processing $acronym"
  bundle exec bin/ncbo_ontology_process -o "$acronym"
  echo "$checksum" >"$STATE_DIR/$acronym"
done

touch "$STATE_DIR/ready"
echo "[provision] Done"
exec "$@"
