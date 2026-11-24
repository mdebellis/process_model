# Process model with examples

An ontology for process modeling that combines P-Plan, PROV, OWL-Time, and SWRL rules for Allen interval relations. The combined source includes a collaborative tendering plan, a synthetic execution with timestamps, the Method Omega methodology example, provisional state and goal extensions, and a Customer Portal execution in progress derived from Method Omega.

## Open the ontology

Open [ontologies/process_model_with_examples.rdf](ontologies/process_model_with_examples.rdf) in Protégé, or import it into AllegroGraph. This self-contained RDF/XML file is the **single ontology source**: 7,159 asserted triples, including ten complete SWRL rules. Its ontology label is **Process model with examples**. The ontology IRI is `https://in2use.com/process_model` (no trailing slash); the namespace for all project-owned vocabulary and examples is `https://in2use.com/process_model/`, abbreviated `pm:`. Standard vocabulary IRIs remain unchanged.

The [naming conventions](docs/naming_conventions.md) explain the IRI and label conventions. Earlier migration and identity reports are historical snapshots. The [Customer Portal checks](validation/customer_portal_execution.json) cover the execution addition, preserved original axioms, complete SWRL rules, and Protégé-compatible parsing and reasoning at that revision. The subsequent [parthood checks](validation/parthood_reflexivity.json) cover the current source and the deliberate omission of SULO's global reflexivity axioms for `hasPart` and `isPartOf`; transitivity and inverses remain. See the [parthood notes](validation/README.md#current-parthood-checks) before regenerating inferred data.

**Keep the source in RDF/XML, with `rdf:type` elements first within each resource description.** OWLAPI 4.5.29 can otherwise read named SWRL rules with empty bodies or heads and cause Pellet to report an inconsistency, even when the RDF graph is unchanged. See the [RDF/XML compatibility checks](validation/rdfxml_compatibility.md). Opening and saving the named-rule Turtle representation also deleted SWRL rule content in the affected installation; see the [execution notes](docs/figure8_execution.md#open-the-rdfxml-file-in-protégé).

## Examples and queries

| Example | Documentation | SPARQL queries |
|---|---|---|
| Figure 8 collaborative tendering plan | [Model notes](docs/figure8_model_notes.md) | Included in the model notes |
| Synthetic tender execution and temporal reasoning | [Execution notes](docs/figure8_execution.md) | [Execution queries](queries/figure8_execution/) |
| Method Omega methodology and Customer Portal plan | [SPARQL and Gruff examples](docs/Method_Omega.md), [model notes](docs/method_omega_notes.md) | [Method Omega queries](queries/method_omega/) |
| Customer Portal execution in progress | [Execution walkthrough](docs/Customer_Portal_Execution.md) | [Plan/actual, graph, and timing queries](queries/customer_portal_execution/) |
| State descriptions, goals, and provisional assessments | [State and goal draft](state_goal_extensions_review/README.md) | [State test queries and ChatGPT template](state_goal_extensions_review/queries/) |

The plan examples describe possible work. The tender and Customer Portal executions are synthetic demonstration data. The Customer Portal snapshot is **10 February 2027 at 12:00 UTC-08:00**, within its fictional baseline schedule. It contains six completed and five ongoing step executions; five planned Steps have not started. Early technical design deliberately illustrates a deviation from the plan. The example adds no named graphs or new namespaces and preserves the planned specifications and dates. Customer Portal execution queries assume the reasoner has run and its inferred `hasPart` relationships are visible to the query engine; the Allen table and graph queries also require inferred interval relations. For visualizing those relations, use [05b_actual_allen_graph.rq](queries/customer_portal_execution/05b_actual_allen_graph.rq), which displays one direction from each inverse pair; query 05 retains the full table. Loading SWRL rule definitions alone does not execute them.

[Validation records](validation/README.md) distinguish the current [execution query checks](validation/customer_portal_execution_queries.json) and parthood checks from historical execution-addition, ontology-identity, naming, namespace migration, state extension, RDF/XML compatibility, cleanup, and reasoning checks. Screenshots and the illustrative tender timeline are in [docs/images](docs/images/). Earlier screenshots and reports retain the identifiers used when they were produced.

