# Validation records

The repository has one ontology source: [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf). Validation records document checks on this source and the earlier stages from which it was assembled.

## Repository cleanup verification

[cleanup_verification.json](cleanup_verification.json) records the current cleanup checks: the RDF/XML is byte-identical to the prior combined source, contains 4,942 triples and ten complete SWRL rules, and retains the expected example structure. All nine query files and eight inline Figure 8 queries were executed against the asserted source. The query for inferred Allen relations returned zero rows, as expected without materialized inferences.

These checks did not rerun Pellet or OWLAPI, or test a live Protégé or Gruff installation. The model itself was preserved rather than regenerated.

## Historical checks

| Records | Scope |
|---|---|
| [Figure 8 reports](history/figure8/) | Rule restoration, the synthetic tender execution, temporal regression checks, query results, RDF/XML round trips, and verification of the earlier Protégé export |
| [Method Omega report](history/method_omega/validation_results.json) | The combined 4,942-triple model, methodology structure and queries, preservation of prior data and rules, and reasoning checks |

These JSON files are historical evidence. Their source filenames, absolute scratch paths, counts, and references to Turtle files or inference exports describe the environments and versions tested at the time. Those references are not instructions to load another ontology and are not current repository paths. The obsolete source snapshots and build/recovery bundles have been removed; the historical reports have not been rewritten to suggest that the original tests were rerun.

The historical RDF/XML/Turtle equivalence checks do not make Turtle a supported editing format for this project. The affected Protégé/OWLAPI route deleted named SWRL rule content when opening and saving Turtle; the tested RDF/XML route preserved the complete rules. Maintain the ontology in RDF/XML.

The [plan notes](../docs/figure8_model_notes.md), [execution notes](../docs/figure8_execution.md), and [Method Omega notes](../docs/method_omega_notes.md) explain the modeling assumptions and the limits of the recorded checks. Historical reasoner results and GUI screenshots should not be read as verification of a reader's current installation.
