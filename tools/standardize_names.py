"""Reproduce the historical v3 naming revision from its baseline.

This generator intentionally retains that revision's slash-terminated ontology
IRI. The current source uses a slashless ontology IRI; see docs/naming_conventions.md.
Validate the current source with validation/validate_naming.py.

Usage: python tools/standardize_names.py --baseline-ref 03dc687
Requires RDFLib and lxml. Reads the baseline from git; writes only the current
ontology, review fragment, executable examples, and active documentation.
Historical migration scripts, maps, reports and provenance remain historical.
"""
import argparse
import csv
import re
import subprocess
from pathlib import Path

from lxml import etree
from rdflib import Graph, Literal, Namespace, OWL, RDF, RDFS, URIRef

PM = 'https://in2use.com/process_model/'
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
SWRL = Namespace('http://www.w3.org/2003/11/swrl#')
KINDS = {OWL.Class: 'class', OWL.NamedIndividual: 'individual',
         OWL.ObjectProperty: 'object_property', OWL.DatatypeProperty: 'data_property',
         OWL.AnnotationProperty: 'annotation_property', SWRL.Imp: 'rule', SWRL.Variable: 'variable'}
PROPERTY_NAMES = {
    'aboutVersion': 'has_subject_version',
    'assignedAgent': 'has_assigned_agent', 'assignedRole': 'has_assigned_role',
    'assignmentForStep': 'has_assigned_step', 'choiceAfterStep': 'has_choice_source_step',
    'conditionVariable': 'has_condition_variable', 'eventForRole': 'has_event_role',
    'expectedOutcome': 'has_expected_outcome', 'expected_duration': 'has_expected_duration',
    'exposes_output_variable': 'has_exposed_output_variable',
    'hasAlternative': 'has_alternative', 'hasCondition': 'has_condition',
    'hasFlowDependency': 'has_flow_dependency', 'hasOutcome': 'has_outcome',
    'hasIncomingTransition': 'is_target_step_of', 'hasOutgoingTransition': 'is_source_step_of',
    'transitionFrom': 'has_source_step', 'transitionTo': 'has_target_step',
    'messagePayloadVariable': 'has_message_payload_variable', 'payload': 'has_payload',
    'plannedReceiverRole': 'has_planned_receiver_role', 'plannedSenderRole': 'has_planned_sender_role',
    'previousVersion': 'has_previous_version', 'recipient': 'has_recipient', 'sender': 'has_sender',
    'sharesInputVariable': 'shares_input_variable', 'triggeredByVariable': 'has_trigger_variable',
    'versionIdentifier': 'has_version_identifier', 'versionOf': 'has_document_series',
}


def title_name(name):
    # Keep the product spelling ChatGPT, acronyms, and source-figure IDs (T11).
    if name == 'ChatGPT_Evaluation':
        return name
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name.replace('-', '_'))
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    name = re.sub(r'\bRun(\d+)', r'Run_\1', name.replace('_', ' ')).replace(' ', '_')
    return '_'.join(word[:1].upper() + word[1:] for word in name.split('_'))


def build_map(graph):
    records = []
    for subject in sorted(set(graph.subjects())):
        if not isinstance(subject, URIRef) or not str(subject).startswith(PM) or str(subject) == PM:
            continue
        kinds = {KINDS[t] for t in graph.objects(subject, RDF.type) if t in KINDS}
        if not kinds:
            raise ValueError('Unclassified project entity: ' + str(subject))
        old = str(subject)[len(PM):]
        new = PROPERTY_NAMES.get(old, old) if any(k.endswith('property') for k in kinds) else title_name(old)
        records.append((str(subject), PM + new, ','.join(sorted(kinds))))
    destinations = [new for old, new, kind in records]
    assert len(destinations) == len(set(destinations)), 'Naming collision'
    return records


def translate_text(value, mapping):
    local = {old[len(PM):]: new[len(PM):] for old, new in mapping.items() if old != new}
    value = re.sub(re.escape(PM) + r'([A-Za-z0-9_-]+)',
                   lambda m: mapping.get(m.group(0), m.group(0)), value)
    value = re.sub(r'(?<![\w])(?:pm:|PM\.)([A-Za-z0-9_-]+)',
                   lambda m: m.group(0)[:3] + local.get(m.group(1), m.group(1)), value)
    value = re.sub(r'''\bPM\[(['"])([A-Za-z0-9_-]+)\1\]''',
                   lambda m: 'PM[' + m.group(1) + local.get(m.group(2), m.group(2)) + m.group(1) + ']', value)
    # Bare local names in code samples and prose. Avoid rewriting plain English
    # sender/recipient/payload or any term in another vocabulary's full IRI.
    names = [n for n in local if any(c.isupper() for c in n) or '_' in n]
    if names:
        pattern = r'(?<![\w:/#.-])(' + '|'.join(map(re.escape, sorted(names, key=len, reverse=True))) + r')(?![\w.-])'
        value = re.sub(pattern, lambda m: local[m.group(1)], value)
    return value


def mapped_graph(graph, mapping):
    result = Graph()
    for prefix, iri in graph.namespaces():
        result.bind(prefix, iri)
    historical = {URIRef(PM + n) for n in ('baseModelMetadata', 'mergedSourceMetadata', 'sourceSchemaMetadata')}
    annotations = set(graph.subjects(RDF.type, OWL.AnnotationProperty))
    annotations.update({RDFS.comment, RDFS.label, RDFS.seeAlso, RDFS.isDefinedBy,
                        SKOS.definition, SKOS.note, SKOS.scopeNote, SKOS.example})
    for s, p, o in graph:
        if (isinstance(o, Literal) and s not in historical
                and (p in annotations or p == URIRef(PM + 'has_sparql_query'))
                and p not in (RDFS.label, SKOS.prefLabel, SKOS.altLabel, SKOS.changeNote, SKOS.historyNote)):
            o = Literal(translate_text(str(o), mapping), lang=o.language, datatype=o.datatype, normalize=False)
        result.add(tuple(URIRef(mapping.get(str(x), str(x))) if isinstance(x, URIRef) else x for x in (s, p, o)))
    for s in set(result.subjects()):
        if not isinstance(s, URIRef) or not str(s).startswith(PM) or str(s) == PM:
            continue
        if not any(t in KINDS for t in result.objects(s, RDF.type)):
            continue
        default = Literal(str(s)[len(PM):].replace('_', ' '), lang='en')
        for predicate in (RDFS.label, SKOS.prefLabel):
            for old in list(result.objects(s, predicate)):
                if old.language not in (None, 'en'):
                    continue
                result.remove((s, predicate, old))
                if old != default:
                    result.add((s, SKOS.altLabel, old))
            # A preferred label is maintained only when already used. Every
            # project entity gets the default English rdfs:label.
            if predicate == RDFS.label or any(graph.objects(URIRef(next((a for a, b in mapping.items() if b == str(s)), str(s))), SKOS.prefLabel)):
                result.add((s, predicate, default))
    # Put the two pre-existing inverse definitions on their has_ primary side.
    for primary, inverse in [('has_source_step', 'is_source_step_of'), ('has_target_step', 'is_target_step_of')]:
        triple = (URIRef(PM + inverse), OWL.inverseOf, URIRef(PM + primary))
        if triple in result:
            result.remove(triple)
            result.add((triple[2], OWL.inverseOf, triple[0]))
    return result


def write_xml(graph, path):
    graph.serialize(destination=path, format='xml')
    tree = etree.parse(str(path))
    for description in tree.getroot():
        for node in reversed(description.findall('{' + str(RDF) + '}type')):
            description.remove(node)
            description.insert(0, node)
    tree.write(str(path), xml_declaration=True, encoding='UTF-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-ref', default='03dc687f43dd18644318579e4adb7c263815af53')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    def read(path):
        return subprocess.check_output(['git', '-C', str(root), 'show', args.baseline_ref + ':' + str(path)])
    source = Graph().parse(data=read('ontologies/process_model_with_examples.rdf'), format='xml')
    records = build_map(source)
    mapping = {old: new for old, new, kind in records if old != new}
    with (root / 'docs/naming_migration.tsv').open('w') as stream:
        writer = csv.writer(stream, delimiter='\t', lineterminator='\n')
        writer.writerow(['old_iri', 'new_iri', 'kind'])
        writer.writerows(row for row in records if row[0] != row[1])
    updated = mapped_graph(source, mapping)
    updated.set((URIRef(PM), OWL.versionInfo, Literal('process-model-v3-2026-11-18')))
    updated.add((URIRef(PM), SKOS.changeNote, Literal(
        '2026-11-18 (ChatGPT): Standardized project-defined class and individual IRIs to Title_Case with underscores, '
        'and property IRIs to lowercase with underscores and has_/is_..._of naming where applicable. '
        'Standardized rule identifiers and English default labels; retained prior labels as alternative labels. '
        'Updated queries and supporting files. Preserved external vocabulary, historical provenance, logical meanings, '
        'and RDF/XML type-first serialization. Recorded the renaming in docs/naming_migration.tsv.', lang='en')))
    write_xml(updated, root / 'ontologies/process_model_with_examples.rdf')
    fragment = Graph().parse(data=read('state_goal_extensions_review/state_goal_extensions.ttl'), format='turtle')
    mapped_graph(fragment, mapping).serialize(destination=root / 'state_goal_extensions_review/state_goal_extensions.ttl', format='turtle')
    paths = list(root.glob('queries/**/*.rq')) + list(root.glob('state_goal_extensions_review/queries/*.rq'))
    paths += list(root.glob('state_goal_extensions_review/*.py'))
    paths += [root / 'validation/expected_rule_atom_counts.tsv']
    paths += [root / 'docs' / name for name in ('figure8_model_notes.md', 'figure8_execution.md', 'method_omega_notes.md')]
    paths += [root / 'state_goal_extensions_review/README.md']
    for path in paths:
        path.write_text(translate_text(read(path.relative_to(root)).decode(), mapping))
    print({'renamed': len(mapping), 'entities': len(records), 'triples_before': len(source), 'triples_after': len(updated)})


if __name__ == '__main__':
    main()
