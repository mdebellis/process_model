# Figure 8 synthetic execution and temporal reasoning

Execution example prepared 5 November 2026 for Michael DeBellis. All execution data are synthetic demonstration data, not a record of a real tender. This page describes the execution layer of the [Figure 8 plan](figure8_model_notes.md).

Current examples use `pm:` for the entity namespace `https://in2use.com/process_model/`. The ontology IRI is `https://in2use.com/process_model`, without the trailing slash; its label is **Process model with examples**. The [naming guide](naming_conventions.md) explains the current convention and earlier identifier changes. Historical reports and screenshots retain the earlier identifiers.

## Open the RDF/XML file in Protégé

**Open [process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf) in Protégé and retain RDF/XML when saving.** It is the repository's single ontology source, containing the reusable model, restored rules, Figure 8 plan and execution, Method Omega, and the state and goal extensions. This source can also be imported directly into AllegroGraph. Preserve `rdf:type` elements before other properties within resource descriptions; the [RDF/XML compatibility report](../validation/rdfxml_compatibility.md) explains why this ordering is needed for the affected OWLAPI parser.

**Do not convert the source to Turtle for editing in the affected Protégé/OWLAPI installation: that route deleted SWRL rule content.** A test using OWLAPI 4.5.29, matching the generator identified in the damaged upload, reproduced ten empty SWRL rules from both the intact donor and restored Turtle. The same model in RDF/XML loaded, saved, and reloaded with all ten complete rules and their annotations. SWRLTab was not involved in this reproduction. Moving named rules after variable declarations or removing AtomList typing did not solve the Turtle failure. Experimental anonymous-rule Turtle worked, but the supplied source preserves the named rule IRIs.

This establishes a failure in that parser/version/encoding combination, not the release that introduced it or the cause of a particular SWRLTab update. OWLAPI saves can turn named SWRL rule nodes into anonymous nodes while retaining their labels and executable content; keep the supplied named-rule source as the reference. The repository now keeps the combined RDF/XML source and the [historical validation reports](../validation/history/figure8/), rather than separate donor and recovery ontologies.

## Historical repair and execution additions on 5 November 2026

- Restored seven temporal rules, two planned resource-flow rules, and the qualified-association rule from the uploaded intact `supply_chain_model(1).ttl`.
- Restored seventeen SWRL variable declarations and removed damaged rule fragments and eight SWRL structural predicates incorrectly declared as annotation properties.
- Preserved all 3,170 unrelated triples from the latest Figure 8 upload, including its plan, labels, and transition inverse properties. Updated ontology metadata to describe the additional example.
- Added six `Step_Execution` individuals and one overall `prov:Activity`, `Tender_Run_01` (now `pm:Step_Execution` and `pm:Tender_Run_01`). The overall Activity contains the six executions through the existing `sulo:hasPart` property; it is neither a Plan nor a provenance Bundle.
- Added actual-example participants through qualified PROV associations; ten artifacts correspond to the ten planned Variables, including four messages and one approval decision.
- Added seven `time:ProperInterval` individuals linked from Activities with `time:hasTime`. Interval endpoints have `time:inXSDDateTimeStamp` values. Direct `prov:startedAtTime` and `prov:endedAtTime` values on Activities support the Gruff timeline. Both representations denote the same instants.

That execution addition introduced no custom classes/properties, SHACL constraints, or stored Allen inferences. The current combined source includes the standard PROV declarations needed by the qualified-usage records; these were omitted from the first delivery. The execution addition retained the namespaces and naming conventions in use at that time; the later namespace migration changed the project-owned IRIs.

## Read the example

All times are UTC on 2 November 2026.

| Activity | Planned Step | Start | End | Participant |
|---|---|---|---|---|
| Run_01_Create_Draft | T1_Create_Tender_Draft_Task | 09:00 | 11:00 | Lead supplier |
| Run_01_Provide_Input | T222_Make_Input_Task | 11:30 | 13:00 | Invited partner |
| Run_01_Incorporate_Input | T2_Incorporate_Inputs_Task | 13:00 | 15:00 | Lead supplier |
| Run_01_Send_And_Await_Vote | T11_Send_Tender_For_Voting_Task | 15:00 | 17:30 | Lead supplier |
| Run_01_Vote | T12_Vote_For_Tender_Task | 15:15 | 17:00 | Invited partner |
| Run_01_Submit | T3_Submit_Tender_Task | 17:30 | 18:00 | Lead supplier |

Each task Activity has exactly one `pp:correspondsToStep` link. The original Steps remain planned descriptions. A future run would have new Activity/artifact/interval individuals referring to these same Steps and Variables.

The voting request is generated at 15:00; the partner uses it at 15:15, produces an approval at 16:55, and generates its reply at 17:00. The supplier uses the reply at 17:15 while its send-and-await Activity is still running. That Activity ends at 17:30, when submission starts. An input can therefore be used during execution without having existed at the Activity's start.

The replacement Step and its rejection condition remain in the Plan. This successful run has no replacement Activity. Start/end EventSteps remain planned milestones; this example does not give them fabricated duration-bearing task Activities. The overall run begins with drafting and ends with submission; the external call for tender is already available at that start.

## Queries

The five files in [queries/figure8_execution](../queries/figure8_execution/) can be pasted into Gruff. Queries 1, 2, 4, and 5 work from asserted data. Query 3 needs the inferred Allen assertions visible to the query engine, for example after running Pellet and loading the exported inferences into AllegroGraph. AllegroGraph loading the SWRL triples alone is not a substitute for executing these SWRL rules.

| File | Result | Historical verified size |
|---|---|---|
| [01_execution_table.rq](../queries/figure8_execution/01_execution_table.rq) | Activities, Steps, agents, roles, timestamps, intervals | 6 rows |
| [02_execution_graph_timeline.rq](../queries/figure8_execution/02_execution_graph_timeline.rq) | Graph of executions and corresponding Steps with date properties | 44 triples |
| [03_inferred_allen_relations.rq](../queries/figure8_execution/03_inferred_allen_relations.rq) | Relations between the six task intervals, with Activity labels | 30 ordered pairs after inference |
| [04_approval_evidence.rq](../queries/figure8_execution/04_approval_evidence.rq) | Approval result, matching conditional transition, and performed submission | 1 row |
| [05_message_timing.rq](../queries/figure8_execution/05_message_timing.rq) | Four messages with producers, generation times, consumers, and use times | 4 rows |

The historical cleanup checks reproduced 6 rows, 44 triples, 1 approval row, and 4 message rows on the then-current asserted source. Query 3 returned zero rows because the source excludes materialized Allen inferences. See [cleanup_verification.json](../validation/cleanup_verification.json) for that snapshot and [namespace_migration.json](../validation/namespace_migration.json) for the later migration checks.

Query 2 projects `prov:wasAssociatedWith` from qualified associations for display; the supplied source stores the qualified associations. Query 4 matches the recorded outcome and performed Step; it does not execute a branch. Query 3 filters to Activities with Step correspondence so any reflexive `sulo:hasPart` inference does not add the overall run to the task-only view.

Queries 1, 2, and 5 normalize date lexical values to `xsd:dateTime`; the SELECT queries also use DISTINCT. This prevents equivalent `dateTime`/`dateTimeStamp` literals in an inference export from duplicating display rows. It does not modify the stored timestamps or the SWRL rules.

Useful inferred relations: drafting is **before** partner input; input **meets** incorporation; incorporation **meets** send-and-await; send-and-await **contains** voting; voting is **during** send-and-await; send-and-await **meets** submission. The overall run additionally shows **starts/started by** and **finishes/finished by**. The business example naturally covers eleven Allen relations when the run and self-pairs are included. A separate regression covers all thirteen; the example was not distorted to force a crossing overlap.

## Query Visualizations

These screenshots predate the namespace migration. Any older IRIs or prefixes visible in them are historical; use the linked query files for the current identifiers.

<img width="1041" height="544" alt="Query_01" src="https://github.com/user-attachments/assets/f48b86cf-3c7b-4157-a87e-1fd9af87c88c" />
Query 01 Execution Table
<br>
<br>
<img width="1475" height="644" alt="Query 02 (2)" src="https://github.com/user-attachments/assets/1c1f1d52-b407-4a36-931f-202052038a97" />
Query 02 
<br>
<br>
<img width="799" height="324" alt="Query_03" src="https://github.com/user-attachments/assets/b0ae5e4d-c4d7-4c65-a614-5304fc266276" />
<br>Query 03
<br>
<br>
<img width="958" height="463" alt="Query_04" src="https://github.com/user-attachments/assets/90849094-9a98-4dda-ac3d-7146980dfd34" />
<br>Query 04
<br>
<br>
<img width="836" height="596" alt="Query_05" src="https://github.com/user-attachments/assets/c5baf9fd-4d5f-44ce-ae99-381be319aaf9" />
<br>Query 05
<br>
<br>

## Gruff timeline

1. Display the result graph from query 2, including the Activity date triples.
2. Set **Visual Graph Options → Time Bar → Start Time Predicate** to `http://www.w3.org/ns/prov#startedAtTime`.
3. Set **End Time Predicate** to `http://www.w3.org/ns/prov#endedAtTime`.
4. Enable **View → Optional Graph View Panes → Show Time Bar**.
5. Click the square Time Chart button on the time bar and sort by the earliest date.

The timeline uses literal dates on Activities. `time:hasBeginning` and `time:hasEnd` instead point to Instant nodes, so use the PROV predicates for these settings. The [tender execution timeline](../docs/tender_execution_timeline.png) is an independent preview of the intended schedule, not a screenshot or verification of an installed Gruff UI. Times may be rendered in a local timezone by a viewer; the stored literals explicitly use UTC.

Menu reference: [Franz Gruff documentation, AllegroGraph 9.0.2](https://franz.com/agraph/support/documentation/9.0.2/gruff.html).

## Historical validation

These findings record the November 2026 execution-model checks, before Method Omega was added. They describe the historical test results, rather than a new reasoner run during repository cleanup.

- RDFLib parsed both formats and confirmed graph equivalence. Validation reports record the triple counts for the original example and subsequent declaration repair.
- All ten restored rule subgraphs match the donor; other source triples are preserved apart from the documented rule repair and ontology metadata update.
- Pellet loaded and extracted inferences successfully. All 49 ordered pairs among seven demonstration intervals have exactly the expected Allen relation.
- A separate regression checked 484 ordered interval pairs, all thirteen Allen relations, invalid/reversed/incomplete interval controls, timezone equivalence, and absence of unintended merging from equal time values.
- Six task correspondences, ten artifacts, four messages, twelve qualified usages, seven actual-agent inferences, and ten planned flow dependencies passed checks. Generation precedes use and recorded events fall within the relevant Activities.
- No Plan was inferred to be an Activity; no replacement execution was added.
- OWLAPI 4.5.29 read/save/reload preserved all ten rule bodies/heads and annotations through the RDF/XML route. The Turtle failure was reproduced separately. This does not test the installed SWRLTab UI.

Validation summaries are retained under [validation/history/figure8](../validation/history/figure8/). The single ontology source excludes regression fixtures and materialized inferred triples. Donor ontologies, recovery snapshots, and obsolete build files are no longer shipped. See the [validation guide](../validation/README.md) for the distinction between historical reports and current namespace migration checks.
