# Figure 8 collaborative tendering model

## Files and starting point

Replace `supply_chain_model.ttl` with the updated schema. Add `supply_chain_figure8.ttl` as a new worked example. The basic `process_model.ttl` is unchanged by this modeling work.

Open `supply_chain_figure8.ttl` directly in Protege. It is self-contained: it includes the corrected base, the supply-chain vocabulary, and the Figure 8 individuals. It does not require imports, catalog files, or separately opening the schema first.

- The example ontology IRI is `https://www.michaeldebellis.com/supply_chain_figure8`
- The example namespace, abbreviated fig8 below, is `https://www.michaeldebellis.com/supply_chain_figure8/`
- The main plan individual is `fig8:TenderingPlan`.
- The reusable vocabulary namespace, abbreviated sc, is `https://www.michaeldebellis.com/supply_chain_model/`

## Source and scope

Kazantsev, DeBellis, Quboa, Sampaio, Mehandjiev and Stalker, An ontology-guided approach to process formation and coordination of demand-driven collaborations, International Journal of Production Research 62(9), 3398-3414 (2024), DOI 10.1080/00207543.2023.2242508. The model follows Figure 8 on printed page 3408 and the accompanying explanation on page 3407.

This is the planned workflow. The model does not claim that a particular execution, vote, message transmission, or tender submission occurred. The participant organizations are placeholders for the two lanes, not real companies identified in the paper. There are no invented execution timestamps. The historical Time examples inherited from the reusable base remain present.

## Schema additions

Added five classes: `TaskStep`, `CommunicationStep`, `EventStep`, `StartEventStep`, and `EndEventStep`. The six existing task categories are now also subclasses of `TaskStep`. `TaskStep` and `EventStep` are disjoint; `StartEventStep` and `EndEventStep` are disjoint.

Added `eventForRole` to identify the role whose lane contains an event, and `triggeredByVariable` to identify the planned input whose arrival triggers a start event. A receiving start event does not become a second producer of the incoming document or message.

The schema's ten existing SWRL rules are unchanged. The underlying P-Plan, PROV, SULO, and Time definitions are unchanged. Both the updated schema and the worked example have dated `skos:changeNote` annotations identifying ChatGPT.

## Seven tasks

- `fig8:t1CreateTenderDraftTask` - `DraftingStep`, assigned to the lead supplier. Uses the call for tender and produces the initial draft.
- `fig8:t2IncorporateInputsTask` - `RevisionStep`, assigned to the lead supplier. Incorporates the partner contribution into a new revised-tender variable. The local identifier corrects the spelling of the incorporation task in the figure.
- `fig8:t11SendTenderForVotingTask` - `CommunicationStep`, assigned to the lead supplier. Sends the revised tender for voting and awaits the returning vote.
- `fig8:t3SubmitTenderTask` - `SubmissionStep`, assigned to the lead supplier. The approval branch.
- `fig8:t13ReplaceSupplierTask` - `PartnerReplacementStep`, assigned to the lead supplier. The rejection branch, described in the paper as inviting an alternative partner.
- `fig8:t222MakeInputTask` - `ContributionStep`, assigned to the invited partner. Produces a separate partner contribution.
- `fig8:t12VoteForTenderTask` - `ReviewStep`, assigned to the invited partner. Reviews the revised tender and produces the partner decision.

Each task has its own `PlannedAssignment` connecting the task, the placeholder organization, and its contextual role. These are intended assignments, not actual PROV associations or executions.

## Events and control flow

The lead-supplier path starts at `fig8:CFT_Received`, proceeds through draft creation, input incorporation, and the send-and-await task, and then branches.

Approval leads to submission and `fig8:TenderSubmitted_End`. Rejection leads to supplier replacement and `fig8:SupplierReplaced_End`.

The partner path starts at `fig8:Draft_Received`, proceeds through contribution and voting, and finishes at `fig8:PartnerVote_End`. This participant-specific end is not asserted to end the lead supplier's path.

There are ten explicit `StepTransition` individuals, including two `ConditionalTransition` individuals. `fig8:SubmissionChoice` groups the two conditional alternatives after `t11SendTenderForVotingTask`.

The XOR gateway is represented by the `ExclusiveChoice` individual. Its incoming connection is recorded with `choiceAfterStep`; its outgoing branches are the `hasAlternative` links to the two `ConditionalTransitions`.

`ApprovalCondition` checks `PartnerDecisionVar` for `sc:Approved`. `RejectionCondition` checks the same variable for `sc:Rejected`. These outcome-to-branch mappings come from the explanatory text, since the figure itself does not label the branches. Neither outcome is asserted for an actual decision in the delivered plan. Missing decision information does not select a branch.

The replacement branch ends where Figure 8 ends. No retry loop or additional partner lane has been invented.

## Four message exchanges

- `DraftToPartnerMessageVar`: draft creation to partner input; lead-supplier role to partner role; payload `InitialDraftVar`.
- `ContributionToLeadMessageVar`: partner input to incorporation; partner role to lead-supplier role; payload `PartnerContributionVar`.
- `VotingRequestMessageVar`: send-for-voting to partner vote; lead-supplier role to partner role; payload `RevisedTenderVar`.
- `VoteToLeadMessageVar`: partner vote back to the send-and-await task; partner role to lead-supplier role; payload `PartnerDecisionVar`.

The variables are planned message slots, not actual `Message` instances. `Message` payload links refer to separate planned document or decision variables. For a later execution, actual `Message` and `DocumentVersion` individuals can be connected to these slots with `p-plan:correspondsToVariable`.

## Resource variables and versions

There are ten variables: five document slots, one decision slot, and four message slots. `CallForTenderVar` is an external input with no producer inside this plan. Every other variable has exactly one asserted producing step.

`InitialDraftVar`, `PartnerContributionVar`, `RevisedTenderVar`, and `SubmittedTenderVar` are distinct. This respects P-Plan's functional `isOutputVarOf` property. The submitted-tender slot is an explicit modeling detail representing the submitted copy or submission artifact; the figure does not name that output slot.

All twelve task/event steps are explicitly different from each other, and the ten variables are explicitly different from each other. This both supports the existing SWRL `differentFrom` conditions and exposes accidental multiple-producer errors.

## Request/reply interpretation

The figure returns the vote message to the same task that sends the tender for voting. Preserving all seven depicted tasks therefore requires treating `t11SendTenderForVotingTask` as a task with a send phase and a wait/receive phase.

At this level, `hasInputVar` records information used during the task; it does not by itself say that every input must exist before the task starts. The returning vote is an input received during that task. A workflow engine that treats every input as a start precondition would need an explicit refinement into separate send and receive steps, or equivalent support for a request/reply task.

Consequently the reasoner correctly derives a resource dependency from `t11` to `t12` and another from `t12` to `t11`. These are request/reply dependencies, not a control-flow loop. No mutual `p-plan:isPreceededBy` assertions are added. The explicit control-flow graph is acyclic.

## Reasoning and validation

Use a SWRL-enabled reasoner such as the tested Pellet configuration to obtain the inferred resource links. The delivered Turtle files contain asserted source data and rules, not materialized inference output.

Pellet classification found no inconsistencies or unsatisfiable named classes in either the updated schema or the worked example.

The Figure 8 example yields ten directed `hasFlowDependency` links and ten directed `sharesInputVariable` links, matching the explicitly checked expectations. Shared input does not by itself imply resource contention or an exclusive choice.

Checks cover the seven task assignments, five events, ten control transitions, four message exchanges, correct message roles and payloads, explicit approval/rejection conditions, single producers, and the separation of planned elements from actual executions and artifacts. Separate test fixtures confirmed that reusing the initial-draft output variable for two distinct producers is inconsistent, and that a task cannot also be a planned event.

Guard queries on separate test data matched approval to submission, rejection to replacement, and missing decision information to no branch. This demonstrates how to consult the conditions; it does not turn the ontology into an executable workflow engine.

The inherited regression tests also passed: 31 PROV type entailments, qualified associations, prior resource-dependency controls, and 484 interval-pair comparisons covering all thirteen Allen relations. Synthetic tests and inferred triples are not included in the deliverables.

## Useful SPARQL queries

Updated 4 November 2026 by ChatGPT for the Figure 8 demonstration in AllegroGraph/Gruff.

The table and graph queries below work directly on the asserted content of `supply_chain_figure8.ttl`; no prior SWRL execution or materialization is required. They are scoped to `fig8:TenderingPlan`.

Use the `SELECT` variants for tables. Use the `CONSTRUCT` variants for visual graphs: run the query in Gruff, then choose **Create Visual Graph**. A `CONSTRUCT` returns a graph for browsing; it does not insert those triples into the repository. These instructions target Gruff connected directly to AllegroGraph, as in the demonstration, rather than its generic SPARQL-endpoint mode.

Gruff has to reconstruct related triples from a `SELECT` result. Returning only labels can therefore produce a valid table with nothing to graph. Including entity IRIs helps, but the explicit graph variants specify exactly which links should be displayed. See [Gruff 9.0.2 query documentation](https://franz.com/agraph/support/documentation/9.0.2/gruff.html).

### 1. Task assignments

**1a — Table: seven assignments.** The assignment individual is now included so the result retains the connection between each task, agent, and role.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?assignment ?task ?label ?agent ?role WHERE {
  ?task pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?label.
  ?assignment sc:assignmentForStep ?task;
              sc:assignedAgent ?agent;
              sc:assignedRole ?role.
}
ORDER BY ?task
```

**1b — Graph: tasks, assignments, agents, and roles.** This includes the assignment nodes and their three links, rather than showing only tasks linked to the plan. The two organizations remain illustrative placeholders, as described above.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?assignment sc:assignmentForStep ?task;
              sc:assignedAgent ?agent;
              sc:assignedRole ?role;
              rdfs:label ?assignmentLabel.
  ?task pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?label.
  ?agent rdfs:label ?agentLabel.
  ?role rdfs:label ?roleLabel.
  fig8:TenderingPlan rdfs:label ?planLabel.
} WHERE {
  ?task pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?label.
  ?assignment sc:assignmentForStep ?task;
              sc:assignedAgent ?agent;
              sc:assignedRole ?role.
  OPTIONAL { ?assignment rdfs:label ?assignmentLabel. }
  OPTIONAL { ?agent rdfs:label ?agentLabel. }
  OPTIONAL { ?role rdfs:label ?roleLabel. }
  OPTIONAL { fig8:TenderingPlan rdfs:label ?planLabel. }
}
```

### 2. Control transitions and branch conditions

**2a — Table: ten transitions.** Returns the transition and endpoint IRIs alongside their labels. Two rows have outcomes: approval leads to submission and rejection leads to replacement. The other eight rows have no condition/outcome binding because those transitions are unconditional.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?transition ?from ?fromLabel ?to ?toLabel ?condition ?outcome WHERE {
  ?transition sc:transitionFrom ?from; sc:transitionTo ?to.
  ?from pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?fromLabel.
  ?to pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?toLabel.
  OPTIONAL {
    ?transition sc:hasCondition ?condition.
    ?condition sc:expectedOutcome ?outcome.
  }
}
ORDER BY ?fromLabel ?toLabel
```

**2b — Graph: the ten transition individuals and their endpoints, plus the two branch conditions.** The transition is a node with `transitionFrom` and `transitionTo` links. These links both originate at the transition node; follow their predicate names to distinguish the source and target steps. The graph preserves the ontology's actual representation instead of inventing a direct step-to-step control predicate. The outcomes describe alternatives in the plan, not votes that have actually occurred.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?transition sc:transitionFrom ?from;
              sc:transitionTo ?to;
              sc:hasCondition ?condition;
              rdfs:label ?transitionLabel.
  ?from rdfs:label ?fromLabel.
  ?to rdfs:label ?toLabel.
  ?condition sc:expectedOutcome ?outcome; rdfs:label ?conditionLabel.
  ?outcome rdfs:label ?outcomeLabel.
} WHERE {
  ?transition sc:transitionFrom ?from; sc:transitionTo ?to.
  ?from pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?fromLabel.
  ?to pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?toLabel.
  OPTIONAL {
    ?transition sc:hasCondition ?condition.
    ?condition sc:expectedOutcome ?outcome.
    OPTIONAL { ?condition rdfs:label ?conditionLabel. }
    OPTIONAL { ?outcome rdfs:label ?outcomeLabel. }
  }
  OPTIONAL { ?transition rdfs:label ?transitionLabel. }
}
```

### 3. Resource-flow dependencies without prior reasoning

The original third query selected `sc:hasFlowDependency` triples. That property is declared and appears in a SWRL rule head, but the supplied Turtle file contains **zero asserted uses of it as a predicate**. Importing rule definitions is not the same as executing the rules or loading their inferred results. A zero-row result, or Gruff's warning that no triples use this predicate, is therefore expected on the asserted graph.

For this demonstration, calculate the dependencies at query time by joining a producer's `pp:hasOutputVar` with a consumer's `pp:hasInputVar` for the same variable. Both steps must belong to the Figure 8 plan.

**3a — Table: ten distinct producer/consumer pairs.**

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?producer ?consumer WHERE {
  ?producer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
}
ORDER BY ?producer ?consumer
```

This reproduces the ten expected dependency pairs for this Figure 8 dataset. Its steps are explicitly different individuals and are CollaborationSteps through their declared types and subclass hierarchy. The `!=` filter compares RDF terms; it is not a general replacement for OWL/SWRL distinctness reasoning on arbitrary ontologies.

**3b — Graph: ten derived dependency edges.** The `WHERE` clause reads the asserted output/input links, so it does not require pre-existing `hasFlowDependency` triples. The `CONSTRUCT` presents those calculated links under the existing `sc:hasFlowDependency` property. They are query results, not changes to the stored ontology.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
CONSTRUCT {
  ?producer sc:hasFlowDependency ?consumer;
            rdfs:label ?producerLabel.
  ?consumer rdfs:label ?consumerLabel.
} WHERE {
  ?producer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
  OPTIONAL { ?producer rdfs:label ?producerLabel. }
  OPTIONAL { ?consumer rdfs:label ?consumerLabel. }
}
```

The two opposite dependencies between the send-and-await task and the voting task are intentional: one carries the voting request and the other carries the reply. They are resource dependencies, not a control-flow loop or a requirement that each task finish before the other starts.

**3c — Explanation table: which variable establishes each dependency?** Returns twelve rows supporting the ten distinct pairs. Two pairs each share both a document variable and a message variable, so `DISTINCT` on the producer/consumer pair in 3a is intentional.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?producer ?consumer ?variable WHERE {
  ?producer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasOutputVar ?variable.
  ?consumer pp:isStepOfPlan fig8:TenderingPlan;
            pp:hasInputVar ?variable.
  FILTER(?producer != ?consumer)
}
ORDER BY ?producer ?consumer ?variable
```

### Optional: query stored or reasoner-visible dependency triples

The original third query remains useful after inferred dependency assertions have been exported and loaded, materialized by an appropriate rule translation, or otherwise made visible to the query engine. Merely running a reasoner in a separate Protégé session does not make its inferences available in AllegroGraph.

**Expected on the supplied asserted file: zero rows.** This query is a check for available dependency triples, not the recommended first-use demonstration query.

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
SELECT ?producer ?consumer WHERE {
  ?producer pp:isStepOfPlan fig8:TenderingPlan;
            sc:hasFlowDependency ?consumer.
}
ORDER BY ?producer ?consumer
```

### Query verification for this revision

All eight SPARQL blocks in this section were executed with RDFLib against the GitHub `supply_chain_figure8.ttl` retrieved on 4 November 2026. The original three queries returned 7, 10, and 0 rows, reproducing the reported behavior. The replacement dependency query matched all ten independently enumerated expected pairs from the original Figure 8 validation, including the request/reply pair in both directions. The graph versions were checked for their assignment, transition, condition, and dependency edges; the source graph remained unchanged.

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

This revision tests SPARQL results and graph structure; it is not a new Pellet validation or a claim that the queries have been run in the user's live Gruff/AllegroGraph repository. The earlier ontology-validation results above remain the record of the original implementation.

## Suggested commit text for this Figure 8 implementation

```text
Implement the Figure 8 collaborative tendering plan

Extended the reusable supply-chain schema with planned task, communication, start-event, and end-event categories, plus properties for event lanes and triggering variables. Preserved the ten existing SWRL rules and the corrected base ontology definitions.

Added supply_chain_figure8.ttl as a separate self-contained example containing the seven tasks, two start events, three end events, seven planned role assignments, ten resource/message variables, four message exchanges, ten control-flow transitions, and explicit approval/rejection conditions from the paper. Kept document versions and message payloads in distinct planned variables, with one producer per produced variable.

Documented the send-and-await interpretation of the voting request task so that the returning vote is represented without inventing an eighth task or converting the request/reply resource cycle into a control-flow loop. Kept the supplier-replacement branch terminal as drawn. Added dated change notes identifying ChatGPT and retained a clear separation between planned workflow elements and actual executions.

Validated both ontologies with Pellet and checked the expected resource dependencies, message exchanges, control topology, branch conditions, and producer constraints. All inherited temporal and PROV regression checks passed. The basic process_model.ttl was unchanged.
```
