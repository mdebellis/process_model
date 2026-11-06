"""Add Michael's Method Omega diagram to the supplied, asserted ontology."""
from pathlib import Path
import json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, BNode, URIRef, Literal
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'deliverables'
OUT.mkdir(exist_ok=True)
SOURCE = ROOT.parent / 'upload/supply_chain_figure8.rdf'
g = Graph().parse(SOURCE)
original = set(g)
PP = Namespace('http://purl.org/net/p-plan#')
PROV = Namespace('http://www.w3.org/ns/prov#')
TIME = Namespace('http://www.w3.org/2006/time#')
SC = Namespace('https://www.michaeldebellis.com/supply_chain_model/')
PM = Namespace('https://www.in2use.com/process_model/')
MO = Namespace('https://www.in2use.com/method_omega/')
DC = Namespace('http://purl.org/dc/terms/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
for prefix, ns in [('pp', PP), ('prov', PROV), ('time', TIME), ('sc', SC), ('pm', PM), ('mo', MO)]:
    g.bind(prefix, ns, override=True, replace=True)

def en(text): return Literal(text, lang='en')
def note(node, text): g.add((node, RDFS.comment, en(text)))
def label(node):
    text = str(node).rsplit('/', 1)[-1].replace('_', ' ')
    g.add((node, RDFS.label, en(text)))
    g.add((node, SKOS.prefLabel, en(text)))

# The retained P-Plan subset lacked these four standard terms. Copy their
# original axioms, without changing any reused IRI or existing declaration.
reference = Graph().parse(ROOT / 'p-plan-2014.owl')
for name in ['MultiStep', 'isDecomposedAsPlan', 'isSubPlanOfPlan', 'isPrecededBy']:
    for triple in reference.triples((PP[name], None, None)):
        g.add(triple)
for name, text in [('MultiStep', 'MultiStep'), ('isDecomposedAsPlan', 'is decomposed as plan'),
                   ('isSubPlanOfPlan', 'is subplan of plan'), ('isPrecededBy', 'is preceded by')]:
    g.add((PP[name], SKOS.prefLabel, en(text)))

def term(name, kind, comment):
    node = PM[name]
    g.add((node, RDF.type, kind)); label(node); note(node, comment)
    g.add((node, RDFS.isDefinedBy, URIRef(str(PM))))
    return node

has_step = term('has_step', OWL.ObjectProperty,
    'Inverse of p-plan:isStepOfPlan, for displaying Plan-to-Step membership. This relation is not transitive; a MultiStep is linked to its separate decomposition Plan with p-plan:isDecomposedAsPlan.')
g.add((has_step, OWL.inverseOf, PP.isStepOfPlan))
g.add((has_step, RDFS.domain, PP.Plan)); g.add((has_step, RDFS.range, PP.Step))
precedes = term('precedes', OWL.ObjectProperty,
    'Inverse of p-plan:isPrecededBy. This is planned precedence, not a timestamp relation between actual Activities. Immediate possible control-flow edges are modeled separately as StepTransitions.')
g.add((precedes, OWL.inverseOf, PP.isPrecededBy))
g.add((precedes, RDFS.domain, PP.Step)); g.add((precedes, RDFS.range, PP.Step))
exposes = term('exposes_output_variable', OWL.ObjectProperty,
    'Links a MultiStep to an output Variable produced by a Step in its decomposition and made available to consumers outside that decomposition. This exposes the same planned slot; it neither asserts another producer nor creates another artifact. Deliberately not a subproperty of p-plan:hasOutputVar, whose inverse is functional.')
g.add((exposes, RDFS.domain, PP.MultiStep)); g.add((exposes, RDFS.range, PP.Variable))
expected = term('expected_duration', OWL.ObjectProperty,
    'An estimate of the elapsed duration of an execution described by a Plan or Step, represented as an OWL-Time Duration with a numeric value and unit. It is not actual elapsed time, labor effort, or an implicit working-calendar calculation. State separately whether a composite estimate includes rework. No default inheritance or roll-up arithmetic is implied.')
union = BNode(); members = BNode()
g.add((union, RDF.type, OWL.Class)); g.add((union, OWL.unionOf, members))
Collection(g, members, [PP.Plan, PP.Step])
g.add((expected, RDFS.domain, union)); g.add((expected, RDFS.range, TIME.Duration))
fst = term('Finish_To_Start_Transition', OWL.Class,
    'A planned possible transition that, when selected, requires the source Activity occurrence to have completed by the time the target occurrence starts. No overlap is permitted; zero waiting time is permitted. Applies to the particular occurrences connected by that transition, including a later iteration of a loop. This declaration neither executes a transition nor infers actual interval relations.')
g.add((fst, RDFS.subClassOf, SC.StepTransition))

individuals = []
def named(name, *classes):
    node = MO[name]
    individuals.append(node)
    g.add((node, RDF.type, OWL.NamedIndividual)); label(node)
    for cls in classes: g.add((node, RDF.type, cls))
    return node

root = named('Method_Omega', PP.Plan)
note(root, 'Reusable Method Omega development methodology, transcribed from Michael DeBellis\'s supplied diagram. This excerpt expands Requirements Acquisition only. No project-specific plan, execution, participant assignment, scheduled date, or duration estimate is asserted.')
g.add((root, SKOS.scopeNote, en('Horizontal solid arrows are finish-to-start requirements. The No branch is a possible rework transition, not an unconditional reverse precedence assertion. Precedence applies to the matching pass through the plan, not every pair of Activities sharing the source and target Step definitions. Unspecified dependencies do not assert concurrency.')))

plan_names = ['Requirements_Acquisition_Plan', 'Create_Detailed_Requirements_Plan',
              'Create_Wireframes_Plan', 'Create_Use_Cases_Plan']
for name in plan_names: named(name, PP.Plan)

# Columns: contextual Step, containing Plan, MultiStep flag, optional body Plan.
rows = [
 ('Requirements_Acquisition','Method_Omega',True,'Requirements_Acquisition_Plan'),
 ('Technical_Design','Method_Omega',True,None),
 ('Implementation','Method_Omega',True,None),
 ('Testing','Method_Omega',True,None),
 ('Rollout','Method_Omega',True,None),
 ('Kickoff_Meeting','Requirements_Acquisition_Plan',False,None),
 ('Create_Project_Narrative','Requirements_Acquisition_Plan',False,None),
 ('Create_Detailed_Requirements','Requirements_Acquisition_Plan',True,'Create_Detailed_Requirements_Plan'),
 ('Review_Requirements','Requirements_Acquisition_Plan',False,None),
 ('Requirements_Acquisition_Completed','Requirements_Acquisition_Plan',False,None),
 ('Create_Wireframes','Create_Detailed_Requirements_Plan',True,'Create_Wireframes_Plan'),
 ('Create_Use_Cases','Create_Detailed_Requirements_Plan',True,'Create_Use_Cases_Plan'),
 ('User_Wireframe_Interviews','Create_Wireframes_Plan',False,None),
 ('Develop_Wireframes','Create_Wireframes_Plan',False,None),
 ('Use_Case_Interviews','Create_Use_Cases_Plan',False,None),
 ('Write_Use_Cases','Create_Use_Cases_Plan',False,None),
]
for name, parent, multi, body in rows:
    cls = SC.EndEventStep if name == 'Requirements_Acquisition_Completed' else SC.TaskStep
    step = named(name, PP.Step, cls, *([PP.MultiStep] if multi else []))
    g.add((step, PP.isStepOfPlan, MO[parent]))
    if body:
        g.add((step, PP.isDecomposedAsPlan, MO[body]))
        g.add((MO[body], PP.isSubPlanOfPlan, MO[parent]))
        note(MO[body], 'Reusable decomposition of '+name.replace('_',' ')+'. The contextual MultiStep retains its position and dependencies in its containing Plan.')
    elif multi:
        note(step, 'Unexpanded MultiStep in the supplied excerpt. Its detailed decomposition is intentionally unspecified; no empty or invented body Plan is asserted.')
note(MO.Requirements_Acquisition_Completed, 'Planned completion event reached only on approval. It belongs to Requirements Acquisition Plan. Completing the containing Requirements Acquisition MultiStep enables Technical Design at the outer level; no unconditional cross-level shortcut is added.')
note(MO.Review_Requirements, 'Review uses the Wireframes and Use Cases exposed by Create Detailed Requirements and produces the decision for the exclusive choice. Rejection returns to Create Detailed Requirements for another pass. The diamond is the choice, not an extra work Step.')

edges = [
 ('Requirements_Acquisition','Technical_Design'),
 ('Technical_Design','Implementation'),
 ('Implementation','Testing'),
 ('Testing','Rollout'),
 ('Kickoff_Meeting','Create_Project_Narrative'),
 ('Create_Project_Narrative','Create_Detailed_Requirements'),
 ('Create_Detailed_Requirements','Review_Requirements'),
 ('Create_Wireframes','Create_Use_Cases'),
 ('User_Wireframe_Interviews','Develop_Wireframes'),
 ('Use_Case_Interviews','Write_Use_Cases'),
]
def transition(name, a, b, condition=None):
    t = named(name, fst, SC.StepTransition, *([SC.ConditionalTransition] if condition else []))
    g.add((t, SC.transitionFrom, MO[a])); g.add((t, SC.transitionTo, MO[b]))
    if condition: g.add((t, SC.hasCondition, MO[condition]))
    return t
for a, b in edges:
    transition(a+'_To_'+b, a, b)
    g.add((MO[b], PP.isPrecededBy, MO[a]))

# Keep the single producing MultiStep shown for each circular deliverable.
# The containing MultiStep exposes it rather than becoming a second producer.
for name, producer in [('Wireframes','Create_Wireframes'), ('Use_Cases','Create_Use_Cases')]:
    v = named(name, PP.Variable)
    g.add((MO[producer], PP.hasOutputVar, v))
    g.add((MO.Review_Requirements, PP.hasInputVar, v))
    g.add((MO.Create_Detailed_Requirements, exposes, v))
    for plan in ['Create_Detailed_Requirements_Plan','Requirements_Acquisition_Plan']:
        g.add((v, PP.isVariableOfPlan, MO[plan]))
    note(v, 'Expected '+name.replace('_',' ')+' deliverable slot. Its asserted producer is the '+producer.replace('_',' ')+' MultiStep, as drawn. It is exposed by the containing MultiStep for review. Production by individual leaf Steps and actual document versions are not specified in this excerpt.')
decision = named('Requirements_Review_Decision', SC.DecisionVariable, PP.Variable)
g.add((decision, PP.isVariableOfPlan, MO.Requirements_Acquisition_Plan))
g.add((MO.Review_Requirements, PP.hasOutputVar, decision))
note(decision, 'Planned decision slot introduced to express the diagram\'s Yes/No conditions. It is not an actual recorded approval or rejection.')
for name, outcome in [('Requirements_Approved_Condition',SC.Approved),
                       ('Requirements_Not_Approved_Condition',SC.Rejected)]:
    c = named(name, SC.DecisionCondition)
    g.add((c, SC.conditionVariable, decision)); g.add((c, SC.expectedOutcome, outcome))
note(MO.Requirements_Not_Approved_Condition, 'The diagram\'s No outcome is represented using the existing Rejected value. Here it means revision is required at this review, not that the project is cancelled. A missing decision does not mean No.')
yes = transition('Approval_To_Requirements_Completion','Review_Requirements',
                 'Requirements_Acquisition_Completed','Requirements_Approved_Condition')
no = transition('Rejection_To_Requirements_Rework','Review_Requirements',
                'Create_Detailed_Requirements','Requirements_Not_Approved_Condition')
choice = named('Requirements_Approved_Choice', SC.ExclusiveChoice)
g.add((choice, SC.choiceAfterStep, MO.Review_Requirements))
g.add((choice, SC.hasAlternative, yes)); g.add((choice, SC.hasAlternative, no))
note(choice, 'The diagram\'s Requirements Approved? diamond. Yes leads to completion; No leads to a new pass through Create Detailed Requirements and review. A reasoner does not evaluate the condition or create Activities. The exact set of leaf Steps repeated on revision is left unspecified.')

different = BNode(); head = BNode()
g.add((different, RDF.type, OWL.AllDifferent)); g.add((different, OWL.distinctMembers, head))
Collection(g, head, individuals)

ontology = next(g.subjects(RDF.type, OWL.Ontology))
updates = {
 RDFS.label: en('Process modeling examples: tendering and Method Omega'),
 DC.title: en('Process modeling examples: collaborative tendering and Method Omega development'),
 DC.description: en('Self-contained experimental ontology containing the Figure 8 tendering Plan and its synthetic execution, plus the abstract Method Omega development methodology excerpt. Existing tendering assertions, vocabulary IRIs, SULO alignments and ten SWRL rules are retained. Method Omega adds nested P-Plan definitions, finish-to-start transitions, expected deliverable slots and an approval/rework choice. No Method Omega executions or estimate values are included.'),
 DC.modified: Literal('2026-11-06', datatype=XSD.date),
 OWL.versionInfo: Literal('figure8-and-method-omega-v1-2026-11-06'),
 SKOS.scopeNote: en('Figure 8 plan content follows the cited paper and its accompanying text; the dated tender run is explicitly synthetic. Method Omega follows Michael DeBellis\'s supplied diagram and conventions, with modeling choices explained on its individuals. Existing Time examples remain. These are review examples, not a workflow engine or records of real projects.'),
}
for prop, value in updates.items(): g.set((ontology, prop, value))
g.add((ontology, SKOS.changeNote, en('2026-11-06 (ChatGPT): Added the Method Omega excerpt in the https://www.in2use.com/method_omega/ namespace, preserving existing domain data and all ten SWRL rules. Copied four missing standard P-Plan terms from the 2014 release. Added has_step and precedes display inverses, Finish_To_Start_Transition, exposes_output_variable, and expected_duration in https://www.in2use.com/process_model/. Kept separate MultiSteps and body Plans, single producers for Variables, and conditional rework without a precedence cycle. No Method Omega Activities, duration values, SHACL constraints or materialized inferences added. Updated ontology-level descriptive metadata; retained the ontology IRI.')))

# Unrelated source assertions must all survive. Only the listed ontology
# annotation properties are intentionally replaced.
removed = original-set(g)
assert all(s == ontology and p in updates for s,p,o in removed), removed
g.serialize(OUT/'supply_chain_figure8.rdf', format='xml')
g.serialize(OUT/'supply_chain_figure8.ttl', format='turtle')
delta = Graph()
for prefix, ns in g.namespaces(): delta.bind(prefix, ns)
for triple in set(g)-original: delta.add(triple)
delta.serialize(OUT/'method_omega_additions.ttl',format='turtle')
manifest = {'source_triples':len(original),'combined_triples':len(g),
 'new_triples':len(set(g)-original),'replaced_metadata_triples':len(removed),
 'ordinary_plans':len(plan_names)+1,'steps':len(rows),'multisteps':sum(r[2] for r in rows),
 'expanded_multisteps':sum(bool(r[3]) for r in rows),'variables':3,
 'transitions':len(edges)+2,'conditional_transitions':2,'direct_precedence_edges':len(edges),
 'new_individuals':len(individuals),'step_inventory':rows,'direct_precedence':edges,
 'ontology_iri':str(ontology),'source_file':SOURCE.name}
(ROOT/'build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k not in ['step_inventory','direct_precedence']},indent=2))
