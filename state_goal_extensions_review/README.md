# State and goal extensions — first draft

18 November 2026

Open [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf) in Protégé. It is the complete updated
ontology, including the existing tendering, Method Omega and OWL-Time examples.
Use the corrected type-first RDF/XML serialization described in the
[compatibility report](../validation/rdfxml_compatibility.md). The original
draft's export triggered a Protégé/OWLAPI parser issue despite passing the
earlier CLI checks. The review archive
contains additions-only Turtle, query examples, a small invocation helper and
validation results; it does not contain another copy of the complete ontology.

## Scope of this draft

The eventual language for describing states is deliberately undecided. SPARQL
is the provisional executable representation. A future higher-level language,
including the discussed Manchester Syntax extension, can replace or generate
tests without changing the identity of state descriptions or goals.

All project-owned vocabulary and example individuals now use
`https://in2use.com/process_model/`, abbreviated `pm:`. This is also the ontology
IRI; its label is **Process model with examples**. The later
[namespace migration](../docs/namespace_migration.md) updated the draft's local
IRIs and query text while preserving standard vocabulary IRIs. The original
validation reports retain the identifiers used when they were produced; the
[migration report](../validation/namespace_migration.json) covers the current source.

The supplied baseline contained 4,942 asserted triples but no State_Description
or has_sub_state declarations. The state draft supplied those foundations and
contained 5,294 triples before namespace migration. The current ontology contains
5,299 asserted triples. The five additional triples are four role preferred
labels and one migration change note. No inferred triples or runtime evaluation records have
been added.

## Vocabulary

| Class | Meaning |
|---|---|
| State_Description | A description of a condition; it does not assert that the condition holds. |
| Goal | A State_Description specifying a condition to achieve or maintain. |
| State_Test | A reusable assessment specification with provisional SPARQL text. |
| Evaluation_Method | The method determining satisfaction, independently of its invocation interface. |
| State_Evaluation | An assessment **record**, aligned to PROV Entity and SULO InformationObject; not an execution Activity. |
| Evaluation_Result | A controlled category describing the outcome of an evaluation. |

`has_sub_goal` is a subproperty of `has_sub_state`, with Goal domain and range.
The decomposition properties do not by themselves specify AND/OR semantics,
transitivity, execution order, or goal satisfaction. The parent test supplies
the satisfaction criterion. `has_goal` links a Plan or Step to a Goal.

`has_state_test` links a state description to its test. Tests have
`has_evaluation_method` and optional `has_sparql_query` values. There are two
initial methods: **SPARQL_Evaluation** and **ChatGPT_Evaluation**. A SELECT query
that calls ChatGPT is still ChatGPT evaluation.

An evaluation record can be linked through `has_state_evaluation`, and identify
its applied test, evaluated execution and entities, evidence, result, time,
context, explanation, actual evaluator identifier and raw response. The result
individuals are **Satisfied**, **Unsatisfied**, **Unknown** and
**Evaluation_Error**. Evaluation_Error is a technical failure, not a truth value.
None of these records is generated merely by asserting ontology relationships.

Classes and individuals use Title_Case with underscores; properties use
lower_case with underscores. Every new object property has a `has_…` primary
direction and an `is_…_of` inverse. Domain, range and owl:inverseOf declarations
appear on the primary side. English rdfs:label and skos:prefLabel values replace
underscores with spaces. Classes remain primitive; no new equivalence,
disjointness or functional-property constraints were introduced.

## Connection to the existing examples

The existing supply-chain DecisionCondition class is now a subclass of
State_Description, retaining its original parents. Its four existing individuals
have English skos:definition values. The namespace migration updates their IRIs;
their outcomes and branch meanings remain unchanged. A missing decision still
does not mean rejection.

The illustrative **Approved_Tender_Submitted** goal has **Tender_Approved** and
**Tender_Submitted** subgoals. Three ASK tests assess the selected execution and
selected document version. The parent also requires the submission to have used
the actual approval decision about that version. Two separately satisfied
subgoals alone do not guarantee this additional link.

For Method Omega, **Requirements_Ready_For_Review** is a proposed qualitative goal
for Create Detailed Requirements. Its assessment checks the supplied wireframes
and use cases for clarity, consistency and sufficient detail for review. This is
an illustrative addition, not a requirement claimed to appear in the source
diagram or paper. It is separate from the existing formal approval decision.

Every state individual, including the four legacy conditions, has an English
natural-language definition. The legacy conditions retain their existing
declarative representation; this draft does not give all of them executable tests.

## Running the deterministic examples

The three concrete files in `queries/` contain explicit VALUES for TenderRun01
and Run01RevisedTender. Each returns true against the complete updated ontology
with an RDFLib SPARQL processor. They are ordinary SPARQL queries suitable for
testing in AllegroGraph as well; no AllegroGraph server execution was performed
in this review.

The query strings stored on State_Test deliberately omit the concrete VALUES.
The caller **must** supply both `run` and `version`. These are the selected inputs,
not a request to discover the globally latest document version. SPARQL graph
patterns can bind omitted variables themselves, so caller validation is essential.
`query_examples.py` demonstrates explicit IRI validation and RDFLib initial
bindings before execution. It returns a raw ASK result, not an automatic workflow
decision. For AllegroGraph, apply the equivalent client bindings or explicit VALUES.

ASK false means no matching pattern in the selected dataset. Map it to Unsatisfied
only if the relevant records are complete and unambiguous under the test's stated
interpretation. Otherwise use Unknown. Check material conflicts separately; these
positive-pattern examples do not establish vote unanimity, absence of revocation,
or workflow timing compliance. Query failures are Evaluation_Error. A false or
failed query does not automatically trigger an LLM fallback.

## ChatGPT assessment template

`queries/chatgpt_requirements_readiness_template.rq` selects one explicit state
and test. Bind `evidence_text` and `context_text` as string literals before running
it. Supply actual document contents or excerpts with evidence identifiers, version
identifiers, the relevant execution and project expectations. The ontology contains
planned document slots, not those documents or a Method Omega execution.

The query reads the state's definition and the test's criteria and calls the
documented AllegroGraph `llm:response` **function**, which returns one text response.
It requests JSON containing `result`, `explanation`, and `evidence_references`.
The caller must validate that response and map the permitted result names to the
corresponding individuals. Malformed or unusable output is Evaluation_Error;
insufficient evidence is Unknown. ASK over the existence of an LLM response would
not test whether the model answered Satisfied.

This uses the configured OpenAI model through AllegroGraph. Record the actual
model identifier; a ChatGPT evaluation label does not identify a particular model
or reuse a ChatGPT web session. No API key or fixed model identifier is embedded.
No LLM invocation was made during validation.

Documentation checked:
- [AllegroGraph LLM examples](https://franz.com/agraph/support/documentation/llm-examples.html)
- [AllegroGraph LLM magic properties](https://franz.com/agraph/support/documentation/magic-properties.html)

## Validation

The checks below describe the initial draft validation before namespace migration. The
[RDF/XML compatibility regression](../validation/rdfxml_compatibility.md)
additionally reproduces the reported Protégé inconsistency and verifies the
corrected serialization with OWLAPI 4.5.29 and the official Pellet plug-in. Both
sets of reports describe the earlier IRIs. See the [namespace migration
results](../validation/namespace_migration.json) for checks on the current source.

- RDF/XML parsing and isomorphic roundtrip: passed.
- Existing named assertions and anonymous structures preserved, except updated
  ontology modified date and versionInfo; two explanatory ontology notes added.
- All ten SWRL rules structurally preserved.
- Naming, English labels and inverse-property conventions: passed for 49 new terms.
- Expected Goal/subgoal entailments and absence of converse inferences: passed.
- English definitions present for all eight state individuals.
- All 26 parser, positive/negative query and caller-validation checks: passed.
- Full Pellet consistency: **Consistent: Yes**; classification completed with no
  named unsatisfiable classes reported, using the OWLAPIv3 loader.
- ChatGPT template: syntax parsed only; vendor function execution remains to be
  tested on a configured AllegroGraph server with actual evidence.

Machine-readable reports and the Pellet report are included. The query regressions
can be repeated with RDFLib using `validate_queries.py` and the path to the complete
updated RDF file. These examples specify and test conditions; they do not implement
a workflow engine or automatically execute processes.
