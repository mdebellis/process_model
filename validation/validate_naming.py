"""Check naming, labels, unchanged RDF meaning, and query behavior.

Run from any directory: python validation/validate_naming.py
Requires RDFLib and lxml. Baseline defaults to the preceding GitHub revision.
Does not call an LLM; Pellet checks are recorded separately.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

from lxml import etree
from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef
from rdflib.compare import isomorphic
from rdflib.plugins.sparql.parser import parseQuery

PM = 'https://in2use.com/process_model/'
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
SWRL = Namespace('http://www.w3.org/2003/11/swrl#')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref', default='03dc687f43dd18644318579e4adb7c263815af53')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    def read(path):
        return subprocess.check_output(['git', '-C', str(root), 'show', args.baseline_ref + ':' + str(path)], stderr=subprocess.DEVNULL)
    source_path = 'ontologies/process_model_with_examples.rdf'
    before_bytes, after_bytes = read(source_path), (root / source_path).read_bytes()
    before, after = Graph().parse(data=before_bytes, format='xml'), Graph().parse(data=after_bytes, format='xml')
    rows = list(csv.DictReader((root / 'docs/naming_migration.tsv').open(), delimiter='\t'))
    mapping = {URIRef(r['old_iri']): URIRef(r['new_iri']) for r in rows}
    inverse = {v: k for k, v in mapping.items()}
    results = []
    def check(name, passed, **details):
        results.append(dict(check=name, passed=bool(passed), **details))
    def rename(term):
        return mapping.get(term, term)
    def original(term):
        return inverse.get(term, term)

    check('Unique naming map with no resource merges', len(rows) == len(mapping) == len(inverse)
          and not (set(mapping.values()) & (set(before.subjects()) - set(mapping))), count=len(rows))
    check('Only project IRIs renamed', all(str(x).startswith(PM) for pair in mapping.items() for x in pair))
    all_iris = {t for triple in after for t in triple if isinstance(t, URIRef)}
    check('No obsolete IRIs remain in RDF terms', not set(mapping) & all_iris)
    external_before = {t for triple in before for t in triple if isinstance(t, URIRef) and not str(t).startswith(PM)}
    external_after = {t for triple in after for t in triple if isinstance(t, URIRef) and not str(t).startswith(PM)}
    check('External IRIs unchanged', external_before == external_after)
    check('Stable ontology identity', set(after.subjects(RDF.type, OWL.Ontology)) == {URIRef(PM)})

    entity_types = {OWL.Class, OWL.NamedIndividual, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, SWRL.Imp, SWRL.Variable}
    entities = {s for s, t in after.subject_objects(RDF.type) if t in entity_types and str(s).startswith(PM)}
    failures = []
    for s in entities:
        local = str(s)[len(PM):]
        types = set(after.objects(s, RDF.type))
        prop = bool(types & {OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty})
        if prop:
            good = bool(re.fullmatch('[a-z]+(?:_[a-z]+)*', local))
            if OWL.ObjectProperty in types:
                good &= local.startswith('has_') or (local.startswith('is_') and local.endswith('_of')) or local in {'precedes', 'shares_input_variable'}
        else:
            tokens = local.split('_')
            good = bool(tokens) and all(re.fullmatch(r'(?:[A-Z][a-z]*|[A-Z]+|T\d+|\d+|ChatGPT)', token) for token in tokens)
        if not good:
            failures.append(local)
    check('All project names follow conventions', not failures, failures=sorted(failures), entities=len(entities))
    label_failures = []
    for s in entities:
        default = Literal(str(s)[len(PM):].replace('_', ' '), lang='en')
        labels = {o for o in after.objects(s, RDFS.label) if o.language in (None, 'en')}
        prefs = {o for o in after.objects(s, SKOS.prefLabel) if o.language in (None, 'en')}
        if labels != {default} or (prefs and prefs != {default}):
            label_failures.append(str(s))
    check('Exact default English labels and consistent preferred labels', not label_failures, failures=label_failures)
    retained = True
    for s in set(before.subjects()):
        if rename(s) not in entities:
            continue
        for predicate in (RDFS.label, SKOS.prefLabel):
            for label in before.objects(s, predicate):
                retained &= (rename(s), predicate, label) in after or (rename(s), SKOS.altLabel, label) in after
    check('Prior labels retained as defaults or alternatives', retained)

    # Normalize the complete graph, excluding only annotations intentionally
    # changed by this edit. Canonicalize the symmetric inverseOf axiom syntax.
    local_inverse = {str(new)[len(PM):]: str(old)[len(PM):] for old, new in mapping.items()}
    def undo_literal(value):
        value = re.sub(re.escape(PM) + r'([A-Za-z0-9_-]+)', lambda m: str(inverse.get(URIRef(m.group(0)), m.group(0))), value)
        value = re.sub(r'(?<!\w)(pm:|PM\.)([A-Za-z0-9_-]+)', lambda m: m.group(1) + local_inverse.get(m.group(2), m.group(2)), value)
        pattern = r'(?<![\w:/#.-])(' + '|'.join(map(re.escape, sorted(local_inverse, key=len, reverse=True))) + r')(?![\w.-])'
        return re.sub(pattern, lambda m: local_inverse[m.group(1)], value)
    ignored = {RDFS.label, SKOS.prefLabel, SKOS.altLabel, SKOS.changeNote, SKOS.historyNote, OWL.versionInfo}
    def normalize(graph, undo):
        normalized = Graph()
        for s, p, o in graph:
            if p in ignored:
                continue
            if undo:
                s, p = original(s), original(p)
                o = original(o) if isinstance(o, URIRef) else (Literal(undo_literal(str(o)), lang=o.language, datatype=o.datatype, normalize=False) if isinstance(o, Literal) else o)
            if p == OWL.inverseOf and str(s) > str(o):
                s, o = o, s
            normalized.add((s, p, o))
        return normalized
    check('All other assertions preserved under renaming', isomorphic(normalize(before, False), normalize(after, True)))
    history_preserved = all((rename(s), p, o) in after for p in (SKOS.changeNote, SKOS.historyNote)
                            for s, o in before.subject_objects(p))
    check('Historical provenance annotations preserved', history_preserved)
    check('Primary transition properties own inverse definitions', all(
        (URIRef(PM + 'has_' + name + '_step'), OWL.inverseOf, URIRef(PM + 'is_' + name + '_step_of')) in after
        for name in ('source', 'target')))

    # Give the old graph the new intended labels while retaining its old IRIs.
    # This lets exact query comparisons distinguish display edits from behavior.
    old_with_new_labels = Graph()
    for triple in before:
        old_with_new_labels.add(triple)
    for s in entities:
        old = original(s)
        old_with_new_labels.remove((old, RDFS.label, None))
        for label in after.objects(s, RDFS.label):
            old_with_new_labels.add((old, RDFS.label, label))
    def compare_query(first_text, second_text):
        a = old_with_new_labels.query(first_text)
        b = after.query(second_text)
        if a.type != b.type:
            return False, None
        if b.type in {'CONSTRUCT', 'DESCRIBE'}:
            graph = Graph()
            for triple in b.graph:
                graph.add(tuple(original(t) for t in triple))
            return isomorphic(a.graph, graph), len(b.graph)
        if b.type == 'ASK':
            return bool(a) == bool(b), int(bool(b))
        return list(a.vars) == list(b.vars) and Counter(tuple(row) for row in a) == Counter(tuple(original(t) for t in row) for row in b), len(b)
    query_results = []
    for path in sorted((root / 'queries').rglob('*.rq')):
        good, count = compare_query(read(path.relative_to(root)).decode(), path.read_text())
        query_results.append(dict(path=str(path.relative_to(root)), passed=good, count=count))
    check('All nine query results preserved with intended labels', len(query_results) == 9 and all(r['passed'] for r in query_results), queries=query_results)
    inline_results = []
    for path in sorted((root / 'docs').glob('*.md')):
        try:
            first = read(path.relative_to(root)).decode()
        except subprocess.CalledProcessError:
            continue
        a = re.findall(r'```sparql\s*\n(.*?)```', first, re.S | re.I)
        b = re.findall(r'```sparql\s*\n(.*?)```', path.read_text(), re.S | re.I)
        if not a and not b:
            continue
        assert len(a) == len(b), path
        for index, (first_text, second_text) in enumerate(zip(a, b), 1):
            good, count = compare_query(first_text, second_text)
            inline_results.append(dict(path=str(path.relative_to(root)), example=index, passed=good, count=count))
    check('All eight inline SPARQL results preserved', len(inline_results) == 8 and all(r['passed'] for r in inline_results), queries=inline_results)
    state_result = subprocess.run([sys.executable, str(root / 'state_goal_extensions_review/validate_queries.py')], capture_output=True, text=True)
    state_report = json.loads(state_result.stdout)
    check('All 26 state and caller validation cases pass', state_result.returncode == 0 and state_report.get('passed') and state_report.get('checks') == 26, report=state_report)
    templates = []
    for path in sorted((root / 'state_goal_extensions_review/queries').glob('*.rq')):
        text = path.read_text()
        parseQuery(text)
        templates.append(dict(path=str(path.relative_to(root)), parsed=True,
                              deterministic_result=None if 'llm:' in text else bool(after.query(text))))
    check('State query files parse and deterministic ASK examples pass', len(templates) == 4 and all(r['deterministic_result'] is not False for r in templates), templates=templates)
    fragment = Graph().parse(root / 'state_goal_extensions_review/state_goal_extensions.ttl')
    query_predicate = URIRef(PM + 'has_sparql_query')
    check('Review fragment stored queries match complete ontology', all((s, query_predicate, o) in after for s, o in fragment.subject_objects(query_predicate)))
    old_fragment = Graph().parse(data=read('state_goal_extensions_review/state_goal_extensions.ttl'), format='turtle')
    check('Review fragment assertions preserved', isomorphic(normalize(old_fragment, False), normalize(fragment, True)))
    xml = etree.fromstring(after_bytes)
    check('RDF types precede other properties in each XML description', all(
        not any(c.tag == '{' + str(RDF) + '}type' for c in list(e)[i + 1:])
        for e in xml for i, child in enumerate(e) if child.tag != '{' + str(RDF) + '}type'))
    broken_links = []
    output = args.output or root / 'validation/naming_validation.json'
    for path in root.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if re.match(r'[a-z]+:', target) or target.startswith('#'):
                continue
            target = target.split('#')[0]
            if target and not (path.parent / target).exists() and (path.parent / target).resolve() != output.resolve():
                broken_links.append([str(path.relative_to(root)), target])
    check('Relative Markdown links resolve', not broken_links, broken_links=broken_links)
    report = dict(passed=all(r['passed'] for r in results), baseline_commit=args.baseline_ref,
                  baseline_triples=len(before), current_triples=len(after), renamed_iris=len(rows),
                  renamed_by_kind=dict(Counter(r['kind'] for r in rows)),
                  ontology_sha256=hashlib.sha256(after_bytes).hexdigest(), checks=results,
                  scope='No LLM invoked. Query labels intentionally changed. Reasoning recorded separately in naming_reasoning.json.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], checks=len(results), failures=[r['check'] for r in results if not r['passed']], output=str(output))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
