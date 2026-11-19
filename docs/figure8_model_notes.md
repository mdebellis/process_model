
# Figure 8 collaborative tendering model

## Files and starting point

Open [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf) in Protégé. This is the repository's single, self-contained ontology source. It includes the reusable vocabulary, the Figure 8 plan, its synthetic execution, and Method Omega. It does not require imports, catalog files, or separately opening a schema.

Keep the source in **RDF/XML**. Opening and saving the named-rule Turtle representation in the affected Protégé/OWLAPI installation deleted SWRL rule content; the RDF/XML route preserved it. See the [execution notes](figure8_execution.md#open-the-rdfxml-file-in-protégé) for the tested conditions.

This page explains the Figure 8 **planned workflow**. The [dated execution](figure8_execution.md) is a separate set of synthetic individuals in the same ontology.

- The ontology IRI and namespace for all project-owned vocabulary and examples are `https://in2use.com/process_model/`, abbreviated `pm:` below.
- The ontology label is **Process model with examples**.
- The main plan individual is `pm:TenderingPlan`.

The [namespace migration notes](namespace_migration.md) explain the changes from the earlier supply-chain and Method Omega identifiers. Standard P-Plan, PROV, SULO, and OWL-Time IRIs are unchanged. The reusable role classes are `pm:Partner_Role` and `pm:Lead_Supplier_Role`; the Figure 8 role individuals are `pm:Tendering_Partner_Role` and `pm:Tendering_Lead_Supplier_Role`. Distinct names preserve the distinction between role classes and the contextual roles in this example.

## Source and scope

Kazantsev, DeBellis, Quboa, Sampaio, Mehandjiev and Stalker, An ontology-guided approach to process formation and coordination of demand-driven collaborations, International Journal of Production Research 62(9), 3398-3414 (2024), DOI 10.1080/00207543.2023.2242508. The model follows Figure 8 on printed page 3408 and the accompanying explanation on page 3407.

The plan describes possible work; it does not establish that a real tender, vote, message transmission, or submission occurred. The participant organizations are placeholders for the two lanes, not real companies identified in the paper. The combined ontology also contains a separately identified synthetic execution with illustrative timestamps, described in the [execution notes](figure8_execution.md). Historical Time examples inherited from the reusable base remain present.

## Schema additions

Added five classes: `TaskStep`, `CommunicationStep`, `EventStep`, `StartEventStep`, and `EndEventStep`. The six existing task categories are now also subclasses of `TaskStep`. `TaskStep` and `EventStep` are disjoint; `StartEventStep` and `EndEventStep` are disjoint.

Added `eventForRole` to identify the role whose lane contains an event, and `triggeredByVariable` to identify the planned input whose arrival triggers a start event. A receiving start event does not become a second producer of the incoming document or message.

The original Figure 8 plan additions preserved the ten existing SWRL rules and the underlying P-Plan, PROV, SULO, and Time definitions. Subsequent work restored damaged rule content, completed standard PROV declarations for the execution example, and added missing standard P-Plan terms for Method Omega. The combined source retains dated `skos:changeNote` annotations recording these changes.

## Seven tasks

- `pm:t1CreateTenderDraftTask` - `DraftingStep`, assigned to the lead supplier. Uses the call for tender and produces the initial draft.
- `pm:t2IncorporateInputsTask` - `RevisionStep`, assigned to the lead supplier. Incorporates the partner contribution into a new revised-tender variable. The local identifier corrects the spelling of the incorporation task in the figure.
- `pm:t11SendTenderForVotingTask` - `CommunicationStep`, assigned to the lead supplier. Sends the revised tender for voting and awaits the returning vote.
- `pm:t3SubmitTenderTask` - `SubmissionStep`, assigned to the lead supplier. The approval branch.
- `pm:t13ReplaceSupplierTask` - `PartnerReplacementStep`, assigned to the lead supplier. The rejection branch, described in the paper as inviting an alternative partner.
- `pm:t222MakeInputTask` - `ContributionStep`, assigned to the invited partner. Produces a separate partner contribution.
- `pm:t12VoteForTenderTask` - `ReviewStep`, assigned to the invited partner. Reviews the revised tender and produces the partner decision.

Each task has its own `PlannedAssignment` connecting the task, the placeholder organization, and its contextual role. These are intended assignments, not actual PROV associations or executions.

## Events and control flow

The lead-supplier path starts at `pm:CFT_Received`, proceeds through draft creation, input incorporation, and the send-and-await task, and then branches.

Approval leads to submission and `pm:TenderSubmitted_End`. Rejection leads to supplier replacement and `pm:SupplierReplaced_End`.

The partner path starts at `pm:Draft_Received`, proceeds through contribution and voting, and finishes at `pm:PartnerVote_End`. This participant-specific end is not asserted to end the lead supplier's path.

There are ten explicit `StepTransition` individuals, including two `ConditionalTransition` individuals. `pm:SubmissionChoice` groups the two conditional alternatives after `t11SendTenderForVotingTask`.

The XOR gateway is represented by the `ExclusiveChoice` individual. Its incoming connection is recorded with `choiceAfterStep`; its outgoing branches are the `hasAlternative` links to the two `ConditionalTransitions`.

`ApprovalCondition` checks `PartnerDecisionVar` for `pm:Approved`. `RejectionCondition` checks the same variable for `pm:Rejected`. These outcome-to-branch mappings come from the explanatory text, since the figure itself does not label the branches. The plan describes both alternatives. The separate synthetic execution records an approval decision and a submission; it does not change those planned alternatives. Missing decision information does not select a branch.

The replacement branch ends where Figure 8 ends. No retry loop or additional partner lane has been invented.

## Four message exchanges

- `DraftToPartnerMessageVar`: draft creation to partner input; lead-supplier role to partner role; payload `InitialDraftVar`.
- `ContributionToLeadMessageVar`: partner input to incorporation; partner role to lead-supplier role; payload `PartnerContributionVar`.
- `VotingRequestMessageVar`: send-for-voting to partner vote; lead-supplier role to partner role; payload `RevisedTenderVar`.
- `VoteToLeadMessageVar`: partner vote back to the send-and-await task; partner role to lead-supplier role; payload `PartnerDecisionVar`.

The variables are planned message slots, not actual `Message` instances. `Message` payload links refer to separate planned document or decision variables. In an execution, `Message` and `DocumentVersion` individuals connect to these slots with `p-plan:correspondsToVariable`, as illustrated in the [synthetic execution](figure8_execution.md).

## Resource variables and versions

There are ten variables: five document slots, one decision slot, and four message slots. `CallForTenderVar` is an external input with no producer inside this plan. Every other variable has exactly one asserted producing step.

`InitialDraftVar`, `PartnerContributionVar`, `RevisedTenderVar`, and `SubmittedTenderVar` are distinct. This respects P-Plan's functional `isOutputVarOf` property. The submitted-tender slot is an explicit modeling detail representing the submitted copy or submission artifact; the figure does not name that output slot.

All twelve task/event steps are explicitly different from each other, and the ten variables are explicitly different from each other. This both supports the existing SWRL `differentFrom` conditions and exposes accidental multiple-producer errors.

## Request/reply interpretation

The figure returns the vote message to the same task that sends the tender for voting. Preserving all seven depicted tasks therefore requires treating `t11SendTenderForVotingTask` as a task with a send phase and a wait/receive phase.

At this level, `hasInputVar` records information used during the task; it does not by itself say that every input must exist before the task starts. The returning vote is an input received during that task. A workflow engine that treats every input as a start precondition would need an explicit refinement into separate send and receive steps, or equivalent support for a request/reply task.

Consequently the reasoner correctly derives a resource dependency from `t11` to `t12` and another from `t12` to `t11`. These are request/reply dependencies, not a control-flow loop. No mutual `p-plan:isPrecededBy` assertions are added. The explicit control-flow graph is acyclic.

## Reasoning and historical validation

Use a SWRL-enabled reasoner such as the tested Pellet configuration to obtain the inferred resource links. The combined RDF/XML source contains asserted data and rules, without materialized inference output.

The following findings record the original Figure 8 validation. The repository cleanup has separate [verification records](../validation/README.md); it does not constitute a new Pellet run.

Pellet classification found no inconsistencies or unsatisfiable named classes in either the updated schema or the worked example.

The Figure 8 example yields ten directed `hasFlowDependency` links and ten directed `sharesInputVariable` links, matching the explicitly checked expectations. Shared input does not by itself imply resource contention or an exclusive choice.

Checks cover the seven task assignments, five events, ten control transitions, four message exchanges, correct message roles and payloads, explicit approval/rejection conditions, single producers, and the separation of planned elements from actual executions and artifacts. Separate test fixtures confirmed that reusing the initial-draft output variable for two distinct producers is inconsistent, and that a task cannot also be a planned event.

Guard queries on separate test data matched approval to submission, rejection to replacement, and missing decision information to no branch. This demonstrates how to consult the conditions; it does not turn the ontology into an executable workflow engine.

The inherited regression tests also passed: 31 PROV type entailments, qualified associations, prior resource-dependency controls, and 484 interval-pair comparisons covering all thirteen Allen relations. Separate regression fixtures and materialized inferred triples are excluded from the source. The synthetic tender execution described elsewhere is included.

## Useful SPARQL queries

Originally prepared 4 November 2026 for the Figure 8 demonstration in AllegroGraph/Gruff; the query text below now uses the unified `pm:` namespace. The screenshots are historical captures and may show earlier IRIs or prefix names.

The table and graph queries below work directly on the asserted content of [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf); no prior SWRL execution or materialization is required. They are scoped to `pm:TenderingPlan`.

Use the `SELECT` variants for tables. Use the `CONSTRUCT` variants for visual graphs: run the query in Gruff, then choose **Create Visual Graph**. A `CONSTRUCT` returns a graph for browsing; it does not insert those triples into the repository. These instructions target Gruff connected directly to AllegroGraph, as in the demonstration, rather than its generic SPARQL-endpoint mode.

Gruff has to reconstruct related triples from a `SELECT` result. Returning only labels can therefore produce a valid table with nothing to graph. Including entity IRIs helps, but the explicit graph variants specify exactly which links should be displayed. See [Gruff 9.0.2 query documentation](https://franz.com/agraph/support/documentation/9.0.2/gruff.html).

### 1. Task assignments

**1a — Table: seven assignments.** The assignment individual is now included so the result retains the connection between each task, agent, and role.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?assignment ?task ?label ?agent ?role WHERE {
  ?task pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?label.
  ?assignment pm:assignmentForStep ?task;
              pm:assignedAgent ?agent;
              pm:assignedRole ?role.
}
ORDER BY ?task
```
<img width="1122" height="649" alt="task_assignments_1a" src="https://github.com/user-attachments/assets/aa0a8f37-4341-419e-92b6-4a195234732a" />
Figure 1a. Gruff Visualization of Query 1a



**1b — Graph: tasks, assignments, agents, and roles.** This includes the assignment nodes and their three links, rather than showing only tasks linked to the plan. The two organizations remain illustrative placeholders, as described above.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?assignment pm:assignmentForStep ?task;
              pm:assignedAgent ?agent;
              pm:assignedRole ?role;
              rdfs:label ?assignmentLabel.
  ?task pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?label.
  ?agent rdfs:label ?agentLabel.
  ?role rdfs:label ?roleLabel.
  pm:TenderingPlan rdfs:label ?planLabel.
} WHERE {
  ?task pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?label.
  ?assignment pm:assignmentForStep ?task;
              pm:assignedAgent ?agent;
              pm:assignedRole ?role.
  OPTIONAL { ?assignment rdfs:label ?assignmentLabel. }
  OPTIONAL { ?agent rdfs:label ?agentLabel. }
  OPTIONAL { ?role rdfs:label ?roleLabel. }
  OPTIONAL { pm:TenderingPlan rdfs:label ?planLabel. }
}
```
<img width="1056" height="703" alt="task_assignments_1b" src="https://github.com/user-attachments/assets/2b10d129-63ce-4e1d-9967-0953fc8fda1e" />
Figure 1b. Gruff Visualization of Query 1b



### 2. Control transitions and branch conditions

**2a — Table: ten transitions.** Returns the transition and endpoint IRIs alongside their labels. Two rows have outcomes: approval leads to submission and rejection leads to replacement. The other eight rows have no condition/outcome binding because those transitions are unconditional.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?transition ?from ?fromLabel ?to ?toLabel ?condition ?outcome WHERE {
  ?transition pm:transitionFrom ?from; pm:transitionTo ?to.
  ?from pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?fromLabel.
  ?to pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?toLabel.
  OPTIONAL {
    ?transition pm:hasCondition ?condition.
    ?condition pm:expectedOutcome ?outcome.
  }
}
ORDER BY ?fromLabel ?toLabel
```
<img width="1907" height="720" alt="control_trasitions_2a1" src="https://github.com/user-attachments/assets/24a1f81e-4741-4003-9768-6160b0f35909" />
Figure 2a. Gruff Visualization of Query 2a.



**2b — Graph: the ten transition individuals and their endpoints, plus the two branch conditions.** The transition is a node with `transitionFrom` and `transitionTo` links. These links both originate at the transition node; follow their predicate names to distinguish the source and target steps. The graph preserves the ontology's actual representation instead of inventing a direct step-to-step control predicate. The outcomes describe alternatives in the plan, not votes that have actually occurred.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?transition pm:transitionFrom ?from;
              pm:transitionTo ?to;
              pm:hasCondition ?condition;
              rdfs:label ?transitionLabel.
  ?from rdfs:label ?fromLabel.
  ?to rdfs:label ?toLabel.
  ?condition pm:expectedOutcome ?outcome; rdfs:label ?conditionLabel.
  ?outcome rdfs:label ?outcomeLabel.
} WHERE {
  ?transition pm:transitionFrom ?from; pm:transitionTo ?to.
  ?from pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?fromLabel.
  ?to pp:isStepOfPlan pm:TenderingPlan; rdfs:label ?toLabel.
  OPTIONAL {
    ?transition pm:hasCondition ?condition.
    ?condition pm:expectedOutcome ?outcome.
    OPTIONAL { ?condition rdfs:label ?conditionLabel. }
    OPTIONAL { ?outcome rdfs:label ?outcomeLabel. }
  }
  OPTIONAL { ?transition rdfs:label ?transitionLabel. }
}
```
<img width="1903" height="690" alt="control_trasitions_2b" src="https://github.com/user-attachments/assets/e8e52dd6-516c-49c5-a69d-1a97015986bb" />
Figure 2b. Results of SPARQL Query 2b.



### 3. Resource-flow dependencies without prior reasoning

The original third query selected `pm:hasFlowDependency` triples. That property is declared and appears in a SWRL rule head, but the asserted ontology contains **zero uses of it as a predicate**. Importing rule definitions is not the same as executing the rules or loading their inferred results. A zero-row result, or Gruff's warning that no triples use this predicate, is therefore expected on the asserted graph.

For this demonstration, calculate the dependencies at query time by joining a producer's `pp:hasOutputVar` with a consumer's `pp:hasInputVar` for the same variable. Both steps must belong to the Figure 8 plan.

**3a — Table: ten distinct producer/consumer pairs.**

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?producer ?consumer WHERE {
  ?producer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
}
ORDER BY ?producer ?consumer
```

This reproduces the ten expected dependency pairs for this Figure 8 dataset. Its steps are explicitly different individuals and are CollaborationSteps through their declared types and subclass hierarchy. The `!=` filter compares RDF terms; it is not a general replacement for OWL/SWRL distinctness reasoning on arbitrary ontologies.

**3b — Graph: ten derived dependency edges.** The `WHERE` clause reads the asserted output/input links, so it does not require pre-existing `hasFlowDependency` triples. The `CONSTRUCT` presents those calculated links under the existing `pm:hasFlowDependency` property. They are query results, not changes to the stored ontology.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?producer pm:hasFlowDependency ?consumer;
            rdfs:label ?producerLabel.
  ?consumer rdfs:label ?consumerLabel.
} WHERE {
  ?producer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
  OPTIONAL { ?producer rdfs:label ?producerLabel. }
  OPTIONAL { ?consumer rdfs:label ?consumerLabel. }
}
```
<img width="1159" height="529" alt="derived_dependency_edges_3b" src="https://github.com/user-attachments/assets/7c6e445b-19ef-40bd-803e-6e2678c28d37" />
Figure 3b. Visualization of Query 3b.



The two opposite dependencies between the send-and-await task and the voting task are intentional: one carries the voting request and the other carries the reply. They are resource dependencies, not a control-flow loop or a requirement that each task finish before the other starts.

**3c — Explanation table: which variable establishes each dependency?** Returns twelve rows supporting the ten distinct pairs. Two pairs each share both a document variable and a message variable, so `DISTINCT` on the producer/consumer pair in 3a is intentional.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?producer ?consumer ?variable WHERE {
  ?producer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan pm:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
}
ORDER BY ?producer ?consumer ?variable
```

### Optional: query stored or reasoner-visible dependency triples

The original third query remains useful after inferred dependency assertions have been exported and loaded, materialized by an appropriate rule translation, or otherwise made visible to the query engine. Merely running a reasoner in a separate Protégé session does not make its inferences available in AllegroGraph.

**Expected on the supplied asserted file: zero rows.** This query is a check for available dependency triples, not the recommended first-use demonstration query.

```sparql
PREFIX pm: <https://in2use.com/process_model/>
PREFIX pp: <http://purl.org/net/p-plan#>
SELECT ?producer ?consumer WHERE {
  ?producer pp:isStepOfPlan pm:TenderingPlan;
            pm:hasFlowDependency ?consumer.
}
ORDER BY ?producer ?consumer
```

### Historical query verification on 4 November 2026

The earlier versions of all eight SPARQL blocks in this section were executed with RDFLib against the GitHub `supply_chain_figure8.ttl` retrieved on 4 November 2026, using the namespaces in that source. The original three queries returned 7, 10, and 0 rows, reproducing the reported behavior. The replacement dependency query matched all ten independently enumerated expected pairs from the original Figure 8 validation, including the request/reply pair in both directions. The graph versions were checked for their assignment, transition, condition, and dependency edges; the source graph remained unchanged.

| Query | Verified result |
|---|---|
| 1a | 7 assignment rows |
| 1b | 47 triples, including all 7 assignment nodes and their task/agent/role links |
| 2a | 10 transition rows, including 2 conditional outcomes |
| 2b | 50 triples, including all 10 transitions and both branch conditions |
| 3a | 10 distinct dependency pairs |
| 3b | 17 triples: 10 dependency edges and 7 task labels |
| 3c | 12 producer/consumer/variable rows |
| Optional stored-triple query | 0 rows before inference output is made available |

These historical checks tested SPARQL results and graph structure; they were not a new Pellet validation or a claim that the queries had run in a live Gruff/AllegroGraph repository. The [validation overview](../validation/README.md) distinguishes those earlier records from the [namespace migration checks](../validation/namespace_migration.json). The ontology-validation results above remain the record of the original implementation.

The namespace migration checks reran all eight current snippets against the 5,299-triple source. Their result sizes match the table above. After applying the IRI mapping, the results are unchanged except for the two deliberately updated role labels displayed by query 1b: **Tendering Lead Supplier Role** and **Tendering Partner Role**.


