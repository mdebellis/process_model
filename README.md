# Process model with examples

An ontology for process modeling that combines P-Plan, PROV, OWL-Time, and SWRL rules for Allen interval relations. The combined source includes a collaborative tendering plan, a synthetic execution with timestamps, the Method Omega methodology example, and provisional state and goal extensions.

## Open the ontology

Open [ontologies/process_model_with_examples.rdf](ontologies/process_model_with_examples.rdf) in Protégé, or import it into AllegroGraph. This self-contained RDF/XML file is the **single ontology source**: 5,506 asserted triples, including ten complete SWRL rules. Its ontology label is **Process model with examples**. The ontology IRI is `https://in2use.com/process_model` (no trailing slash); the namespace for all project-owned vocabulary and examples is `https://in2use.com/process_model/`, abbreviated `pm:`. The current version is `process-model-v4-2026-11-18`. Standard vocabulary IRIs remain unchanged.

The [naming conventions](docs/naming_conventions.md) describe the current ontology identity, entity names, and labels. The [naming map](docs/naming_migration.tsv) records the earlier 175 entity renames. Current [structural and query checks](validation/ontology_identity.json) and [reasoning checks](validation/ontology_identity_reasoning.json) cover the corrected ontology IRI and its definition references. Entity IRIs and query text are unchanged by this correction. Clients using identifiers from before namespace unification need to apply the earlier [namespace map](docs/iri_migration.tsv), then the naming map, and the exact ontology-identity correction described in the naming guide.

**Keep the source in RDF/XML, with `rdf:type` elements first within each resource description.** OWLAPI 4.5.29 can otherwise read named SWRL rules with empty bodies or heads and cause Pellet to report an inconsistency, even when the RDF graph is unchanged. See the [RDF/XML compatibility checks](validation/rdfxml_compatibility.md). Opening and saving the named-rule Turtle representation also deleted SWRL rule content in the affected installation; see the [execution notes](docs/figure8_execution.md#open-the-rdfxml-file-in-protégé).

## Examples and queries

| Example | Documentation | SPARQL queries |
|---|---|---|
| Figure 8 collaborative tendering plan | [Model notes](docs/figure8_model_notes.md) | Included in the model notes |
| Synthetic tender execution and temporal reasoning | [Execution notes](docs/figure8_execution.md) | [Execution queries](queries/figure8_execution/) |
| Method Omega hierarchy, conditions, and rework | [Method Omega notes](docs/method_omega_notes.md) | [Method Omega queries](queries/method_omega/) |
| State descriptions, goals, and provisional assessments | [State and goal draft](state_goal_extensions_review/README.md) | [State test queries and ChatGPT template](state_goal_extensions_review/queries/) |

The plan examples describe possible work. The tender execution is synthetic demonstration data. Queries generally operate on asserted data; the execution query for Allen relations requires reasoner results made available to the query engine. Loading SWRL rule definitions alone does not execute them.

[Validation records](validation/README.md) distinguish the current ontology-identity checks from earlier naming, namespace migration, state extension, RDF/XML compatibility, cleanup, and reasoning checks. Screenshots and the illustrative tender timeline are in [docs](docs/). Earlier screenshots and reports retain the identifiers used when they were produced.
