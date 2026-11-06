# Figure 8: restored rules and a dated execution

Prepared 5 November 2026 for Michael DeBellis. All execution data are synthetic demonstration data, not a record of a real tender.

## Open the RDF/XML file in Protégé

**Use `supply_chain_figure8.rdf` in Protégé.** It contains the complete model, restored rules, and the dated example. The `.rdf` and `.ttl` files represent the same RDF graph and retain the original vocabulary and named rule IRIs on disk. Load one format, not both, into a fresh test repository.

The Turtle file is suitable for direct RDF loading into AllegroGraph. **Avoid opening that named-rule Turtle in the affected Protégé/OWLAPI installation and saving it over your source.** A test using OWLAPI 4.5.29, matching the generator identified in the damaged upload, reproduced ten empty SWRL rules from both the intact donor and restored Turtle. The same model in RDF/XML loaded, saved, and reloaded with all ten complete rules and their annotations. SWRLTab was not involved in this reproduction. Moving named rules after variable declarations or removing AtomList typing did not solve the Turtle failure. Experimental anonymous-rule Turtle worked, but the supplied source preserves the named rule IRIs.

This establishes a failure in that parser/version/encoding combination, not the release that introduced it or the cause of a particular SWRLTab update. OWLAPI saves can turn named SWRL rule nodes into anonymous nodes while retaining their labels and executable content; keep the supplied named-rule source as the reference. The separate `recovery` folder contains the untouched donor and a repaired plan without the new execution data.

## What changed

- Restored seven temporal rules, two planned resource-flow rules, and the qualified-association rule from the uploaded intact `supply_chain_model(1).ttl`.
- Restored seventeen SWRL variable declarations and removed damaged rule fragments and eight SWRL structural predicates incorrectly declared as annotation properties.
- Preserved all 3,170 unrelated triples from the latest Figure 8 upload, including its plan, labels, and transition inverse properties. Updated ontology metadata to describe the additional example.
- Added six `sc:StepExecution` individuals and one overall `prov:Activity`, `fig8:TenderRun01`. The overall Activity contains the six executions through the existing `sulo:hasPart` property; it is neither a Plan nor a provenance Bundle.
- Added actual-example participants through qualified PROV associations; ten artifacts correspond to the ten planned Variables, including four messages and one approval decision.
- Added seven `time:ProperInterval` individuals linked from Activities with `time:hasTime`. Interval endpoints have `time:inXSDDateTimeStamp` values. Direct `prov:startedAtTime` and `prov:endedAtTime` values on Activities support the Gruff timeline. Both representations denote the same instants.

No custom classes/properties, SHACL constraints, or stored Allen inferences were added. The updated source includes the standard PROV declarations needed by the qualified-usage records; these were omitted from the first delivery. Existing ontology namespaces and naming conventions were retained.

## Read the example

All times are UTC on 2 November 2026.

| Activity | Planned Step | Start | End | Participant |
|---|---|---|---|---|
| Run01CreateDraft | t1CreateTenderDraftTask | 09:00 | 11:00 | Lead supplier |
| Run01ProvideInput | t222MakeInputTask | 11:30 | 13:00 | Invited partner |
| Run01IncorporateInput | t2IncorporateInputsTask | 13:00 | 15:00 | Lead supplier |
| Run01SendAndAwaitVote | t11SendTenderForVotingTask | 15:00 | 17:30 | Lead supplier |
| Run01Vote | t12VoteForTenderTask | 15:15 | 17:00 | Invited partner |
| Run01Submit | t3SubmitTenderTask | 17:30 | 18:00 | Lead supplier |

Each task Activity has exactly one `pp:correspondsToStep` link. The original Steps remain planned descriptions. A future run would have new Activity/artifact/interval individuals referring to these same Steps and Variables.

The voting request is generated at 15:00; the partner uses it at 15:15, produces an approval at 16:55, and generates its reply at 17:00. The supplier uses the reply at 17:15 while its send-and-await Activity is still running. That Activity ends at 17:30, when submission starts. An input can therefore be used during execution without having existed at the Activity's start.

The replacement Step and its rejection condition remain in the Plan. This successful run has no replacement Activity. Start/end EventSteps remain planned milestones; this example does not give them fabricated duration-bearing task Activities. The overall run begins with drafting and ends with submission; the external call for tender is already available at that start.

## Queries

The five `.rq` files can be pasted into Gruff. Queries 1, 2, 4, and 5 work from asserted data. Query 3 needs the inferred Allen assertions visible to the query engine, for example after running Pellet and loading the exported inferences into AllegroGraph. AllegroGraph loading the SWRL triples alone is not a substitute for executing these SWRL rules.

| File | Result | Verified size |
|---|---|---|
| 01_execution_table.rq | Activities, Steps, agents, roles, timestamps, intervals | 6 rows |
| 02_execution_graph_timeline.rq | Graph of executions and corresponding Steps with date properties | 44 triples |
| 03_inferred_allen_relations.rq | Relations between the six task intervals, with Activity labels | 30 ordered pairs after inference |
| 04_approval_evidence.rq | Approval result, matching conditional transition, and performed submission | 1 row |
| 05_message_timing.rq | Four messages with producers, generation times, consumers, and use times | 4 rows |

Query 2 projects `prov:wasAssociatedWith` from qualified associations for display; the supplied source stores the qualified associations. Query 4 matches the recorded outcome and performed Step; it does not execute a branch. Query 3 filters to Activities with Step correspondence so any reflexive `sulo:hasPart` inference does not add the overall run to the task-only view.

Queries 1, 2, and 5 normalize date lexical values to `xsd:dateTime`; the SELECT queries also use DISTINCT. This prevents equivalent `dateTime`/`dateTimeStamp` literals in an inference export from duplicating display rows. It does not modify the stored timestamps or the SWRL rules.

Useful inferred relations: drafting is **before** partner input; input **meets** incorporation; incorporation **meets** send-and-await; send-and-await **contains** voting; voting is **during** send-and-await; send-and-await **meets** submission. The overall run additionally shows **starts/started by** and **finishes/finished by**. The business example naturally covers eleven Allen relations when the run and self-pairs are included. A separate regression covers all thirteen; the example was not distorted to force a crossing overlap.

## Query Visualizations
<img width="1041" height="544" alt="Query_01" src="https://github.com/user-attachments/assets/f48b86cf-3c7b-4157-a87e-1fd9af87c88c" />
Query 01 Execution Table




## Gruff timeline

1. Display the result graph from query 2, including the Activity date triples.
2. Set **Visual Graph Options → Time Bar → Start Time Predicate** to `http://www.w3.org/ns/prov#startedAtTime`.
3. Set **End Time Predicate** to `http://www.w3.org/ns/prov#endedAtTime`.
4. Enable **View → Optional Graph View Panes → Show Time Bar**.
5. Click the square Time Chart button on the time bar and sort by the earliest date.

The timeline uses literal dates on Activities. `time:hasBeginning` and `time:hasEnd` instead point to Instant nodes, so use the PROV predicates for these settings. The PNG is an independent preview of the intended schedule, not a screenshot or verification of your installed Gruff UI. Times may be rendered in a local timezone by a viewer; the stored literals explicitly use UTC.

Menu reference: [Franz Gruff documentation, AllegroGraph 9.0.2](https://franz.com/agraph/support/documentation/9.0.2/gruff.html).

## Validation

- RDFLib parsed both formats and confirmed graph equivalence. Validation reports record the triple counts for the original example and subsequent declaration repair.
- All ten restored rule subgraphs match the donor; other source triples are preserved apart from the documented rule repair and ontology metadata update.
- Pellet loaded and extracted inferences successfully. All 49 ordered pairs among seven demonstration intervals have exactly the expected Allen relation.
- A separate regression checked 484 ordered interval pairs, all thirteen Allen relations, invalid/reversed/incomplete interval controls, timezone equivalence, and absence of unintended merging from equal time values.
- Six task correspondences, ten artifacts, four messages, twelve qualified usages, seven actual-agent inferences, and ten planned flow dependencies passed checks. Generation precedes use and recorded events fall within the relevant Activities.
- No Plan was inferred to be an Activity; no replacement execution was added.
- OWLAPI 4.5.29 read/save/reload preserved all ten rule bodies/heads and annotations through the RDF/XML route. The Turtle failure was reproduced separately. This does not test the installed SWRLTab UI.

Validation summaries and the Java round-trip harness are under `validation`. Regression fixtures and inferred triples are excluded from the ontology files. The `recovery` folder includes the unchanged rules donor, the repaired plan before the new execution, and the repair script.

## Verification against Michael's Protégé export

The supplied `supply_chain_figure8_inferences.rdf` has 6,010 triples. All 49 ordered pairs among the seven example intervals have exactly the expected Allen relation, matching the independent local Pellet results. All seven agent associations and ten planned flow dependencies are present, all ten rules remain complete, and the Plan/Step versus Activity distinction is preserved. No replacement execution appears. RDF/XML and the timestamp values therefore work in the tested installation; the Allen results are on the linked intervals rather than on the Activities themselves.

The export also exposed an omission in the first delivery: `prov:qualifiedUsage` and `prov:entity` lacked object-property declarations, so OWLAPI treated them as annotations. The updated source restores the required standard PROV declarations and supporting class axioms. This is separate from the successful temporal inference. The original export is retained unchanged. Updated query counts on that export are 6 rows, 44 triples, 30 interval-pair rows, 1 approval row, and 4 message rows respectively.
