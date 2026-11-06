# Method Omega: abstract methodology excerpt

Work in progress — 6 November 2026.

The combined ontology now contains the existing Figure 8 tendering example and the Method Omega model from Michael's diagram. It contains **4,942 asserted triples**, with no exported inferences. The uploaded source was graph-isomorphic to the last corrected 4,498-triple deliverable, including all ten complete SWRL rules and the qualified PROV usage declarations.

## Open and review

Open **supply_chain_figure8.rdf** in Protégé. It is the complete combined ontology. Its ontology IRI remains `https://www.michaeldebellis.com/supply_chain_figure8`; only its descriptive header now mentions both examples. Existing vocabulary and individual IRIs are preserved.

RDF/XML is the editing format for this example because of the named-SWRL-rule Turtle/OWLAPI parsing issue previously reproduced. The Turtle file contains the same RDF graph and is included for text inspection and compatible RDF tools. The additions-only Turtle file is a review aid, not another complete ontology or a patch that removes old header values.

Run Pellet to see inverse properties and subclass classifications. For Gruff, the supplied queries also work on the asserted graph without exported inferences:

| Query | Result |
|---|---|
| `01_method_omega_hierarchy.rq` | Membership and the separate decomposition Plans |
| `02_method_omega_transitions.rq` | Directed control flow, approval and rework branches |
| `03_method_omega_deliverables.rq` | Producing Steps, exposed outputs and consuming Steps |
| `04_method_omega_step_inventory.rq` | A 16-row inventory with containing and decomposition Plans |

Use **Create Visual Graph** for the first three queries. Query 2 contains a commented filter for showing only the Requirements Acquisition level. These queries are graph projections; they do not add their constructed triples to the repository.

## Hierarchy

`mo:` denotes `https://www.in2use.com/method_omega/`.

| Containing Plan | Direct Steps |
|---|---|
| `Method_Omega` | `Requirements_Acquisition`, `Technical_Design`, `Implementation`, `Testing`, `Rollout` |
| `Requirements_Acquisition_Plan` | `Kickoff_Meeting`, `Create_Project_Narrative`, `Create_Detailed_Requirements`, `Review_Requirements`, `Requirements_Acquisition_Completed` |
| `Create_Detailed_Requirements_Plan` | `Create_Wireframes`, `Create_Use_Cases` |
| `Create_Wireframes_Plan` | `User_Wireframe_Interviews`, `Develop_Wireframes` |
| `Create_Use_Cases_Plan` | `Use_Case_Interviews`, `Write_Use_Cases` |

There are **16 Step definitions, including eight MultiSteps**. Four MultiSteps have explicit decomposition Plans. The other four top-level phases are marked as MultiSteps with their internal details unspecified. The completion text is represented as a planned end-event Step.

Each expanded MultiStep uses the P-Plan separation between a contextual Step and its body Plan. For example:

```turtle
mo:Requirements_Acquisition
    a pp:MultiStep ;
    pp:isStepOfPlan mo:Method_Omega ;
    pp:isDecomposedAsPlan mo:Requirements_Acquisition_Plan .

mo:Kickoff_Meeting
    a pp:Step ;
    pp:isStepOfPlan mo:Requirements_Acquisition_Plan .
```

The body Plan is also linked to its containing Plan through `pp:isSubPlanOfPlan`. Because P-Plan makes MultiStep a subclass of both Step and Plan, MultiSteps will appear under both classes in the inferred hierarchy. This does not make them actual processes or Activities.

Your downward arrows show parent-to-child membership. `pp:isStepOfPlan` itself runs in the opposite direction, so the new `pm:has_step` property is its inverse. For an expanded box, the full graph includes the extra `isDecomposedAsPlan` link that the drawing leaves implicit.

## Sequence, conditions and repeated work

`pm:` denotes `https://www.in2use.com/process_model/`. The following are local extensions, not P-Plan terms.

There are ten asserted forward precedence relationships. The underlying P-Plan triples use successor-to-predecessor direction; `pm:precedes` supplies the forward inverse. Neither relation denotes an immediate next step, because P-Plan precedence is transitive.

The twelve **StepTransition** individuals preserve the immediate possible arrows separately. Each is also a `pm:Finish_To_Start_Transition`, explicitly describing the requirement that the source occurrence completes before the target occurrence starts. The interpretation permits zero waiting time: finish at 11:00 and start at 11:00 are allowed; overlap is not. This is a declared scheduling constraint, not an executable rule or an actual Allen relation.

The **Requirements Approved?** diamond is an `sc:ExclusiveChoice`, not an extra work Step:

- The decision is produced by `Review_Requirements` in the planned `Requirements_Review_Decision` Variable.
- The Yes transition uses the existing `sc:Approved` outcome and reaches `Requirements_Acquisition_Completed`.
- The No transition uses `sc:Rejected` and returns to `Create_Detailed_Requirements`. Here rejection means that this review requires revision, not that the project is cancelled.
- A missing decision does not mean No. The reasoner neither selects a branch nor creates an Activity.

The No transition is **not** asserted as reverse P-Plan precedence. That would create a transitive precedence cycle. If rework occurs later, it creates new Activity occurrences corresponding to the same Step definitions. Requirements for ordering apply to the matching occurrences in that pass, not every possible pair of Activities sharing those Step definitions.

The diagram does not say which internal tasks must repeat after rejection. The model leaves that open. Likewise, the expanded Requirements Acquisition phase must reach its approved completion before the outer transition to Technical Design is permitted; no cross-level shortcut is added.

## Deliverables and flow

`Wireframes` and `Use_Cases` are expected deliverable **Variables**, not actual documents. Their producers are the MultiSteps shown in the diagram: `Create_Wireframes` and `Create_Use_Cases`. `Review_Requirements` has both Variables as inputs.

The containing `Create_Detailed_Requirements` MultiStep exposes both through the local `pm:exposes_output_variable` property. This expresses the dotted flow at the enclosing level while retaining one producer per Variable. That matters because `pp:isOutputVarOf` is functional: assigning the same Variable to two producers would cause OWL to equate those producers, or cause inconsistency when they are explicitly different.

Exposure is not another production event and is deliberately not a subproperty of `pp:hasOutputVar`. These Variables are associated with both Plans in which they are exposed or used; `pp:isVariableOfPlan` is not functional. Leaf-level production, actual documents and document versions remain unspecified.

The solid arrow from Create Wireframes to Create Use Cases supplies order only. No Wireframes input to Create Use Cases was invented. Similarly, no extra narrative deliverable was added where the diagram showed none.

## Expected duration

P-Plan has no expected-duration property. The new object property **`pm:expected_duration`** applies to either a Plan or a Step and points to an OWL-Time `time:Duration`. It is optional, and **no estimate values are asserted**.

For illustration only, a future estimate could be expressed as:

```turtle
@prefix mo: <https://www.in2use.com/method_omega/> .
@prefix pm: <https://www.in2use.com/process_model/> .
@prefix time: <http://www.w3.org/2006/time#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

mo:Develop_Wireframes pm:expected_duration [
    a time:Duration ;
    time:numericDuration "6"^^xsd:decimal ;
    time:unitType time:unitHour
] .
```

That means six elapsed hours, not six person-hours. Working-day estimates need a working calendar, and a composite estimate should specify whether it includes rework. No automatic inheritance, summation or scheduling is implied.

The property is not a subproperty of `time:hasDuration`. In the supplied ontology, that property inherits a TemporalEntity domain through `time:hasTemporalDuration`; using it directly for a Plan would add an unintended temporal-entity classification. Reusing OWL-Time's duration representation through a distinct expected-duration relationship preserves the intended distinction.

## Scope and validation

The excerpt is sufficient for the current abstract model. No additional participants, dates or durations are needed at this stage. For project executions we will later need the participating agents, actual/planned timing, decision outcomes and any rework occurrences.

The combined ontology retains the original SULO alignment and reuses the existing transition, decision and task classes. No SHACL shapes, new SWRL rules or Method Omega Activities were added. New IRIs use the In2use slash namespaces, Title_Case_With_Underscores for classes and individuals, and lower_case_with_underscores for properties. Labels replace underscores with spaces. Reused vocabulary IRIs and existing labels remain unchanged.

Validation passed:

- Pellet loaded and classified the combined ontology successfully.
- RDF/XML and Turtle contain isomorphic RDF graphs.
- Existing domain assertions and all ten complete SWRL rules are preserved.
- OWLAPI 4.5.29 loaded, saved and reloaded the RDF/XML with 3,525 axioms and ten nonempty rules at both stages.
- New Plans and Steps remain separate from Activities and temporal entities; no distinct Method Omega nodes were equated.
- All Variables have one producer; precedence has no cycle; the rework edge remains conditional.
- The prior seven tender Activities still produce their expected agent associations and all 49 ordered Allen interval relations.
- All four queries ran successfully on asserted data alone.

The validation JSON records the counts. Local Pellet/OWLAPI checks do not test the installed Protégé UI or Gruff layout.

## Vocabulary references

- [P-Plan specification](https://vocab.linkeddata.es/p-plan/index.html), particularly subplan representation and the property definitions. P-Plan is by Daniel Garijo and Yolanda Gil, licensed CC BY 4.0. The four missing standard terms were copied from its [2014 OWL release](https://dgarijo.github.io/Vocabularies/P-PLAN/Releases/Release12032014/p-plan.owl).
- [OWL-Time](https://www.w3.org/TR/owl-time/), for duration values and units. The merged ontology retains its existing OWL-Time axioms.
- [PROV-O](https://www.w3.org/TR/prov-o/), for the existing execution representation.
