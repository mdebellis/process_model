# Validation records

The repository has one ontology source: [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf). Validation records document checks on this source and the earlier stages from which it was assembled.

## Current source and namespace migration

The current ontology contains **5,299 asserted triples**, including ten complete SWRL rules and the [state and goal extensions](../state_goal_extensions_review/README.md). Its ontology IRI and project-owned term namespace are `https://in2use.com/process_model/`. The [namespace migration notes](../docs/namespace_migration.md) explain the identifier changes; [namespace_migration.json](namespace_migration.json) records the checks on the migrated source. The increase from 5,294 triples consists of four role preferred labels and one migration change note.

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
