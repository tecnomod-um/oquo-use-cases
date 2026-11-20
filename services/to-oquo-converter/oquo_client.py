"""Client of oquo-instance-creator-endpoint, shared by the converters."""
import os

import requests

OQUO_INSTANCE_CREATOR_ENDPOINT = os.getenv("OQUO_INSTANCE_CREATOR_URL")
TO_OQUO_OBSERVATION = OQUO_INSTANCE_CREATOR_ENDPOINT + 'toOquoObservation'
TO_OQUO_MODEL = OQUO_INSTANCE_CREATOR_ENDPOINT + 'toOquoModel'

def create_oquo_rdf(oquo_observations: list, ontology_iri: str = None) -> str:
    """Sends the observations to oquo-instance-creator-endpoint and returns the RDF (Turtle) it generates.
    With ontology_iri, the OQUO module is added and its scale conversions are applied (/toOquoModel)."""
    if ontology_iri is None:
        response = requests.post(TO_OQUO_OBSERVATION, json={"observationsInfoDTO": oquo_observations})
    else:
        response = requests.post(TO_OQUO_MODEL, params={"ontologyIRI": ontology_iri},
                                 json={"observationsInfoDTO": oquo_observations})
    response.raise_for_status()
    return response.text
