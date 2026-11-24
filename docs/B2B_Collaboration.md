# B2B collaboration: goals, a plan, and execution evidence

This example develops the lavatory collaboration from the supplied draft
**A Collaboration Design Method for Manufacturing Supply Chains**. It uses
the paper's goal decomposition, supplier responsibilities, MakePart,
AssembleProduct, DeliverProduct, and coordination ideas. The supplier names
TurboCo and ExecCo follow the draft; CoverCo, the dates, transport proposal,
receipts, detailed conditions, and execution trace are fictional additions.
This is a bounded worked example for discussion, not a claim that the paper
specifies this exact workflow or that these companies performed it.

Open the updated
[process_model_with_examples.rdf](../ontologies/process_model_with_examples.rdf).
All data is in the default graph and the existing
`https://in2use.com/process_model/` namespace (`pm:`). Existing tender and
Customer Portal examples remain in the same file.

## Start here for the demonstration

1. Load the updated source in Protégé and run Pellet. Regenerate the inferred
   export used by AllegroGraph and replace the old data before materializing.
   This update adds ontology and example data, unlike the previous query-only
   changes. The older `process_model_inferred_axioms.rdf` in the repository is
   not updated by this change and does not contain the B2B addition.
2. Run [02_goal_hierarchy.rq](../queries/b2b_collaboration/02_goal_hierarchy.rq)
   and choose **Create Visual Graph**. Start with the desired delivered module,
   then follow its subgoals and assigned suppliers.
3. Run [04_conditions_and_tests.rq](../queries/b2b_collaboration/04_conditions_and_tests.rq)
   to connect manufacture, transfer, and assembly with their conditions and tests.
4. Run [06_state_evaluations.rq](../queries/b2b_collaboration/06_state_evaluations.rq)
   for the evidence story below. Use
   [08_frame_evidence.rq](../queries/b2b_collaboration/08_frame_evidence.rq)
   to inspect the actual frame, decision, receipt, and Activities.
5. Compare planned and actual work with
   [05_plan_and_execution.rq](../queries/b2b_collaboration/05_plan_and_execution.rq).

Graph queries return existing RDF triples. They do not invent property-path
edges or attach interval predicates directly to Activities. Queries that
scope execution use materialized `sulo:hasPart`; the execution tree displays
`sulo:hasDirectPart`. In Gruff, press **M** to toggle link labels.

## Gruff Visualizations of SPARQL Queries 2-5

### Subgoal Hierarchy

<img width="1058" height="373" alt="image" src="https://github.com/user-attachments/assets/3797e813-127a-4613-9efc-7f8fba7218cf" />

### Conditions and Tests

<img width="1261" height="636" alt="image" src="https://github.com/user-attachments/assets/52d24ce5-ef02-4f99-9153-9daf87be41b0" />



## Four objects with distinct jobs

| Individual | Meaning |
|---|---|
| `Collaboration_Design_Methodology` | The paper's recursive design decisions T1–T5: decompose goals, assign suppliers, operationalize subgoals, decompose processes, and define coordination mechanisms. |
| `B2B_Collaboration_Methodology` | A reusable, bounded operational pattern for the lavatory example. Its seven Steps describe the work that suppliers will perform. |
| `Lavatory_Collaboration_Plan` | A supplier-specific plan derived from the operational pattern, with its own Steps, Variables, goals, assignments, and scheduled dates. |
| `Lavatory_Collaboration_Execution` | The actual-work layer of the fictional scenario, observed at **4 March 2027, 12:00 UTC**. |

The first three are `p-plan:Plan` individuals. The execution root is a
`prov:Activity`; each recorded `Step_Execution` corresponds to exactly one
project-specific planned Step. Qualified PROV associations identify the actual
participating organizations, roles, and project plan.

T1–T5 are not flattened into the manufacturing sequence. They can be revisited
as the collaboration changes. Their own execution is not modeled in this first
increment. The qualitative goal `B2B_Collaboration_Designed` has an English
definition but no executable assessment yet.

## Goal hierarchy and responsibilities

The root goal is `Lavatory_Module_Delivered`. It has subgoals for the assembled
module and the transport cover. The assembly goal has subgoals for the available
frame and the other components. Frame availability has subgoals for manufacture
and transfer arrangements; manufacture also requires the frame design.

TurboCo is responsible for the overall delivery, design, coordination, and
assembly goals. ExecCo is responsible for manufacturing the frame and getting it
to the assembler. CoverCo is responsible for the transport cover. IRIs follow
the local naming convention: `Turbo_Co`, `Exec_Co`, and `Cover_Co`; the paper-style
spellings are retained as English alternative labels.

`has_sub_goal` records decomposition. It does **not** automatically make a parent
goal true when its children are true. For example, an assembled module and a
finished cover are insufficient to establish delivery: the parent test also
requires the delivery Activity and a customer receipt for that same module.

## Planned operational work

| Step | Assigned supplier | Main input | Main output / postcondition |
|---|---|---|---|
| Plan Frame | TurboCo | Internal design context omitted at this abstraction level | Frame design ready |
| Make Frame | ExecCo | Frame design | Physical frame manufactured |
| Coordinate Frame Transfer | TurboCo | Frame and transport proposal | Explicit approved transfer arrangement |
| Transfer Frame | ExecCo | Frame and approval decision | Receipt for that same frame at TurboCo; frame available |
| Make Transport Cover | CoverCo | Internal manufacturing resources omitted | Physical cover ready |
| Assemble Module | TurboCo | Frame, other component batch, and frame receipt | Assembled module |
| Deliver Module | TurboCo | Assembled module and cover | Receipt for the module at the customer |

There is no precedence edge between cover manufacture and frame design or
manufacture; these can proceed in parallel. Assembly requires the frame's
availability **and** the other component batch's availability. Delivery requires
the assembled module **and** the cover. Multiple incoming prerequisite edges
represent joint requirements in this example, not an exclusive gateway.

The paper abstracts MakePart as having no interdependent material inputs from
other suppliers. This example makes design information explicit and leaves
supplier-internal materials and labor outside its scope. Missing input Variables
therefore do not mean manufacturing without physical resources.

The transfer arrangement is a `Decision_Condition` and a `Goal`: the plan seeks
an approved arrangement, and the transfer transition checks that same outcome.
An absent decision does not mean rejection, and an approved decision is not proof
that the transfer happened.

## What happened in the fictional execution

| Event time (UTC) | Evidence and interpretation |
|---|---|
| 1 March, 12:00 | TurboCo completes the frame design. |
| 2 March, 17:00 | ExecCo finishes manufacturing `Lavatory_Frame_01`. The frame exists, but it has not arrived at TurboCo. |
| 3 March, 09:00 | Frame manufacture is Satisfied; frame availability and assembly readiness are Unsatisfied under the complete example-log assumption. Assembly has no Activity yet. |
| 3 March, 09:15–10:00 | Coordination evaluates the transport proposal and produces an explicit Approved decision. |
| 3 March, 10:00–13:00 | ExecCo transfers the same frame. Transfer generates `Lavatory_Frame_Receipt_01`, identifying the frame and TurboCo. |
| 3 March, 13:05 | Frame availability and assembly readiness are Satisfied. Other components were received before this run. |
| 3 March, 13:15 | Assembly actually starts. That start is a separate fact; readiness did not automatically execute the step. |
| 4 March, 12:00 | Assembly remains in progress. No finished module or delivery Activity is fabricated. |

Cover manufacture runs from 1 March at 09:00 until 3 March at 12:00. The planned
transfer finish was 12:00 and planned assembly start was 12:15; both occur one hour
later in the trace. The unchanged baseline makes that delay visible.

The root has six recorded step executions: five completed and one ongoing.
The seven planned Steps are retained. Unstarted delivery remains a planned Step,
with no Activity and no `Not_Started` status individual. There is also no finished
module individual before assembly produces one.

## Conditions, tests, and evaluation records

These are three different things:

| Layer | Example | Meaning |
|---|---|---|
| State description | `Lavatory_Frame_Available` | A condition that can hold for the specified frame, run, recipient, and time. |
| State test | `Lavatory_Frame_Available_Test` | SPARQL that looks for completed manufacture, the correct approval, the transfer, and the receipt by the assessment cutoff. |
| State evaluation | `Lavatory_Frame_Available_After_Transfer_Evaluation` | A synthetic, reproducible record of an assessment at 13:05, with result, evidence, context, and explanation. |

All ten project conditions have English definitions and SPARQL tests. The test
strings stored in the ontology require explicit `run` and `as_of` bindings;
the [runnable query files](../queries/b2b_collaboration/state_tests/) contain
concrete VALUES for this run at the final snapshot. Change the cutoff to
`2027-03-03T09:00:00Z` or `2027-03-03T13:05:00Z` to compare the readiness results.
Resource, proposal, recipient, and project-step bindings are deliberately fixed
to this first example, so a test cannot silently use another order's frame or
approval. A generalized evaluator will need explicit bindings for those inputs.

The eight assessment records are **synthetic example data**, replayed and checked
against the reasoned graph. They are not created by OWL inference, nor claims
that an evaluator actually ran on those future dates. Evidence links exclude
receipts and decisions that postdate the recorded assessment cutoff. The queries
use event time in one complete log; this is not a model of when a system first
learned a fact.

For this complete, unambiguous scenario, a false ASK result is recorded as
`Unsatisfied`. With incomplete evidence it should be `Unknown`; query failures
are `Evaluation_Error`. Conflicting decisions require review rather than choosing
whichever outcome makes the query succeed. The supplied Python caller rejects
missing inputs and conflicting decision outcomes before categorizing results.
No LLM call is made. A false ASK result does not trigger an automatic LLM fallback.

Receipt-based availability assumes no withdrawal, onward transfer, competing
allocation, or approval revocation before assembly. It does not establish quality
certification or continuing custody in an arbitrary future snapshot. Those are
separate conditions to add when required. Here, Unsatisfied delivery means
**not yet achieved**, not late delivery or a failed process.

## TBox additions

| Addition | Purpose |
|---|---|
| `has_precondition` / `is_precondition_of` | Link a Plan or Step to conditions required before a permitted start. Multiple preconditions are jointly required under this example's application policy. |
| `has_postcondition` / `is_postcondition_of` | Link a Plan or Step to conditions expected on successful completion. A recorded end alone does not prove them. |
| `has_responsible_agent` / `is_responsible_agent_of` | Assign responsibility for a context-specific goal, separately from actual PROV participation. |
| `Make_Part_Goal`, `Assemble_Product_Goal`, `Deliver_Product_Goal` | Preserve the paper's goal vocabulary as subclasses of `Goal`. |
| `Make_Part_Step`, `Assemble_Product_Step`, `Deliver_Product_Step`, `Coordination_Step` | Preserve operational distinctions as subclasses of `Task_Step`. |
| `Manufactured_Item`, `Frame`, `Transport_Cover`, `Lavatory_Module`, `Component_Batch` | Describe actual physical resources, distinct from information objects and planned Variables. |
| `Resource_Receipt`, `has_received_resource`, `has_receiving_agent`, and their inverses | Describe explicit receipt evidence for a resource and recipient. |
| `has_expected_type` (annotation property) | Name the class expected for an Entity realizing a Variable, without class/individual punning or a duplicate Variable class hierarchy. |

The additions are primitive classes and ordinary properties. They introduce no
automatic workflow engine, effect rules, new functional constraints, or global
closed-world semantics. Existing SULO containment/parthood choices and all ten
SWRL rules are unchanged. The expected-type annotation is checked with a query
over inferred entity types; it does not type the Variable as a physical item.

## Query index

All queries are in [queries/b2b_collaboration](../queries/b2b_collaboration/).
Run reasoning first so inverse properties, class types, and `hasPart` assertions
are visible to the query engine.

| Query | View |
|---|---|
| [01_methodology.rq](../queries/b2b_collaboration/01_methodology.rq) | Operational methodology Steps and their goals; the root can be changed to inspect T1–T5. |
| [02_goal_hierarchy.rq](../queries/b2b_collaboration/02_goal_hierarchy.rq) | Goal decomposition and responsible suppliers. |
| [03_plan_flow.rq](../queries/b2b_collaboration/03_plan_flow.rq) | Direct prerequisite transitions and the explicit approval condition. |
| [04_conditions_and_tests.rq](../queries/b2b_collaboration/04_conditions_and_tests.rq) | Preconditions, postconditions, component states, and tests. |
| [05_plan_and_execution.rq](../queries/b2b_collaboration/05_plan_and_execution.rq) | Seven planned Steps, supplier assignments, schedules, and recorded actual work. |
| [06_state_evaluations.rq](../queries/b2b_collaboration/06_state_evaluations.rq) | Eight assessment records with time, result, and explanation. |
| [07_execution_tree.rq](../queries/b2b_collaboration/07_execution_tree.rq) | Six direct execution-part edges. |
| [08_frame_evidence.rq](../queries/b2b_collaboration/08_frame_evidence.rq) | Manufacturing, coordination, transfer, assembly, and the frame receipt. |
| [09_expected_types.rq](../queries/b2b_collaboration/09_expected_types.rq) | Type-validation findings; zero rows is expected. |
| [10_readiness_history_graph.rq](../queries/b2b_collaboration/10_readiness_history_graph.rq) | Before/after assessment records for frame and assembly readiness. |

## Checks and next refinements

The [reasoning report](../validation/b2b_collaboration_reasoning.json) covers
Protégé-compatible Pellet consistency, classification, all ten complete SWRL
rules, and RDF/XML save/reload. The
[query report](../validation/b2b_collaboration_queries.json) covers the queries,
assessment replay, required caller bindings, temporal cutoffs, all recorded
start preconditions, and counterexamples with the wrong resource, recipient,
proposal, or decision. A hypothetical completed continuation tests the delivery
goal without adding that future execution to the ontology.

The [preservation report](../validation/b2b_collaboration_preservation.json)
checks naming, English annotations, property conventions, preservation of the
earlier source, and existing Customer Portal graph results. Validation uses
RDFLib and Pellet; the new queries have not been run in a live AllegroGraph/Gruff
session. The source remains RDF/XML to preserve SWRL compatibility.

This increment fully works through the **flow dependency** from frame manufacture
to assembly. Shared-input allocation and iterative shared-output collaboration
remain to be developed. Merely sharing a Variable does not establish scarce-resource
contention, and a shared-output iteration should not be modeled by assigning two
different producers to the same P-Plan output Variable. Supplier-capability
matching, rejection/replanning, repeated deliveries, and quality certification
also require further examples. BPMN diagrams should follow review of this first
operational model and its condition semantics.
