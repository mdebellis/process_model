"""Minimal RDFLib invocation example; this is not a workflow/evaluation engine.

All inputs are explicit. AllegroGraph can use the same ASK query text and
equivalent initial bindings. ChatGPT magic functions require AllegroGraph.
"""
from rdflib import Graph, Namespace, URIRef

PM = Namespace('https://www.in2use.com/process_model/')


def ask_tender_state(graph: Graph, test: URIRef, *, run: URIRef, version: URIRef) -> bool:
    """Return the raw ASK result for one explicitly selected run and version.

    A False value means no match in this dataset. Mapping it to Unsatisfied or
    Unknown requires the test's completeness/evidence policy. Never run a
    different method automatically when a query returns False or raises.
    """
    for name, value in [('test', test), ('run', run), ('version', version)]:
        if not isinstance(value, URIRef) or not str(value):
            raise ValueError(f'{name} must be an explicitly supplied IRI')
    methods = set(graph.objects(test, PM.has_evaluation_method))
    if methods != {PM.SPARQL_Evaluation}:
        raise ValueError('Select exactly one deterministic SPARQL test')
    queries = list(graph.objects(test, PM.has_sparql_query))
    if len(queries) != 1:
        raise ValueError('The selected test must have exactly one query')
    result = graph.query(str(queries[0]), initBindings={'run': run, 'version': version})
    if result.type != 'ASK':
        raise ValueError('The selected deterministic example must return ASK')
    return bool(result)
