# Process model with examples

An ontology for process modeling that combines P-Plan, PROV, OWL-Time, and SWRL rules for Allen interval relations. The combined source includes a collaborative tendering plan, a synthetic execution with timestamps, the Method Omega methodology example, provisional state and goal extensions, a Customer Portal execution in progress derived from Method Omega, and a B2B lavatory collaboration with goals, preconditions, postconditions, and execution evidence.

## Validation

The [client relationship checks](validation/client_relationship_checks.json) and
[current reasoning report](validation/client_relationship_reasoning.json)
cover the current 9,336-triple source. The shared `has_client` property identifies
**Northstar Retail** as the fictional Customer Portal client and the existing
**Aerospace Customer** as the lavatory collaboration client. Its inverse is
`is_client_of`; both client individuals are `prov:Organization` instances.

The [Customer Portal checks](validation/customer_portal_execution.json) cover the execution addition, preserved original axioms, complete SWRL rules, and Protégé-compatible parsing and reasoning at that revision. The subsequent [parthood checks](validation/parthood_reflexivity.json) cover the preceding 7,159-triple source and the deliberate omission of SULO's global reflexivity axioms for `hasPart` and `isPartOf`; transitivity and inverses remain. See the [parthood notes](validation/README.md#parthood-checks-before-the-b2b-addition) before regenerating inferred data.

**Keep the source in RDF/XML, with `rdf:type` elements first within each resource description.** OWLAPI 4.5.29 can otherwise read named SWRL rules with empty bodies or heads and cause Pellet to report an inconsistency, even when the RDF graph is unchanged. See the [RDF/XML compatibility checks](validation/rdfxml_compatibility.md). Opening and saving the named-rule Turtle representation also deleted SWRL rule content in the affected installation; see the [execution notes](docs/figure8_execution.md#open-the-rdfxml-file-in-protégé).

## Examples and queries

| Example | Documentation | SPARQL queries |
|---|---|---|
| Figure 8 collaborative tendering plan | [Model notes](docs/figure8_model_notes.md) | Included in the model notes |
| Synthetic tender execution and temporal reasoning | [Execution notes](docs/figure8_execution.md) | [Execution queries](queries/figure8_execution/) |
| Method Omega methodology and Customer Portal plan | [SPARQL and Gruff examples](docs/Method_Omega.md), [model notes](docs/method_omega_notes.md) | [Method Omega queries](queries/method_omega/) |
| Customer Portal execution in progress | [Execution walkthrough](docs/Customer_Portal_Execution.md) | [Plan/actual, graph, and timing queries](queries/customer_portal_execution/) |
| B2B lavatory collaboration: methodology, plan, and execution | [B2B walkthrough](docs/B2B_Collaboration.md) | [Goal, condition, execution, and state-test queries](queries/b2b_collaboration/) |
| State descriptions, goals, and provisional assessments | [State and goal draft](state_goal_extensions_review/README.md) | [State test queries and ChatGPT template](state_goal_extensions_review/queries/) |

The plan examples describe possible work. The tender and Customer Portal executions are synthetic demonstration data. The Customer Portal snapshot is **10 February 2027 at 12:00 UTC-08:00**, within its fictional baseline schedule. It contains six completed and five ongoing step executions; five planned Steps have not started. Early technical design deliberately illustrates a deviation from the plan. The example adds no named graphs or new namespaces and preserves the planned specifications and dates. Customer Portal execution queries assume the reasoner has run and its inferred `hasPart` relationships are visible to the query engine; the Allen table and graph queries also require inferred interval relations. For visualizing those relations, use [05b_actual_allen_graph.rq](queries/customer_portal_execution/05b_actual_allen_graph.rq), which displays one direction from each inverse pair; query 05 retains the full table. Loading SWRL rule definitions alone does not execute them.

The B2B example separates collaboration-design decisions T1–T5 from the resulting operational workflow. Its fictional snapshot is **4 March 2027 at 12:00 UTC**. A frame is manufactured, then transferred to the assembler; explicit receipt evidence changes assembly readiness. Ten SPARQL state tests and eight synthetic assessment records demonstrate the distinction. See the [walkthrough](docs/B2B_Collaboration.md) for the complete-evidence assumptions and the boundary of this first example.

**Reload and reason over the updated source for the B2B example.** The repository’s older `ontologies/process_model_inferred_axioms.rdf` has not been regenerated and does not include this addition; regenerate your inference export from the current source.

[Validation records](validation/README.md) include the current client and B2B [query checks](validation/b2b_collaboration_queries.json), the B2B addition's [reasoning](validation/b2b_collaboration_reasoning.json) and [preservation](validation/b2b_collaboration_preservation.json) reports, and earlier execution, parthood, naming, namespace, and RDF/XML checks. Screenshots and the illustrative tender timeline are in [docs/images](docs/images/). Earlier screenshots and reports retain the identifiers used when they were produced.

