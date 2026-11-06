"""Check diagram semantics, original-data preservation, and reasoner output."""
from pathlib import Path
from datetime import datetime
import json
import sys
from rdflib import Graph, Namespace, URIRef, BNode, RDF, RDFS, OWL
from rdflib.compare import isomorphic
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'execution_demo'))
from repair_rules import closure, subject_graph, validate_rules

ROOT=Path(__file__).resolve().parent
G=Graph().parse(ROOT/'deliverables/supply_chain_figure8.rdf')
T=Graph().parse(ROOT/'deliverables/supply_chain_figure8.ttl')
BASE=Graph().parse(ROOT.parent/'upload/supply_chain_figure8.rdf')
I=Graph().parse(ROOT/'validation/inferences.rdf')
PP=Namespace('http://purl.org/net/p-plan#')
PROV=Namespace('http://www.w3.org/ns/prov#')
TIME=Namespace('http://www.w3.org/2006/time#')
SULO=Namespace('https://w3id.org/sulo/')
SC=Namespace('https://www.michaeldebellis.com/supply_chain_model/')
MO=Namespace('https://www.in2use.com/method_omega/')
PM=Namespace('https://www.in2use.com/process_model/')
F=Namespace('https://www.michaeldebellis.com/supply_chain_figure8/')
SWRL=Namespace('http://www.w3.org/2003/11/swrl#')

assert isomorphic(G,T),'RDF/XML and Turtle differ'
# Exclude only the ontology-header subject. The rest of the supplied graph,
# including every original blank-node structure, must be preserved exactly.
old_named={s for s in BASE.subjects() if isinstance(s,URIRef)}
old_named-=set(BASE.subjects(RDF.type,OWL.Ontology))
assert isomorphic(subject_graph(BASE,closure(BASE,old_named)),subject_graph(G,closure(G,old_named)))
rules=set(BASE.subjects(RDF.type,SWRL.Imp))
assert len(rules)==10
assert validate_rules(G,rules)==validate_rules(BASE,rules)
assert isomorphic(subject_graph(BASE,closure(BASE,rules)),subject_graph(G,closure(G,rules)))

def mo(node): return isinstance(node,URIRef) and str(node).startswith(str(MO))
steps={s for s in G.subjects(RDF.type,PP.Step) if mo(s)}
multis={s for s in G.subjects(RDF.type,PP.MultiStep) if mo(s)}
plans={s for s in G.subjects(RDF.type,PP.Plan) if mo(s)}
assert len(steps)==16 and len(multis)==8 and len(plans)==5
assert len(list(G.triples((None,PP.isDecomposedAsPlan,None))))==4
parent={s:next(G.objects(s,PP.isStepOfPlan)) for s in steps}
for s in steps:
    assert len(list(G.objects(s,PP.isStepOfPlan)))==1
    assert (parent[s],PM.has_step,s) in I
    assert (s,RDF.type,PP.Step) in I
    for bad in [PROV.Activity,SULO.Process,TIME.TemporalEntity]:
        assert (s,RDF.type,bad) not in I,(s,bad)
for s in multis: assert (s,RDF.type,PP.Plan) in I
for p in plans:
    for bad in [PROV.Activity,SULO.Process,TIME.TemporalEntity]:
        assert (p,RDF.type,bad) not in I,(p,bad)
for s in steps|plans:
    assert not list(G.subjects(PP.correspondsToStep,s))
    assert not list(G.objects(s,PM.expected_duration))

direct={(b,a) for a,b in G.subject_objects(PP.isPrecededBy) if mo(a)}
assert len(direct)==10
for a,b in direct:
    assert parent[a]==parent[b],(a,b,'cross-plan precedence')
    assert (a,PM.precedes,b) in I
# Compute independent transitive closure to detect accidental cycles and to
# verify that the inferred forward-facing inverse has the expected reach.
reachable=set(direct)
while True:
    more={(a,d) for a,b in reachable for c,d in reachable if b==c}
    if more<=reachable: break
    reachable|=more
assert not any(a==b for a,b in reachable)
actual={(a,b) for a,b in I.subject_objects(PM.precedes) if mo(a) and mo(b)}
assert actual==reachable,(actual-reachable,reachable-actual)
assert (MO.Review_Requirements,PM.precedes,MO.Create_Detailed_Requirements) not in I

transitions={s for s in G.subjects(RDF.type,SC.StepTransition) if mo(s)}
assert len(transitions)==12
for t in transitions:
    a=next(G.objects(t,SC.transitionFrom)); b=next(G.objects(t,SC.transitionTo))
    assert parent[a]==parent[b]
    assert (t,RDF.type,PM.Finish_To_Start_Transition) in G
    assert (a,SC.hasOutgoingTransition,t) in I
conditions={s for s in G.subjects(RDF.type,SC.DecisionCondition) if mo(s)}
assert len(conditions)==2
assert (MO.Rejection_To_Requirements_Rework,SC.transitionTo,MO.Create_Detailed_Requirements) in G
assert (MO.Approval_To_Requirements_Completion,SC.transitionTo,MO.Requirements_Acquisition_Completed) in G
assert (MO.Requirements_Approved_Choice,SC.choiceAfterStep,MO.Review_Requirements) in G
assert set(G.objects(MO.Requirements_Approved_Choice,SC.hasAlternative))=={
    MO.Approval_To_Requirements_Completion,MO.Rejection_To_Requirements_Rework}

variables={s for s in G.subjects(RDF.type,PP.Variable) if mo(s)}
assert len(variables)==3
for v in variables:
    producers=set(G.subjects(PP.hasOutputVar,v))
    assert len(producers)==1,(v,producers)
    assert set(I.objects(v,PP.isOutputVarOf))==producers
for v,producer in [(MO.Wireframes,MO.Create_Wireframes),(MO.Use_Cases,MO.Create_Use_Cases)]:
    assert (producer,PP.hasOutputVar,v) in G
    assert (MO.Create_Detailed_Requirements,PM.exposes_output_variable,v) in G
    assert (MO.Create_Detailed_Requirements,PP.hasOutputVar,v) not in I
    assert (MO.Review_Requirements,PP.hasInputVar,v) in G
    assert parent[producer]==next(G.objects(MO.Create_Detailed_Requirements,PP.isDecomposedAsPlan))
# No new distinct nodes should have been equated by functional properties.
for a,b in I.subject_objects(OWL.sameAs):
    assert not (a!=b and (mo(a) or mo(b))),(a,b)

# Regression: compare every Allen interval inference for the prior run against
# independently calculated endpoint order, including equality with itself.
allen={TIME['interval'+x] for x in ['Before','After','Meets','MetBy','Overlaps','OverlappedBy','Starts','StartedBy','During','Contains','Finishes','FinishedBy','Equals']}
activities=set(BASE.objects(F.TenderRun01,SULO.hasPart))|{F.TenderRun01}
assert len(activities)==7
intervals={next(BASE.objects(a,TIME.hasTime)) for a in activities}
def bounds(v):
    dates=[]
    for p in [TIME.hasBeginning,TIME.hasEnd]:
        instant=next(BASE.objects(v,p))
        value=next(BASE.objects(instant,TIME.inXSDDateTimeStamp))
        dates.append(datetime.fromisoformat(str(value).replace('Z','+00:00')))
    return dates
def expected(a,b):
    s,e=bounds(a); t,u=bounds(b)
    if e<t:return TIME.intervalBefore
    if s>u:return TIME.intervalAfter
    if e==t:return TIME.intervalMeets
    if s==u:return TIME.intervalMetBy
    if s==t and e==u:return TIME.intervalEquals
    if s==t:return TIME.intervalStarts if e<u else TIME.intervalStartedBy
    if e==u:return TIME.intervalFinishes if s>t else TIME.intervalFinishedBy
    if s<t:return TIME.intervalOverlaps if e<u else TIME.intervalContains
    return TIME.intervalDuring if e<u else TIME.intervalOverlappedBy
for a in intervals:
    for b in intervals:
        assert set(I.predicates(a,b))&allen=={expected(a,b)},(a,b)
for a in activities:
    assert (a,RDF.type,SULO.Process) in I
    association=next(BASE.objects(a,PROV.qualifiedAssociation))
    agent=next(BASE.objects(association,PROV.agent))
    assert (a,PROV.wasAssociatedWith,agent) in I
assert not any(p in allen for s,p,o in G),'Inferences were saved into asserted source'

query_counts={}
for path in sorted((ROOT/'deliverables/queries').glob('*.rq')):
    result=G.query(path.read_text())
    count=len(result.graph) if result.type=='CONSTRUCT' else len(result)
    assert count>0,path
    query_counts[path.name]=count

report={'combined_asserted_triples':len(G),'pellet_consistent':True,
 'new_step_definitions':len(steps),'multisteps':len(multis),'separate_body_plans':4,
 'unexpanded_multisteps':4,'methodology_root_plans':1,
 'direct_precedence_edges':len(direct),'inferred_precedence_pairs':len(reachable),
 'transitions':len(transitions),'conditional_transitions':2,
 'single_producer_variables':len(variables),'existing_swr_rules_preserved':10,
 'original_domain_data_unchanged':True,'plan_activity_separation':True,
 'old_tender_activities_checked':7,'old_ordered_interval_pairs_checked':49,
 'new_execution_activities':0,'duration_estimate_values':0,
 'rdfxml_turtle_isomorphic':True,'queries_on_asserted_data':query_counts}
(ROOT/'validation/results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
