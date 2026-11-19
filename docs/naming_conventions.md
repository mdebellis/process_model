# Naming conventions and migration

18 November 2026. The current version is `process-model-v3-2026-11-18`.

The ontology remains **Process model with examples**, with the stable ontology
IRI and project namespace `https://in2use.com/process_model/`, abbreviated `pm:`.
This revision standardizes project-owned local names and labels. The
[naming map](naming_migration.tsv) records **175 renamed IRIs**. The complete
[RDF/XML source](../ontologies/process_model_with_examples.rdf) now contains
**5,505 asserted triples**, including all ten SWRL rules.

## Names and labels

Classes and individuals use Title_Case with underscores between words.
Rule and variable identifiers follow the same readable form. Source-figure
task identifiers retain their numbers with an uppercase initial, such as
`T11_Send_Tender_For_Voting_Task`. Acronyms retain their capitals, including
`SPARQL`, `CFT`, `UK`, and `WWII`; the product name `ChatGPT` retains its spelling.

Properties use lower_case with underscores. Object properties normally use a
primary `has_…` direction and an `is_…_of` name for an existing inverse.
`precedes` remains a directional exception, and `shares_input_variable` retains
its symmetric meaning without introducing a separate inverse name.

| Earlier local name | Current local name |
|---|---|
| `CollaborationStep` | `Collaboration_Step` |
| `TenderRun01` | `Tender_Run_01` |
| `t11SendTenderForVotingTask` | `T11_Send_Tender_For_Voting_Task` |
| `transitionFrom` | `has_source_step` |
| `hasOutgoingTransition` | `is_source_step_of` |
| `expected_duration` | `has_expected_duration` |
| `sharesInputVariable` | `shares_input_variable` |

Every project entity has a direct English `rdfs:label` made by replacing the
underscores in its local name with spaces, for example
`"T11 Send Tender For Voting Task"@en`. Existing English `skos:prefLabel` values
follow the same convention. Replaced labels are retained as `skos:altLabel`,
with their original language tags, so earlier descriptive text is still
available. The ontology itself keeps its English label **Process model with
examples**. Standard external vocabulary IRIs and labels are unchanged,
including reused P-Plan, PROV, SULO, and OWL-Time terms.

## What changes semantically

The revision changes identifiers, labels, references in queries and supporting
files, and version/change annotations. It preserves the example data and the
logical meanings of the classes, properties, and rules. The increase from
5,299 to 5,505 triples comes from label and change annotations.

Two existing `owl:inverseOf` statements are now written on the primary side:

| Primary property | Existing inverse |
|---|---|
| `has_source_step` | `is_source_step_of` |
| `has_target_step` | `is_target_step_of` |

Reversing the written direction of these symmetric inverse declarations does
not change their meaning. This cleanup introduces no new inverse properties,
domain/range restrictions, or other logical constraints. A `has_` name does not
by itself assert an inverse or add a domain/range axiom.

## Updating queries and external clients

The repository's active query files, embedded state tests, helpers, examples,
and rule expectations use the current identifiers. Clients and stored data
outside this repository must translate their own references.

For clients using the previous unified namespace, apply
[naming_migration.tsv](naming_migration.tsv). For clients still using the
original supply-chain or Method Omega namespaces, apply both maps in order:

1. Apply the original [namespace map](iri_migration.tsv).
2. Apply the [naming map](naming_migration.tsv) to that result. If an IRI has no
   entry in the second map, retain the name produced by the first map.

For example, the original supply-chain `CollaborationStep` becomes
`pm:CollaborationStep` in the first map and `pm:Collaboration_Step` in the
second. Update subjects, predicates, and object IRIs, as well as IRIs embedded
in SPARQL text or application configuration. Loading the revised ontology does
not rename existing external data automatically; replacing or migrating that
data prevents old and new identifiers from being mixed.

The [namespace migration notes](namespace_migration.md), original maps,
previous validation reports, provenance text, and screenshots remain historical
evidence. Their earlier names and counts describe the snapshots tested then.

## Validation and RDF/XML compatibility

- [Naming and query checks](../validation/naming_validation.json) record the
  structural, label, mapping, and query checks for this revision.
- [Reasoning checks](../validation/naming_reasoning.json) record the parser and
  reasoner checks for this revision.

Keep the complete ontology in RDF/XML, with each resource description's
`rdf:type` elements before its other properties. The
[RDF/XML compatibility report](../validation/rdfxml_compatibility.md) explains
the earlier OWLAPI parsing failure this ordering avoids. Historical reports
remain unchanged; the current reports identify the source they test.
