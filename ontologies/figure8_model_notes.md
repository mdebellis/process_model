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

List the seven task assignments. This query works on the asserted graph:

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?task ?label ?agent ?role WHERE {
  ?task pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?label.
  ?assignment sc:assignmentForStep ?task;
              sc:assignedAgent ?agent;
              sc:assignedRole ?role.
}
ORDER BY ?task
```

List the ten control transitions and their optional decision outcomes. This also works on the asserted graph:

```sparql
PREFIX sc: <https://www.michaeldebellis.com/supply_chain_model/>
PREFIX fig8: <https://www.michaeldebellis.com/supply_chain_figure8/>
PREFIX pp: <http://purl.org/net/p-plan#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?fromLabel ?toLabel ?outcome WHERE {
  ?transition sc:transitionFrom ?from; sc:transitionTo ?to.
  ?from pp:isStepOfPlan fig8:TenderingPlan; rdfs:label ?fromLabel.
  ?to rdfs:label ?toLabel.
  OPTIONAL { ?transition sc:hasCondition/sc:expectedOutcome ?outcome. }
}
ORDER BY ?fromLabel ?toLabel
```

List inferred resource-flow links. The query engine must be able to see the SWRL inference output:

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

## Suggested commit text for this Figure 8 implementation

```text
Implement the Figure 8 collaborative tendering plan

Extended the reusable supply-chain schema with planned task, communication, start-event, and end-event categories, plus properties for event lanes and triggering variables. Preserved the ten existing SWRL rules and the corrected base ontology definitions.

Added supply_chain_figure8.ttl as a separate self-contained example containing the seven tasks, two start events, three end events, seven planned role assignments, ten resource/message variables, four message exchanges, ten control-flow transitions, and explicit approval/rejection conditions from the paper. Kept document versions and message payloads in distinct planned variables, with one producer per produced variable.

Documented the send-and-await interpretation of the voting request task so that the returning vote is represented without inventing an eighth task or converting the request/reply resource cycle into a control-flow loop. Kept the supplier-replacement branch terminal as drawn. Added dated change notes identifying ChatGPT and retained a clear separation between planned workflow elements and actual executions.

Validated both ontologies with Pellet and checked the expected resource dependencies, message exchanges, control topology, branch conditions, and producer constraints. All inherited temporal and PROV regression checks passed. The basic process_model.ttl was unchanged.
```
