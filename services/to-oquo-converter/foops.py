"""Conversion of the results of FOOPS! (https://w3id.org/foops/) to OQUO, with the module oquo-foops."""
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Query, Response

from oquo_client import create_oquo_rdf

router = APIRouter()
OQUO_FOOPS_IRI = 'https://purl.org/oquo-foops'
FOOPS_TEST_TO_OQUO_METRIC = {
    "https://w3id.org/foops/test/CN1":        "https://purl.org/oquo-foops#ContentNegotiationMetric",
    "https://w3id.org/foops/test/DOC1":       "https://purl.org/oquo-foops#HTMLDocumentationMetric",
    "https://w3id.org/foops/test/FIND1":      "https://purl.org/oquo-foops#OntologyPrefixDeclaredMetric",
    "https://w3id.org/foops/test/FIND2":      "https://purl.org/oquo-foops#PrefixInCommunityRegistryMetric",
    "https://w3id.org/foops/test/FIND3":      "https://purl.org/oquo-foops#OntologyInMetadataRegistryMetric",
    "https://w3id.org/foops/test/FIND_3_BIS": "https://purl.org/oquo-foops#MetadataAccessibleWithoutOntologyMetric",
    "https://w3id.org/foops/test/HTTP1":      "https://purl.org/oquo-foops#OpenProtocolMetric",
    "https://w3id.org/foops/test/OM1":        "https://purl.org/oquo-foops#MinimumMetadataMetric",
    "https://w3id.org/foops/test/OM2":        "https://purl.org/oquo-foops#RecommendedMetadataMetric",
    "https://w3id.org/foops/test/OM3":        "https://purl.org/oquo-foops#DetailedMetadataMetric",
    "https://w3id.org/foops/test/OM4.1":      "https://purl.org/oquo-foops#LicenseAvailableMetric",
    "https://w3id.org/foops/test/OM4.2":      "https://purl.org/oquo-foops#LicenseResolvableMetric",
    "https://w3id.org/foops/test/OM5.1":      "https://purl.org/oquo-foops#BasicProvenanceMetadataMetric",
    "https://w3id.org/foops/test/OM5.2":      "https://purl.org/oquo-foops#DetailedProvenanceMetadataMetric",
    "https://w3id.org/foops/test/PURL1":      "https://purl.org/oquo-foops#PersistentURLMetric",
    "https://w3id.org/foops/test/RDF1":       "https://purl.org/oquo-foops#RDFAvailabilityMetric",
    "https://w3id.org/foops/test/URI1":       "https://purl.org/oquo-foops#OntologyURIResolvableMetric",
    "https://w3id.org/foops/test/URI2":       "https://purl.org/oquo-foops#ConsistentOntologyIDMetric",
    "https://w3id.org/foops/test/VER1":       "https://purl.org/oquo-foops#VersionIRIDeclaredMetric",
    "https://w3id.org/foops/test/VER2":       "https://purl.org/oquo-foops#VersionIRIResolvableMetric",
    "https://w3id.org/foops/test/VOC1":       "https://purl.org/oquo-foops#MetadataVocabularyReuseMetric",
    "https://w3id.org/foops/test/VOC2":       "https://purl.org/oquo-foops#VocabularyReuseMetric",
    "https://w3id.org/foops/test/VOC3":       "https://purl.org/oquo-foops#TermLabelsMetric",
    "https://w3id.org/foops/test/VOC4":       "https://purl.org/oquo-foops#TermDefinitionsMetric",
}

FOOPS_TEST_TO_OQUO_ISSUE = {
    "https://w3id.org/foops/test/CN1":        "https://purl.org/oquo-foops#ContentNegotiationNotSupportedIssue",
    "https://w3id.org/foops/test/DOC1":       "https://purl.org/oquo-foops#NoHTMLDocumentationIssue",
    "https://w3id.org/foops/test/FIND1":      "https://purl.org/oquo-foops#PrefixNotDeclaredIssue",
    "https://w3id.org/foops/test/FIND2":      "https://purl.org/oquo-foops#PrefixNotInCommunityRegistryIssue",
    "https://w3id.org/foops/test/FIND3":      "https://purl.org/oquo-foops#OntologyNotInMetadataRegistryIssue",
    "https://w3id.org/foops/test/FIND_3_BIS": "https://purl.org/oquo-foops#MetadataNotAccessibleWithoutOntologyIssue",
    "https://w3id.org/foops/test/HTTP1":      "https://purl.org/oquo-foops#NoOpenProtocolIssue",
    "https://w3id.org/foops/test/OM1":        "https://purl.org/oquo-foops#MissingMinimumMetadataIssue",
    "https://w3id.org/foops/test/OM2":        "https://purl.org/oquo-foops#MissingRecommendedMetadataIssue",
    "https://w3id.org/foops/test/OM3":        "https://purl.org/oquo-foops#MissingDetailedMetadataIssue",
    "https://w3id.org/foops/test/OM4.1":      "https://purl.org/oquo-foops#NoLicenseIssue",
    "https://w3id.org/foops/test/OM4.2":      "https://purl.org/oquo-foops#LicenseNotResolvableIssue",
    "https://w3id.org/foops/test/OM5.1":      "https://purl.org/oquo-foops#MissingBasicProvenanceMetadataIssue",
    "https://w3id.org/foops/test/OM5.2":      "https://purl.org/oquo-foops#MissingDetailedProvenanceMetadataIssue",
    "https://w3id.org/foops/test/PURL1":      "https://purl.org/oquo-foops#NonPersistentURIIssue",
    "https://w3id.org/foops/test/RDF1":       "https://purl.org/oquo-foops#NoRDFSerialisationIssue",
    "https://w3id.org/foops/test/URI1":       "https://purl.org/oquo-foops#OntologyURINotResolvableIssue",
    "https://w3id.org/foops/test/URI2":       "https://purl.org/oquo-foops#InconsistentOntologyIDIssue",
    "https://w3id.org/foops/test/VER1":       "https://purl.org/oquo-foops#MissingDistinctVersionIRIIssue",
    "https://w3id.org/foops/test/VER2":       "https://purl.org/oquo-foops#VersionIRINotResolvableIssue",
    "https://w3id.org/foops/test/VOC1":       "https://purl.org/oquo-foops#NoMetadataVocabularyReuseIssue",
    "https://w3id.org/foops/test/VOC2":       "https://purl.org/oquo-foops#NoVocabularyReuseIssue",
    "https://w3id.org/foops/test/VOC3":       "https://purl.org/oquo-foops#TermWithNoLabelIssue",
    "https://w3id.org/foops/test/VOC4":       "https://purl.org/oquo-foops#TermWithNoDefinitionIssue",
}


def generate_oquo_observation(feature_of_interest_iri, check):
    check_id = check['id']
    check_status = check['status']
    explanation = check['explanation']
    passed_tests = check['total_passed_tests']
    total_tests = check['total_tests_run']
    check_score = passed_tests / total_tests


    oquo_metric_iri = FOOPS_TEST_TO_OQUO_METRIC.get(check_id)
    if oquo_metric_iri is None:
        raise KeyError(f"FOOPS! check not modelled in oquo-foops: {check_id}")

    oquo_observation = {}
    oquo_observation['sourceDocumentIRI'] = feature_of_interest_iri
    oquo_observation['featureOfInterestIRI'] = feature_of_interest_iri
    oquo_observation['featureOfInterestTypeIRI'] = 'http://www.w3.org/2002/07/owl#Ontology'
    oquo_observation['metricUsedIRI'] = oquo_metric_iri
    oquo_observation['scaleIRI'] = oquo_metric_iri + 'Scale'
    oquo_observation['scaleTypeIRI'] = 'https://purl.org/oquo#RawScale'
    oquo_observation['rankingFunctionIRI'] = 'http://purl.org/net/QualityModel#HigherBest'
    oquo_observation['value'] = check_score
    oquo_observation['timestamp'] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    oquo_observation['agentIRI'] = 'https://purl.org/oquo-foops#foops-software-agent'
    oquo_observation['agentTypeIRI'] = 'http://www.w3.org/ns/prov#SoftwareAgent'

    if 'error' == check_status:
        issue = {
            'issueType': FOOPS_TEST_TO_OQUO_ISSUE.get(check_id),
            'message': explanation,
            'hostAsset': feature_of_interest_iri
        }
        oquo_observation['issues'] = [issue]

    return oquo_observation


def execute_convert_foops_to_oquo(foops_data: dict, model_iri: str = None):
    ontology_iri = foops_data['ontology_URI']
    oquo_observations = []
    for check in foops_data['checks']:
        oquo_observation = generate_oquo_observation(ontology_iri, check)
        oquo_observations.append(oquo_observation)
    return create_oquo_rdf(oquo_observations, model_iri)


@router.post("/foopsToOquo")
def convert_foops_to_oquo(foops_results: dict = Body(...)):
    turtle = execute_convert_foops_to_oquo(foops_results)
    return Response(content=turtle, media_type="text/turtle")


@router.post("/foopsToOquoModel")
def convert_foops_to_oquo_model(foops_results: dict = Body(...),
                                modelIRI: str = Query(OQUO_FOOPS_IRI,
                                                      description="IRI of the OQUO module that describes the "
                                                                  "FOOPS! metrics. By default, oquo-foops.")):
    turtle = execute_convert_foops_to_oquo(foops_results, modelIRI)
    return Response(content=turtle, media_type="text/turtle")
