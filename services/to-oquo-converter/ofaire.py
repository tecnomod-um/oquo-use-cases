"""Conversion of the results of O'FAIRe (https://github.com/agroportal/fairness) to OQUO, with the module oquo-ofaire."""
from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException, Query, Response

from oquo_client import create_oquo_rdf

router = APIRouter()

OQUO_OFAIRE_NS = "https://purl.org/oquo-ofaire#"
OFAIRE_AGENT_IRI = OQUO_OFAIRE_NS + "ofaire-software-agent"
FAIR_CATEGORIES = ("Findable", "Accessible", "Interoperable", "Reusable")
OQUO_OFAIRE_IRI = 'https://purl.org/oquo-ofaire'


def ofaire_question_to_oquo_metric(question_id):
    """IRI of the metric of oquo-ofaire for an O'FAIRe question, e.g. A1.1Q1 -> ...#A1_1Q1Metric."""
    return OQUO_OFAIRE_NS + question_id.replace(".", "_") + "Metric"


def get_ontology_iri(assessment):
    """IRI of the assessed ontology, as reported by O'FAIRe in question F1Q1, or None if absent."""
    f1q1 = assessment.get("Findable", {}).get("F1", {}).get("results", {}).get("F1Q1", {})
    iri = f1q1.get("properties", {}).get("owl:ontologyIRI")
    return iri if iri else None


def iterate_questions(assessment):
    """Yields (question id, question result) for every question of an O'FAIRe assessment."""
    for category in FAIR_CATEGORIES:
        for principle in assessment.get(category, {}).values():
            if isinstance(principle, dict) and "results" in principle:
                yield from principle["results"].items()


def generate_oquo_observation(ontology_iri, question_id, question, timestamp):
    score = question.get("score")
    if score is None:
        return None

    oquo_metric_iri = ofaire_question_to_oquo_metric(question_id)

    oquo_observation = {}
    oquo_observation['sourceDocumentIRI'] = ontology_iri
    oquo_observation['featureOfInterestIRI'] = ontology_iri
    oquo_observation['featureOfInterestTypeIRI'] = 'http://www.w3.org/2002/07/owl#Ontology'
    oquo_observation['metricUsedIRI'] = oquo_metric_iri
    oquo_observation['scaleIRI'] = oquo_metric_iri + 'Scale'
    oquo_observation['scaleTypeIRI'] = 'https://purl.org/oquo#RawScale'
    oquo_observation['rankingFunctionIRI'] = 'http://purl.org/net/QualityModel#HigherBest'
    # The raw scales of oquo-ofaire are ordinal: one category per number of credits, ranked
    # (om:rank) by that number. The credits identify the category of the value.
    oquo_observation['value'] = int(score)
    oquo_observation['timestamp'] = timestamp
    oquo_observation['agentIRI'] = OFAIRE_AGENT_IRI
    oquo_observation['agentTypeIRI'] = 'http://www.w3.org/ns/prov#SoftwareAgent'

    explanation = question.get('explanation')
    if explanation:
        oquo_observation['details'] = [explanation]

    return oquo_observation


def execute_convert_ofaire_to_oquo(ofaire_data: dict, ontology_iri: str = None, model_iri: str = None):
    ontologies = ofaire_data.get('ontologies')
    if not ontologies:
        raise HTTPException(status_code=400, detail="The O'FAIRe results contain no ontologies")

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    oquo_observations = []
    for acronym, assessment in ontologies.items():
        iri = ontology_iri or get_ontology_iri(assessment)
        if iri is None:
            raise HTTPException(status_code=400,
                                detail=f"The IRI of the ontology {acronym} is not in the O'FAIRe results; "
                                       "give it in the parameter ontologyIRI")
        for question_id, question in iterate_questions(assessment):
            oquo_observation = generate_oquo_observation(iri, question_id, question, timestamp)
            if oquo_observation is not None:
                oquo_observations.append(oquo_observation)
    return create_oquo_rdf(oquo_observations, model_iri)


@router.post("/ofaireToOquo")
def convert_ofaire_to_oquo(ofaire_results: dict = Body(...),
                           ontologyIRI: str = Query(None, description="IRI of the assessed ontology. "
                                                    "By default, the one reported by O'FAIRe (F1Q1).")):
    turtle = execute_convert_ofaire_to_oquo(ofaire_results, ontologyIRI)
    return Response(content=turtle, media_type="text/turtle")


@router.post("/ofaireToOquoModel")
def convert_ofaire_to_oquo_model(ofaire_results: dict = Body(...),
                                 ontologyIRI: str = Query(None, description="IRI of the assessed ontology. "
                                                          "By default, the one reported by O'FAIRe (F1Q1)."),
                                 modelIRI: str = Query(OQUO_OFAIRE_IRI,
                                                       description="IRI of the OQUO module that describes the "
                                                                   "O'FAIRe metrics. By default, oquo-ofaire.")):
    turtle = execute_convert_ofaire_to_oquo(ofaire_results, ontologyIRI, modelIRI)
    return Response(content=turtle, media_type="text/turtle")
