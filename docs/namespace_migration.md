# One namespace for the process model

This page records the historical namespace-only revision. The current source
also includes the [naming cleanup and ontology-identity correction](naming_conventions.md);
the counts, ontology IRI, local names, and validation results below describe the earlier snapshot. Clients
updating from the original namespaces need the namespace map followed by the
later naming map, as explained in that guide.

18 November 2026. This revision updates the repository from commit
`6a446c369bf2401e5107b6fa5fc5b5a945c2ac8c`.

The ontology IRI and the namespace for project-defined entities are now both:

`https://in2use.com/process_model/`

The exact spelling has **no `www`** and ends in `/`. Queries use the single
project prefix `pm:`. The file remains
[process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf),
with the English ontology label **Process model with examples**.

The ontology IRI stays stable across revisions. This revision is recorded as
`process-model-v2-2026-11-18` in `owl:versionInfo`; versions do not require a new
namespace for their classes, properties or individuals. No `owl:versionIRI` is
introduced by this migration.

## Scope

The [complete IRI mapping](iri_migration.tsv) contains 308 entries covering:

- 270 project resources previously distributed across five namespaces;
- 19 locally created historical-event/date examples that had been placed in
  the W3C OWL-Time namespace;
- 17 SWRL variables, now named `pm:Variable_A`, `pm:Variable_Start_Date_A`, etc.;
- the old ontology identifier and the former namespace reference used by
  `rdfs:isDefinedBy`, both now referring to the unified ontology identifier.

Reused vocabulary keeps its original IRIs, including PROV, P-Plan, OWL-Time,
SULO and the retained upper-model vocabulary. Standard OWL-Time individuals
such as weekdays and temporal units are unchanged. The migration changes no
dates or temporal relationships.

Historical provenance text, dated validation reports and screenshots retain the
identifiers they originally described. The historical `dcterms:source` link to
the earlier supply-chain schema is also retained: it identifies a source, not
an active term in the current vocabulary. These intentional historical references
are distinct from the current query and entity identifiers.

## Role names

The old model used the same local names for two classes and their plan-specific
role individuals. The migration gives them distinct identifiers:

| Meaning | Current local name |
|---|---|
| Partner-role class | `Partner_Role` |
| Partner role in the tendering plan | `Tendering_Partner_Role` |
| Lead-supplier-role class | `Lead_Supplier_Role` |
| Lead-supplier role in the tendering plan | `Tendering_Lead_Supplier_Role` |

Each receives an English `rdfs:label` and `skos:prefLabel` made by replacing its
underscores with spaces. Other existing entity local names are retained; this
revision does not perform a general CamelCase renaming or redesign properties.

The ontology now contains **5,299 asserted triples**, compared with 5,294 before
the migration. The five additional triples are four role preferred labels and
one ontology change note. All ten SWRL rules and the existing examples remain.

## Supporting files

The migration updates the complete RDF/XML ontology, additions-only state/goal
Turtle, four stored SPARQL queries, all executable query files, Python invocation
helpers and regression cases, current rule expectations, and the current
Markdown guides. The additions-only Turtle remains a review fragment; the
RDF/XML file is the complete editable source.

The two Method Omega queries that formerly selected resources by namespace now
select them through their membership in the Method Omega plan hierarchy. Merely
changing their old namespace filter would mix tendering data into those results.
The updated queries preserve the previous results.

Keep `rdf:type` first in RDF/XML resource descriptions. The prior
[parser compatibility report](../validation/rdfxml_compatibility.md) explains
why this is necessary for the tested OWLAPI/Pellet combination. The current
checks also verify rule content, consistency and save/reload behavior.

## Validation and reproduction

- [Namespace and query checks](../validation/namespace_migration.json) compare
  the migrated graph and queries with the prior repository version, including
  preservation of external vocabulary and all 26 state-test cases.
- [Reasoning checks](../validation/namespace_reasoning.json) cover complete
  SWRL parsing, Pellet consistency and inference computation, RDF/XML save/reload,
  and the Allen relations after IRI translation.
- [Inline-query checks](../validation/namespace_inline_queries.json) cover the
  eight SPARQL examples in the Figure 8 notes.

The tools do not call an LLM or execute a workflow. The ChatGPT template remains
syntax-checked only, pending an AllegroGraph server with suitable evidence and
model configuration.

The [migration script](../tools/migrate_namespace.py) accepts separate old and
new repository directories and requires RDFLib and lxml. The
[independent validator](../validation/validate_namespace_migration.py) documents
its command-line options. Historical reports are evidence for their original
snapshots; they have not been rewritten to imply new tests.

## Applying this revision

Copy all replacement files from the update package into the existing repository,
preserving their relative paths. Open the updated RDF/XML file in Protégé and
run Pellet. Generate a fresh inferred-axiom export from this version when needed.

Use a fresh AllegroGraph repository or replace the old dataset when loading the
migrated model. Appending it to the old dataset leaves both sets of entity IRIs
present; the new IRIs do not automatically rename old stored triples. Existing
external scripts that refer to project entities should use the mapping table.
