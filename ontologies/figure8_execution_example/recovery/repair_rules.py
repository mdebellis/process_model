"""Restore the ten SWRL rules from an intact donor, preserving other RDF.

The source contains empty rules, orphan rule atoms, dangling lists and SWRL
structural terms misdeclared as annotation properties. This repair is deliberately
restricted to those structures. No inferred triples or execution data are added.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rdflib import BNode, Graph, Namespace, RDF, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import OWL

SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
STRUCTURAL_PROPERTIES = {
    SWRL.argument1, SWRL.argument2, SWRL.arguments, SWRL.body,
    SWRL.builtin, SWRL.classPredicate, SWRL.head, SWRL.propertyPredicate,
}


def closure(graph: Graph, roots: set) -> set:
    """Return roots and all blank nodes reachable through outgoing triples."""
    seen = set(roots)
    pending = list(roots)
    while pending:
        subject = pending.pop()
        for obj in graph.objects(subject):
            if isinstance(obj, BNode) and obj not in seen:
                seen.add(obj)
                pending.append(obj)
    return seen


def subject_graph(graph: Graph, subjects: set) -> Graph:
    result = Graph()
    for subject in subjects:
        for triple in graph.triples((subject, None, None)):
            result.add(triple)
    return result


def list_items(graph: Graph, head) -> list:
    result = []
    seen = set()
    node = head
    while node != RDF.nil:
        assert node is not None and node not in seen, "Missing or cyclic RDF list"
        seen.add(node)
        firsts = list(graph.objects(node, RDF.first))
        rests = list(graph.objects(node, RDF.rest))
        assert len(firsts) == len(rests) == 1, "Malformed RDF list"
        result.append(firsts[0])
        node = rests[0]
    return result


def validate_rules(graph: Graph, expected: set) -> dict:
    rules = set(graph.subjects(RDF.type, SWRL.Imp))
    assert rules == expected, "Unexpected rule identities"
    details = {}
    for rule in sorted(rules):
        assert isinstance(rule, URIRef), "Original named rule identity was lost"
        counts = {}
        for side in (SWRL.body, SWRL.head):
            heads = list(graph.objects(rule, side))
            assert len(heads) == 1
            atoms = list_items(graph, heads[0])
            assert atoms, f"Empty rule side: {rule} {side}"
            for atom in atoms:
                assert any(str(t).startswith(str(SWRL)) for t in graph.objects(atom, RDF.type))
                for args in graph.objects(atom, SWRL.arguments):
                    assert list_items(graph, args), "Empty built-in argument list"
            counts[str(side).split("#")[-1]] = len(atoms)
        details[str(rule)] = counts
    return details


def repair(source: Path, donor: Path, output: Path) -> dict:
    original = Graph().parse(source, format="turtle")
    intact = Graph().parse(donor, format="turtle")
    donor_roots = set(intact.subjects(RDF.type, SWRL.Imp))
    assert len(donor_roots) == 10
    donor_details = validate_rules(intact, donor_roots)
    donor_nodes = closure(intact, donor_roots)
    donor_rules = subject_graph(intact, donor_nodes)
    donor_variables = set(intact.subjects(RDF.type, SWRL.Variable))

    # Include anonymous rule records, named dangling roots and orphan atoms.
    damaged_roots = set(original.subjects(RDF.type, SWRL.Imp))
    damaged_roots.update(original.subjects(SWRL.body, None))
    damaged_roots.update(original.subjects(SWRL.head, None))
    for subject, predicate, obj in original:
        if isinstance(subject, BNode) and (
            str(predicate).startswith(str(SWRL))
            or (predicate == RDF.type and str(obj).startswith(str(SWRL)))
        ):
            damaged_roots.add(subject)
    damaged_nodes = closure(original, damaged_roots)
    for node in damaged_nodes:
        if isinstance(node, BNode):
            external = [(s, p, node) for s, p in original.subject_predicates(node)
                        if s not in damaged_nodes]
            assert not external, f"Rule fragment is shared with unrelated RDF: {external}"
    removed = set(subject_graph(original, damaged_nodes))
    annotation_declarations = {
        (p, RDF.type, OWL.AnnotationProperty) for p in STRUCTURAL_PROPERTIES
        if (p, RDF.type, OWL.AnnotationProperty) in original
    }
    removed.update(annotation_declarations)
    retained = set(original) - removed

    repaired = Graph()
    for prefix, namespace in original.namespaces():
        repaired.bind(prefix, namespace)
    for triple in retained:
        repaired.add(triple)
    remap = {node: BNode() for node in donor_nodes if isinstance(node, BNode)}
    for subject, predicate, obj in donor_rules:
        repaired.add((remap.get(subject, subject), predicate, remap.get(obj, obj)))
    for variable in donor_variables:
        repaired.add((variable, RDF.type, SWRL.Variable))

    restored_nodes = closure(repaired, donor_roots)
    assert isomorphic(donor_rules, subject_graph(repaired, restored_nodes))
    assert retained <= set(repaired), "Unrelated source triples were changed"
    assert validate_rules(repaired, donor_roots) == donor_details
    assert set(repaired.subjects(RDF.type, SWRL.Variable)) >= donor_variables
    assert not any((p, RDF.type, OWL.AnnotationProperty) in repaired
                   for p in STRUCTURAL_PROPERTIES)

    output.parent.mkdir(parents=True, exist_ok=True)
    repaired.serialize(output, format="turtle")
    reloaded = Graph().parse(output, format="turtle")
    assert isomorphic(repaired, reloaded), "Turtle round trip changed RDF"
    validate_rules(reloaded, donor_roots)
    return {
        "source": str(source), "donor": str(donor), "output": str(output),
        "source_triples": len(original), "result_triples": len(repaired),
        "removed_damaged_rule_triples": len(removed) - len(annotation_declarations),
        "removed_swrl_annotation_declarations": sorted(str(t[0]) for t in annotation_declarations),
        "preserved_unrelated_triples": len(retained),
        "copied_rule_triples": len(donor_rules),
        "restored_variable_declarations": len(donor_variables),
        "rules_match_donor_isomorphically": True,
        "turtle_round_trip_isomorphic": True,
        "rules": donor_details,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("donor", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(repair(args.source, args.donor, args.output), indent=2))
