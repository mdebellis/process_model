"""Run positive and negative regression cases without modifying any file.

Requires rdflib. Run alongside the updated process_model_with_examples.rdf,
or pass its path as the first argument. No network or LLM calls are made.
"""
import json
import sys
from pathlib import Path
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.plugins.sparql.parser import parseQuery
from query_examples import ask_tender_state

ROOT = Path(__file__).resolve().parent
PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'process_model_with_examples.rdf'
BASE = Graph().parse(PATH, format='xml')
PM = Namespace('https://www.in2use.com/process_model/')
FIG = Namespace('https://www.michaeldebellis.com/supply_chain_figure8/')
SC = Namespace('https://www.michaeldebellis.com/supply_chain_model/')
PROV = Namespace('http://www.w3.org/ns/prov#')
SULO = Namespace('https://w3id.org/sulo/')
RESULTS = []


def clone():
    graph = Graph()
    for triple in BASE: graph.add(triple)
    return graph


def case(name, test, expected, graph=BASE, run=FIG.TenderRun01, version=FIG.Run01RevisedTender):
    actual = ask_tender_state(graph, PM[test], run=run, version=version)
    RESULTS.append({'case': name, 'expected': expected, 'actual': actual, 'passed': actual == expected})
    assert actual == expected, name


for test, query in BASE.subject_objects(PM.has_sparql_query):
    parseQuery(str(query))
    RESULTS.append({'case': 'Parse ' + str(test).rsplit('/',1)[-1], 'passed': True})

for name in ['Tender_Approval_Test', 'Tender_Submission_Test', 'Approved_Tender_Submission_Test']:
    case('Existing run: ' + name, name, True)
    case('Different version: ' + name, name, False, version=FIG.Run01InitialDraft)
    case('Different run: ' + name, name, False, run=URIRef('urn:regression:Another_Run'))

graph = clone()
graph.remove((FIG.Run01Decision, SC.hasOutcome, SC.Approved))
case('Missing approval evidence', 'Tender_Approval_Test', False, graph)
case('Parent with missing approval evidence', 'Approved_Tender_Submission_Test', False, graph)
case('Submission independently of approval', 'Tender_Submission_Test', True, graph)

graph.add((FIG.Run01Decision, SC.hasOutcome, SC.Rejected))
case('Explicit rejection', 'Tender_Approval_Test', False, graph)

graph = clone()
graph.remove((FIG.Run01Submit, PROV.endedAtTime, None))
case('Submission not recorded complete', 'Tender_Submission_Test', False, graph)

graph = clone()
graph.remove((FIG.Run01Submit, PROV.used, FIG.Run01Decision))
case('Parent must link actual approval used', 'Approved_Tender_Submission_Test', False, graph)
case('Approval subgoal remains independent', 'Tender_Approval_Test', True, graph)
case('Submission subgoal remains independent', 'Tender_Submission_Test', True, graph)

graph = clone()
graph.remove((FIG.Run01SubmittedTender, PROV.wasDerivedFrom, FIG.Run01RevisedTender))
graph.add((FIG.Run01SubmittedTender, PROV.wasDerivedFrom, FIG.Run01InitialDraft))
case('Submitted copy of wrong version', 'Tender_Submission_Test', False, graph)

graph = clone()
graph.remove((FIG.TenderRun01, SULO.hasPart, FIG.Run01Vote))
graph.add((URIRef('urn:regression:Another_Run'), SULO.hasPart, FIG.Run01Vote))
case('Approval from another execution cannot be borrowed', 'Approved_Tender_Submission_Test', False, graph)

for run, version in [(None, FIG.Run01RevisedTender), (FIG.TenderRun01, None)]:
    try:
        ask_tender_state(BASE, PM.Tender_Approval_Test, run=run, version=version)
    except ValueError:
        RESULTS.append({'case': 'Reject missing caller binding', 'passed': True})
    else:
        raise AssertionError('Missing binding was not rejected')

try:
    ask_tender_state(BASE, PM.Requirements_Readiness_Test, run=FIG.TenderRun01, version=FIG.Run01RevisedTender)
except ValueError:
    RESULTS.append({'case': 'Do not interpret an LLM SELECT as deterministic ASK', 'passed': True})
else:
    raise AssertionError('LLM method was not rejected by ASK helper')

print(json.dumps({'passed': True, 'checks': len(RESULTS), 'results': RESULTS}, indent=2))
