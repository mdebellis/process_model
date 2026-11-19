"""Validate the process-model namespace migration without network or LLM calls.

Historical v2 checker; its header/name expectations describe that snapshot.
Use validation/validate_naming.py to validate the current repository source.

Requires RDFLib. From the repository root:
    python validation/validate_namespace_migration.py --baseline-ref 6a446c3

Alternatively pass --baseline-directory pointing to a pre-migration checkout.
The baseline revision remains historical; this script never rewrites it.
The output defaults to validation/namespace_migration.json.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef, Variable
from rdflib.compare import graph_diff, isomorphic, to_isomorphic
from rdflib.plugins.sparql.algebra import translateQuery
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue

TARGET = 'https://in2use.com/process_model/'
PM = Namespace(TARGET)
SWRL = Namespace('http://www.w3.org/2003/11/swrl#')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
OLD_BASES = (
    'https://www.michaeldebellis.com/supply_chain_model/',
    'https://www.michaeldebellis.com/supply_chain_figure8/',
    'https://www.michaeldebellis.com/process_model/',
    'https://www.in2use.com/process_model/',
    'https://www.in2use.com/method_omega/',
)
OLD_VARIABLE_BASES = ('urn:swrl:var#', 'urn:supply-chain-rule:var:')
OLD_ONTOLOGY = URIRef('https://www.michaeldebellis.com/supply_chain_figure8')
SOURCE_RECORDS = {
    URIRef('https://www.michaeldebellis.com/process_model/mergedSourceMetadata'),
    URIRef('https://www.michaeldebellis.com/supply_chain_figure8/sourceSchemaMetadata'),
}
ROLE_RESOURCES = {
    URIRef('https://www.michaeldebellis.com/supply_chain_model/PartnerRole'),
    URIRef('https://www.michaeldebellis.com/supply_chain_model/LeadSupplierRole'),
    URIRef('https://www.michaeldebellis.com/supply_chain_figure8/PartnerRole'),
    URIRef('https://www.michaeldebellis.com/supply_chain_figure8/LeadSupplierRole'),
}
STANDARD_TIME_INDIVIDUALS = {
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    'unitDay', 'unitHour', 'unitMinute', 'unitMonth', 'unitSecond', 'unitWeek', 'unitYear',
}


class Baseline:
    def __init__(self, root, directory, revision):
        self.root, self.directory, self.revision = root, directory, revision

    def read(self, relative):
        if self.directory:
            return (self.directory / relative).read_bytes()
        return subprocess.check_output(
            ['git', '-C', str(self.root), 'show', self.revision + ':' + relative])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-directory', type=Path)
    parser.add_argument('--baseline-ref', default='6a446c369bf2401e5107b6fa5fc5b5a945c2ac8c')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = Baseline(root, args.baseline_directory, args.baseline_ref)
    ontology_path = 'ontologies/process_model_with_examples.rdf'
    before_bytes = source.read(ontology_path)
    after_bytes = (root / ontology_path).read_bytes()
    before = Graph().parse(data=before_bytes, format='xml')
    after = Graph().parse(data=after_bytes, format='xml')
    with (root / 'docs/iri_migration.tsv').open(newline='', encoding='utf-8') as handle:
        map_rows = list(csv.DictReader(handle, delimiter='\t'))
    mapping = {URIRef(row['old_iri']): URIRef(row['new_iri']) for row in map_rows}
    checks = []

    def check(name, condition, **details):
        checks.append({'check': name, 'passed': bool(condition), **details})

    def mapped(term):
        return mapping.get(term, term) if isinstance(term, URIRef) else term

    def mapped_text(value):
        # Textual full-IRI references are assessed independently of XML ordering.
        # Query prefix syntax is checked with expanded algebra below.
        for old, new in sorted(mapping.items(), key=lambda item: len(str(item[0])), reverse=True):
            value = value.replace(str(old), str(new))
        for old in OLD_BASES:
            value = value.replace(old, TARGET)
        return value

    old_headers = set(before.subjects(RDF.type, OWL.Ontology))
    new_headers = set(after.subjects(RDF.type, OWL.Ontology))
    check('One stable target ontology IRI', new_headers == {URIRef(TARGET)},
          ontology_iris=sorted(map(str, new_headers)))
    check('Unique old mapping keys', len(map_rows) == len(mapping))
    destinations = defaultdict(list)
    for old, new in mapping.items():
        destinations[new].append(old)
    collisions = {str(new): list(map(str, olds)) for new, olds in destinations.items() if len(olds) > 1}
    allowed_aliases = {OLD_ONTOLOGY, URIRef('https://www.in2use.com/process_model/')}
    check('No unintended IRI merges', all(
        new == URIRef(TARGET) and set(olds) == allowed_aliases
        for new, olds in destinations.items() if len(olds) > 1),
        intentional_alias_convergence=collisions)
    check('All destinations use exact target namespace', all(str(v).startswith(TARGET) for v in mapping.values()))

    local_subjects = {s for s in before.subjects() if isinstance(s, URIRef)
                      and (str(s).startswith(OLD_BASES) or str(s).startswith(OLD_VARIABLE_BASES))}
    custom_time = {s for s in before.subjects(RDF.type, OWL.NamedIndividual)
                   if str(s).startswith('http://www.w3.org/2006/time#')
                   and str(s).split('#')[-1] not in STANDARD_TIME_INDIVIDUALS}
    check('All locally defined resources included in mapping', local_subjects | custom_time | old_headers <= set(mapping),
          local_subject_count=len(local_subjects), historical_time_example_count=len(custom_time),
          missing=sorted(map(str, (local_subjects | custom_time | old_headers) - set(mapping))))
    check('SWRL variables are migrated', all(s in mapping for s in before.subjects(RDF.type, SWRL.Variable)),
          variable_count=len(set(before.subjects(RDF.type, SWRL.Variable))))
    unexpected_external_mapping = [str(u) for u in mapping if not (
        str(u).startswith(OLD_BASES) or str(u).startswith(OLD_VARIABLE_BASES)
        or u in old_headers or u in custom_time)]
    check('No reused external vocabulary renamed', not unexpected_external_mapping,
          unexpected_external_mapping=unexpected_external_mapping)
    stale_terms = sorted({str(t) for triple in after for t in triple if isinstance(t, URIRef)
                          and (str(t).startswith(OLD_BASES) or str(t).startswith(OLD_VARIABLE_BASES))})
    check('No legacy project namespace in RDF terms', not stale_terms, legacy_terms=stale_terms)
    check('Historical source IRI remains a source reference',
          (URIRef(TARGET), URIRef('http://purl.org/dc/terms/source'),
           URIRef('https://www.michaeldebellis.com/supply_chain_model')) in after)
    changed_header_fields = {
        RDFS.label, OWL.versionInfo, SKOS.scopeNote, SKOS.changeNote,
        URIRef('http://purl.org/dc/terms/title'), URIRef('http://purl.org/dc/terms/description'),
    }
    retained_header = {(mapped(p), mapped(o)) for p, o in before.predicate_objects(OLD_ONTOLOGY)
                       if p not in changed_header_fields}
    actual_header = {(p, o) for p, o in after.predicate_objects(URIRef(TARGET))
                     if p not in changed_header_fields}
    old_notes = set(before.objects(OLD_ONTOLOGY, SKOS.changeNote))
    new_notes = set(after.objects(URIRef(TARGET), SKOS.changeNote))
    check('Unchanged header metadata and historical change notes retained',
          retained_header == actual_header and old_notes <= new_notes and len(new_notes - old_notes) == 1,
          prior_change_notes=len(old_notes), new_change_notes=len(new_notes - old_notes))

    mapped_roles = {mapped(s) for s in ROLE_RESOURCES}
    query_predicate = PM.has_sparql_query

    def comparable(graph, migrate):
        result = Graph()
        for s, p, o in graph:
            original_s, original_p = s, p
            if migrate:
                s, p = mapped(s), mapped(p)
                if isinstance(o, URIRef):
                    o = mapped(o)
                elif isinstance(o, Literal) and not (
                    original_p in {SKOS.changeNote, SKOS.historyNote} or original_s in SOURCE_RECORDS):
                    o = Literal(mapped_text(str(o)), lang=o.language, datatype=o.datatype)
            if s == URIRef(TARGET) and p != RDF.type:
                continue
            if s in mapped_roles and p in {RDFS.label, SKOS.prefLabel}:
                continue
            if p == query_predicate:
                continue
            result.add((s, p, o))
        return result

    expected, actual = comparable(before, True), comparable(after, False)
    equal = isomorphic(expected, actual)
    graph_details = {'compared_triples_before': len(expected), 'compared_triples_after': len(actual),
                     'excluded_intentional_changes': ['ontology-header annotations', 'four role labels/prefLabels',
                                                     'SPARQL text (expanded algebra checked separately)']}
    if not equal:
        _, missing, added = graph_diff(to_isomorphic(expected), to_isomorphic(actual))
        graph_details.update(missing_count=len(missing), added_count=len(added),
                             missing_sample=[list(map(str, t)) for t in list(missing)[:12]],
                             added_sample=[list(map(str, t)) for t in list(added)[:12]])
    check('RDF structure preserved under declared IRI mapping', equal, **graph_details)

    role_pairs = [('Partner_Role', 'Tendering_Partner_Role'),
                  ('Lead_Supplier_Role', 'Tendering_Lead_Supplier_Role')]
    for cls_name, individual_name in role_pairs:
        cls, individual = PM[cls_name], PM[individual_name]
        condition = ((cls, RDF.type, OWL.Class) in after and
                     (individual, RDF.type, OWL.NamedIndividual) in after and
                     (individual, RDF.type, cls) in after and
                     (individual, RDF.type, individual) not in after)
        check('Role class and plan-specific individual remain distinct: ' + cls_name, condition)
        for term in [cls, individual]:
            expected_label = Literal(str(term)[len(TARGET):].replace('_', ' '), lang='en')
            check('English collision-resolution label: ' + str(term)[len(TARGET):],
                  (term, RDFS.label, expected_label) in after and (term, SKOS.prefLabel, expected_label) in after)

    def canonical(value, migrate=False, field=None):
        if isinstance(value, URIRef):
            return ('iri', str(mapped(value) if migrate else value))
        if isinstance(value, Literal):
            return ('literal', str(value), value.language, str(value.datatype) if value.datatype else None)
        if isinstance(value, Variable):
            return ('variable', str(value))
        if isinstance(value, BNode):
            return ('bnode', str(value))
        if isinstance(value, CompValue):
            return ('algebra', value.name, tuple((str(k), canonical(v, migrate, str(k)))
                    for k, v in sorted(value.items()) if str(k) != '_vars'))
        if isinstance(value, dict):
            return tuple(sorted(((canonical(k, migrate), canonical(v, migrate)) for k, v in value.items()), key=repr))
        if isinstance(value, (tuple, list, set, frozenset)):
            rows = [canonical(v, migrate) for v in value]
            return tuple(sorted(rows, key=repr) if isinstance(value, (set, frozenset)) or field == 'triples' else rows)
        if hasattr(value, '__dict__'):
            return (type(value).__name__, canonical(vars(value), migrate))
        return value

    stored_queries = []
    old_query_property = URIRef('https://www.in2use.com/process_model/has_sparql_query')
    for old_test, old_query in before.subject_objects(old_query_property):
        new_test = mapped(old_test)
        new_queries = list(after.objects(new_test, query_predicate))
        condition = len(new_queries) == 1
        error = None
        if condition:
            try:
                old_algebra = translateQuery(parseQuery(str(old_query))).algebra
                new_algebra = translateQuery(parseQuery(str(new_queries[0]))).algebra
                condition = canonical(old_algebra, True) == canonical(new_algebra)
            except Exception as exc:
                condition, error = False, repr(exc)
        stored_queries.append({'test': str(new_test), 'expanded_algebra_preserved': condition, 'error': error})
    check('All four embedded queries preserve expanded SPARQL algebra',
          len(stored_queries) == 4 and all(r['expanded_algebra_preserved'] for r in stored_queries),
          queries=stored_queries, llm_executed=False)

    inverse = {new: old for old, new in mapping.items() if new != URIRef(TARGET)}

    def original(term):
        return inverse.get(term, term) if isinstance(term, URIRef) else term

    query_checks = []
    for path in sorted((root / 'queries').rglob('*.rq')):
        rel = path.relative_to(root).as_posix()
        try:
            first = before.query(source.read(rel).decode('utf-8'))
            second = after.query(path.read_text(encoding='utf-8'))
        except Exception as exc:
            query_checks.append({'path': rel, 'equivalent_after_inverse_mapping': False,
                                 'error': repr(exc)})
            continue
        condition = first.type == second.type
        if condition and first.type in {'CONSTRUCT', 'DESCRIBE'}:
            normalized = Graph()
            for triple in second.graph:
                normalized.add(tuple(original(t) for t in triple))
            condition = isomorphic(first.graph, normalized)
            count = len(second.graph)
        elif condition and first.type == 'SELECT':
            condition = (list(first.vars) == list(second.vars) and
                         Counter(tuple(row) for row in first) ==
                         Counter(tuple(original(t) for t in row) for row in second))
            count = len(second)
        elif condition and first.type == 'ASK':
            condition, count = bool(first) == bool(second), int(bool(second))
        else:
            count = None
        query_checks.append({'path': rel, 'result_type': second.type, 'result_count': count,
                             'equivalent_after_inverse_mapping': condition})
    check('Nine existing queries retain their results', len(query_checks) == 9 and
          all(r['equivalent_after_inverse_mapping'] for r in query_checks), queries=query_checks)

    template_checks = []
    for path in sorted((root / 'state_goal_extensions_review/queries').glob('*.rq')):
        query = path.read_text(encoding='utf-8')
        result = {'path': path.relative_to(root).as_posix()}
        try:
            translateQuery(parseQuery(query))
            result['syntax_valid'] = True
            if 'llm:' not in query:
                result.update(executed=True, ask_result=bool(after.query(query)))
            else:
                result.update(executed=False, reason='Vendor LLM function requires configured AllegroGraph; no LLM invoked.')
        except Exception as exc:
            result.update(syntax_valid=False, error=repr(exc))
        template_checks.append(result)
    check('Four standalone state queries parse; three deterministic examples pass',
          len(template_checks) == 4 and all(r.get('ask_result', True) and r['syntax_valid'] for r in template_checks), queries=template_checks)

    fragment_path = 'state_goal_extensions_review/state_goal_extensions.ttl'
    fragment_before = Graph().parse(data=source.read(fragment_path), format='turtle')
    fragment_after = Graph().parse(root / fragment_path, format='turtle')
    fragment_queries_match = all(
        list(after.objects(s, query_predicate)) == [o]
        for s, o in fragment_after.subject_objects(query_predicate))
    check('Additions-only Turtle fragment migrated consistently',
          isomorphic(comparable(fragment_before, True), comparable(fragment_after, False))
          and fragment_queries_match,
          triples_before=len(fragment_before), triples_after=len(fragment_after),
          embedded_queries_match_complete_ontology=fragment_queries_match)

    process = subprocess.run([sys.executable, str(root / 'state_goal_extensions_review/validate_queries.py'),
                              str(root / ontology_path)], capture_output=True, text=True)
    try:
        state_report = json.loads(process.stdout)
    except ValueError:
        state_report = {'stdout': process.stdout[-2000:], 'stderr': process.stderr[-2000:]}
    check('All 26 state/query/invocation checks pass', process.returncode == 0 and
          state_report.get('passed') is True and state_report.get('checks') == 26, report=state_report)

    executable_paths = list((root / 'queries').rglob('*.rq')) + list((root / 'state_goal_extensions_review').glob('*.py'))
    executable_paths += list((root / 'state_goal_extensions_review/queries').glob('*.rq'))
    executable_paths += [root / 'validation/expected_rule_atom_counts.tsv']
    stale_files = []
    for path in executable_paths:
        text = path.read_text(encoding='utf-8')
        found = [old for old in OLD_BASES + OLD_VARIABLE_BASES if old in text]
        if found:
            stale_files.append({'path': path.relative_to(root).as_posix(), 'legacy_namespaces': found})
    check('Executable supporting files use current IRIs', not stale_files, stale_files=stale_files)

    report = {'passed': all(c['passed'] for c in checks), 'namespace': TARGET,
              'baseline_commit': args.baseline_ref, 'baseline_triples': len(before), 'current_triples': len(after),
              'baseline_sha256': hashlib.sha256(before_bytes).hexdigest(),
              'current_sha256': hashlib.sha256(after_bytes).hexdigest(),
              'mapping_entries': len(map_rows), 'checks': checks,
              'reasoning_report': 'namespace_reasoning.json',
              'scope': 'No network or LLM calls. Reasoning is tested separately. Historical records are not rewritten.'}
    output = args.output or root / 'validation/namespace_migration.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'passed': report['passed'], 'checks': len(checks),
                      'failures': [c['check'] for c in checks if not c['passed']], 'report': str(output)}, indent=2))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
