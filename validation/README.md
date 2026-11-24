# Validation records

The repository has one ontology source: [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf). Validation records document checks on this source and the earlier stages from which it was assembled.

## Current Customer Portal execution checks

The source now contains **7,158 asserted triples**, including the unchanged ten SWRL rules. The [Customer Portal execution report](customer_portal_execution.json) checks the fictional execution snapshot, preservation of the existing ontology, OWLAPI 4.5.29/Pellet parsing and reasoning, and Allen relations on completed actual intervals. The [execution walkthrough](../docs/Customer_Portal_Execution.md) describes the scenario and query expectations. All data remains in the default graph and the existing namespace.

## Historical ontology-identity checks

At the ontology-identity revision, the ontology contained **5,506 asserted triples**, including ten complete SWRL rules and the [state and goal extensions](../state_goal_extensions_review/README.md). Its ontology IRI is `https://in2use.com/process_model` (no trailing slash). Its entity namespace and `pm:` prefix remain `https://in2use.com/process_model/`; `owl:versionInfo` is `process-model-v4-2026-11-18`.

The [naming conventions](../docs/naming_conventions.md) explain the distinction between ontology identity and entity namespace. The header correction updates 54 `rdfs:isDefinedBy` references in the complete source and 49 in the review fragment. Class, property, and individual IRIs, labels, logical axioms, and query text are unchanged. The additional triple is an ontology change note.

[ontology_identity.json](ontology_identity.json) records that revision's structural, naming, reference, and query checks; [ontology_identity_reasoning.json](ontology_identity_reasoning.json) records the focused comparison with commit `8cfff5f` and its parser/reasoner results. Run `python validation/validate_naming.py` to repeat the structural/query checks; it writes the current report without overwriting the historical naming report.

## Earlier naming revision

The 175 entity IRI changes in [naming_migration.tsv](../docs/naming_migration.tsv), direct English labels, retained alternative labels, and two inverse declarations moved to their primary side were introduced in the preceding 5,505-triple version. [naming_validation.json](naming_validation.json) and [naming_reasoning.json](naming_reasoning.json) remain unchanged evidence for that revision.

## Earlier namespace migration

The [namespace migration notes](../docs/namespace_migration.md), [namespace map](../docs/iri_migration.tsv), and [namespace_migration.json](namespace_migration.json) describe the prior 5,299-triple revision, before the naming cleanup. Its increase from 5,294 triples consisted of four role preferred labels and one migration change note. The namespace reasoning and inline-query reports likewise describe that earlier snapshot. Clients starting with pre-unification identifiers must apply the namespace map first and then the naming map; an IRI absent from the second map keeps its unified-namespace name.

## Earlier state and RDF/XML compatibility checks

The state draft's [structural report](../state_goal_extensions_review/structural_validation.json), [query report](../state_goal_extensions_review/query_validation.json), and [Pellet report](../state_goal_extensions_review/pellet_validation.txt) record checks before the namespace migration. The query checks cover 26 parser, positive/negative query, and caller-validation cases; the ChatGPT template was syntax-checked without an LLM invocation. These reports retain their original IRIs and counts.

**RDF/XML serialization order matters for the affected SWRL parser.** Keep `rdf:type` elements first within each resource description. OWLAPI 4.5.29 can otherwise load named rules with empty bodies or heads, causing Pellet to report inconsistency despite an unchanged RDF graph. The [RDF/XML compatibility report](rdfxml_compatibility.md) documents the diagnosis, repair, and checks using the relevant parser and reasoner before the namespace migration. Its hashes, counts, and identifiers describe that corrected snapshot. The draft's earlier Pellet result describes its own loader environment and does not establish compatibility with every Protégé installation.

## Historical repository cleanup verification

[cleanup_verification.json](cleanup_verification.json) records checks on the **4,942-triple source before the state and goal extensions**: the RDF/XML was byte-identical to the prior combined source, contained ten complete SWRL rules, and retained the expected example structure. All nine query files and eight inline Figure 8 queries were executed against that asserted source. The query for inferred Allen relations returned zero rows, as expected without materialized inferences.

Those cleanup checks did not rerun Pellet or OWLAPI, or test a live Protégé or Gruff installation. The model was preserved rather than regenerated at that stage. The report is retained as historical evidence; its byte-identity and triple-count statements do not describe the current extended source.

## Historical checks

| Records | Scope |
|---|---|
| [Figure 8 reports](history/figure8/) | Rule restoration, the synthetic tender execution, temporal regression checks, query results, RDF/XML round trips, and verification of the earlier Protégé export |
| [Method Omega report](history/method_omega/validation_results.json) | The combined 4,942-triple model, methodology structure and queries, preservation of prior data and rules, and reasoning checks |

These JSON files are historical evidence. Their source filenames, absolute scratch paths, counts, ontology and entity IRIs, and references to Turtle files or inference exports describe the environments and versions tested at the time. Those references are not instructions to load another ontology and are not current repository paths or identifiers. The obsolete source snapshots and build/recovery bundles have been removed; the historical reports have not been rewritten to suggest that the original tests were rerun.

The historical RDF/XML/Turtle equivalence checks do not make Turtle a supported editing format for this project. The affected Protégé/OWLAPI route deleted named SWRL rule content when opening and saving Turtle. Maintain the ontology in RDF/XML with the declaration order described in the [compatibility report](rdfxml_compatibility.md); RDF graph equivalence alone does not verify that an OWLAPI loader preserved the rules.

The [plan notes](../docs/figure8_model_notes.md), [execution notes](../docs/figure8_execution.md), and [Method Omega notes](../docs/method_omega_notes.md) explain the modeling assumptions and the limits of the recorded checks. Historical reasoner results and GUI screenshots should not be read as verification of a reader's current installation.

