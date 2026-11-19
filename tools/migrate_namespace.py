"""Migrate the pre-consolidation repository to its stable project namespace.

Usage: python tools/migrate_namespace.py --source-root OLD --target-root NEW
Requires rdflib and lxml. OLD and NEW must be different directories.
Only the ontology, query/helper sources, additions-only Turtle, active rule
expectations, and IRI mapping are written. Documentation is maintained separately.
Historical validation records and provenance text are intentionally preserved.
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

from lxml import etree
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL

TARGET = 'https://in2use.com/process_model/'
BASES = (
    'https://www.michaeldebellis.com/supply_chain_model/',
    'https://www.in2use.com/process_model/',
    'https://www.in2use.com/method_omega/',
    'https://www.michaeldebellis.com/process_model/',
    'https://www.michaeldebellis.com/supply_chain_figure8/',
)
OLD_ONTOLOGY = 'https://www.michaeldebellis.com/supply_chain_figure8'
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DCT = Namespace('http://purl.org/dc/terms/')
SWRL = Namespace('http://www.w3.org/2003/11/swrl#')
TIME = 'http://www.w3.org/2006/time#'
TIME_EXAMPLES = '''American_Civil_War April_12_1861 August_7_1945
Battle_of_Gettysburg German_Invasion_of_France Invasion_of_Poland July_1_1863
July_3_1863 July_4_1946 June_25_1940 May_10_1940 May_26_1865 October_28_1944
October_6_1939 September_1_1939 September_2_1945 Soviet-Japanese_War_WWII
The_Phony_War UK_Participation_in_WWII'''.split()
ROLE_NAMES = {
    BASES[0] + 'PartnerRole': 'Partner_Role',
    BASES[0] + 'LeadSupplierRole': 'Lead_Supplier_Role',
    BASES[4] + 'PartnerRole': 'Tendering_Partner_Role',
    BASES[4] + 'LeadSupplierRole': 'Tendering_Lead_Supplier_Role',
}
HISTORICAL_SUBJECTS = {
    URIRef(BASES[3] + 'mergedSourceMetadata'),
    URIRef(BASES[4] + 'sourceSchemaMetadata'),
}
PREFIX = re.compile(r'(?im)^\s*(?:PREFIX\s+|@prefix\s+)([\w-]*):\s*<([^>]+)>\s*\.?[ \t]*\n?')


def variable_name(iri):
    local = iri.rsplit('#', 1)[-1] if '#' in iri else iri.rsplit(':', 1)[-1]
    words = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', local).split('_')
    return 'Variable_' + '_'.join(w[:1].upper() + w[1:] for w in words)


def make_mapping(graph):
    mapping = {OLD_ONTOLOGY: TARGET}
    for triple in graph:
        for term in triple:
            if not isinstance(term, URIRef):
                continue
            old = str(term)
            for base in BASES:
                if old.startswith(base):
                    mapping[old] = TARGET + ROLE_NAMES.get(old, old[len(base):])
                    break
    for name in TIME_EXAMPLES:
        assert any(graph.triples((URIRef(TIME + name), None, None))), name
        mapping[TIME + name] = TARGET + name
    for var in graph.subjects(RDF.type, SWRL.Variable):
        mapping[str(var)] = TARGET + variable_name(str(var))
    # Only the old header and an undeclared namespace reference converge.
    reverse = defaultdict(list)
    for old, new in mapping.items():
        reverse[new].append(old)
    for new, olds in reverse.items():
        assert len(olds) == 1 or (new == TARGET and set(olds) == {OLD_ONTOLOGY, BASES[1]}), (new, olds)
    return mapping


def translate_iri(value, mapping):
    if value in mapping:
        return mapping[value]
    for base in BASES:
        if value.startswith(base):
            return TARGET + value[len(base):]
    return value


def translate_text(text, mapping):
    """Translate explicit IRIs and known prefixed names in query/helper text."""
    declarations = list(PREFIX.finditer(text))
    aliases = {m.group(1): m.group(2) for m in declarations}
    # Expand project names before coalescing their namespace declarations.
    for alias, ns in aliases.items():
        if ns not in BASES and ns != TIME:
            continue
        pattern = re.compile(r'(?<![\w:/])' + re.escape(alias) + r':([A-Za-z_][\w.-]*)?')
        def prefixed(match):
            old = ns + (match.group(1) or '')
            new = translate_iri(old, mapping)
            if new.startswith(TARGET):
                return 'pm:' + new[len(TARGET):]
            return match.group(0)
        text = pattern.sub(prefixed, text)
    # Full IRIs in angle brackets; includes prefix namespace declarations.
    text = re.sub(r'<([^<>\s]+)>', lambda m: '<' + translate_iri(m.group(1), mapping) + '>', text)
    # URI strings in Python and full IRIs in explanatory text.
    for old in sorted(mapping, key=len, reverse=True):
        text = re.sub(re.escape(old) + r'(?![A-Za-z0-9_/#.-])', lambda m, old=old: mapping[old], text)
    for base in BASES:
        text = text.replace(base, TARGET)
    # Query files need just one project prefix, including an added prefix when
    # only a custom individual from the Time namespace occurred.
    seen = False
    def declaration(match):
        nonlocal seen
        ns = match.group(2)
        if ns != TARGET:
            return match.group(0)
        if seen:
            return ''
        seen = True
        return ('@prefix pm: <' + TARGET + '> .\n' if '@prefix' in match.group(0).lower()
                else 'PREFIX pm: <' + TARGET + '>\n')
    text = PREFIX.sub(declaration, text)
    return text


def translate_graph(graph, mapping):
    result = Graph(bind_namespaces='none')
    for prefix, ns in graph.namespaces():
        if str(ns) not in BASES and prefix != 'pm':
            result.bind(prefix, ns)
    result.bind('pm', URIRef(TARGET), replace=True)
    for s, p, o in graph:
        subject, predicate = s, p
        s = URIRef(mapping[str(s)]) if isinstance(s, URIRef) and str(s) in mapping else s
        p = URIRef(mapping[str(p)]) if isinstance(p, URIRef) and str(p) in mapping else p
        if isinstance(o, URIRef) and str(o) in mapping:
            o = URIRef(mapping[str(o)])
        elif (isinstance(o, Literal) and subject not in HISTORICAL_SUBJECTS
              and predicate not in (SKOS.changeNote, SKOS.historyNote)):
            value = translate_text(str(o), mapping)
            if value != str(o):
                o = Literal(value, lang=o.language, datatype=o.datatype, normalize=False)
        result.add((s, p, o))
    return result


def write_rdfxml(graph, path):
    graph.serialize(destination=path, format='xml')
    # Essential OWLAPI 4 compatibility: declare types before SWRL properties.
    tree = etree.parse(str(path))
    for description in tree.getroot():
        for type_node in reversed(description.findall('{' + str(RDF) + '}type')):
            description.remove(type_node)
            description.insert(0, type_node)
    tree.write(str(path), xml_declaration=True, encoding='UTF-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--target-root', type=Path, required=True)
    args = parser.parse_args()
    source, target = args.source_root.resolve(), args.target_root.resolve()
    assert source != target, 'Use separate source and destination directories'
    baseline = Graph().parse(source / 'ontologies/process_model_with_examples.rdf')
    mapping = make_mapping(baseline)
    updated = translate_graph(baseline, mapping)
    ontology = URIRef(TARGET)
    updated.set((ontology, RDFS.label, Literal('Process model with examples', lang='en')))
    updated.set((ontology, DCT.title, Literal('Process model with examples', lang='en')))
    updated.set((ontology, DCT.description, Literal(
        'Self-contained experimental process ontology combining a collaborative tendering plan and its synthetic execution, '
        'the abstract Method Omega development methodology, temporal reasoning examples, and provisional state and goal tests. '
        'The ontology and project-defined entities use https://in2use.com/process_model/. Reused external vocabulary retains '
        'its original IRIs. The model includes ten SWRL rules and SPARQL tests; it does not implement a workflow engine. '
        'No Method Omega execution, LLM evaluation record or materialized inference is included.', lang='en')))
    updated.set((ontology, OWL.versionInfo, Literal('process-model-v2-2026-11-18')))
    for value in list(updated.objects(ontology, SKOS.scopeNote)):
        if 'State/goal extensions are a first draft.' in str(value):
            updated.remove((ontology, SKOS.scopeNote, value))
            updated.add((ontology, SKOS.scopeNote, Literal(str(value).replace(
                'Existing ontology IRI and vocabulary IRIs are preserved.',
                'The ontology and project-defined entities share https://in2use.com/process_model/; reused external vocabulary keeps its original IRIs.'), lang='en')))
    updated.add((ontology, SKOS.changeNote, Literal(
        '2026-11-18 (ChatGPT): Consolidated the ontology identity and all project-defined resources under '
        'https://in2use.com/process_model/ (without www). Migrated five project namespaces, nineteen locally created '
        'historical-event/date examples previously in the OWL-Time namespace, and seventeen SWRL variables. '
        'Kept the Partner Role and Lead Supplier Role classes distinct from the Tendering Partner Role and '
        'Tendering Lead Supplier Role individuals. Updated stored queries and supporting files. Preserved external '
        'vocabulary IRIs, historical provenance text, dates, axioms and example relationships. Kept rdf:type first '
        'in RDF/XML descriptions for OWLAPI compatibility. The ontology IRI remains stable across future versions; '
        'this revision is recorded in owl:versionInfo.', lang='en')))
    for local in ROLE_NAMES.values():
        term = URIRef(TARGET + local)
        for predicate in (RDFS.label, SKOS.prefLabel):
            updated.set((term, predicate, Literal(local.replace('_', ' '), lang='en')))
    (target / 'docs').mkdir(exist_ok=True)
    with (target / 'docs/iri_migration.tsv').open('w', newline='') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['old_iri', 'new_iri', 'kind'])
        for old, new in sorted(mapping.items()):
            kind = ('ontology' if old == OLD_ONTOLOGY else 'namespace_reference' if old in BASES
                    else 'swrl_variable' if old.startswith('urn:') else 'local_time_example' if old.startswith(TIME)
                    else 'role_collision' if old in ROLE_NAMES else 'project_entity')
            writer.writerow([old, new, kind])
    write_rdfxml(updated, target / 'ontologies/process_model_with_examples.rdf')
    fragment = Graph().parse(source / 'state_goal_extensions_review/state_goal_extensions.ttl')
    translate_graph(fragment, mapping).serialize(destination=target / 'state_goal_extensions_review/state_goal_extensions.ttl', format='turtle')
    paths = list(source.glob('queries/**/*.rq')) + list(source.glob('state_goal_extensions_review/queries/*.rq'))
    paths += [source / 'state_goal_extensions_review/query_examples.py', source / 'state_goal_extensions_review/validate_queries.py']
    paths += [source / 'validation/expected_rule_atom_counts.tsv']
    for path in paths:
        text = translate_text(path.read_text(), mapping)
        text = text.replace('urn:regression:Another_Run', TARGET + 'Regression_Another_Run')
        # Example membership must follow the model after namespaces converge.
        if path.name == '02_method_omega_transitions.rq':
            text = text.replace('FILTER(STRSTARTS(STR(?transition), STR(pm:)))',
                'pm:Method_Omega (^pp:isStepOfPlan/pp:isDecomposedAsPlan)* ?plan.\n'
                '  ?from pp:isStepOfPlan ?plan.')
        if path.name == '03_method_omega_deliverables.rq':
            text = text.replace('FILTER(STRSTARTS(STR(?variable), STR(pm:)))',
                'pm:Method_Omega (^pp:isStepOfPlan/pp:isDecomposedAsPlan)* ?plan.\n'
                '  ?producer pp:isStepOfPlan ?plan.')
        if path.name == 'validate_queries.py':
            text = text.replace("ROOT / 'process_model_with_examples.rdf'", "ROOT.parent / 'ontologies' / 'process_model_with_examples.rdf'")
            text = text.replace("FIG = Namespace('" + TARGET + "')\n", '')
            text = text.replace("SC = Namespace('" + TARGET + "')\n", '')
            text = text.replace('FIG.', 'PM.').replace('SC.', 'PM.')
        (target / path.relative_to(source)).write_text(text)
    print({'mapped_iris': len(mapping), 'baseline_triples': len(baseline), 'updated_triples': len(updated), 'ontology_iri': TARGET})


if __name__ == '__main__':
    main()
