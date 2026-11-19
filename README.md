# Process model

An ontology for process modeling that combines P-Plan, PROV, OWL-Time, and SWRL rules for Allen interval relations. The combined source includes a collaborative tendering plan, a synthetic execution with timestamps, the Method Omega methodology example, and provisional state and goal extensions.

## Open the ontology

Open [ontologies/process_model_with_examples.rdf](ontologies/process_model_with_examples.rdf) in Protégé, or import it into AllegroGraph. This self-contained RDF/XML file is the **single ontology source**: 5,294 asserted triples, including ten complete SWRL rules. Existing ontology, vocabulary, and individual IRIs are preserved.

**Keep the source in RDF/XML, with `rdf:type` elements first within each resource description.** OWLAPI 4.5.29 can otherwise read named SWRL rules with empty bodies or heads and cause Pellet to report an inconsistency, even when the RDF graph is unchanged. See the [RDF/XML compatibility checks](validation/rdfxml_compatibility.md). Opening and saving the named-rule Turtle representation also deleted SWRL rule content in the affected installation; see the [execution notes](docs/figure8_execution.md#open-the-rdfxml-file-in-protégé).

## Examples and queries

| Example | Documentation | SPARQL queries |
|---|---|---|
| Figure 8 collaborative tendering plan | [Model notes](docs/figure8_model_notes.md) | Included in the model notes |
| Synthetic tender execution and temporal reasoning | [Execution notes](docs/figure8_execution.md) | [Execution queries](queries/figure8_execution/) |
| Method Omega hierarchy, conditions, and rework | [Method Omega notes](docs/method_omega_notes.md) | [Method Omega queries](queries/method_omega/) |
| State descriptions, goals, and provisional assessments | [State and goal draft](state_goal_extensions_review/README.md) | [State test queries and ChatGPT template](state_goal_extensions_review/queries/) |

The plan examples describe possible work. The tender execution is synthetic demonstration data. Queries generally operate on asserted data; the execution query for Allen relations requires reasoner results made available to the query engine. Loading SWRL rule definitions alone does not execute them.

[Validation records](validation/README.md) distinguish the state extension and RDF/XML compatibility checks from historical cleanup, reasoning, and parser checks. Screenshots and the illustrative tender timeline are in [images](images/).
