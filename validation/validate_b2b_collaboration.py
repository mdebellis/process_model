"""Reproduce B2B query checks against source plus materialized entailments.

Usage: python validation/validate_b2b_collaboration.py SOURCE.rdf ENTAILMENTS.nt
Requires RDFLib. ENTAILMENTS.nt must be generated from that source by a reasoner
supporting the retained OWL/SWRL axioms. This script does not execute SWRL.
"""
from pathlib import Path
import argparse
import json
import hashlib
import re
from datetime import datetime
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, URIRef, Literal

PM=Namespace('https://in2use.com/process_model/')
PP=Namespace('http://purl.org/net/p-plan#')
PROV=Namespace('http://www.w3.org/ns/prov#')
SULO=Namespace('https://w3id.org/sulo/')
TIME=Namespace('http://www.w3.org/2006/time#')
SKOS=Namespace('http://www.w3.org/2004/02/skos/core#')

def ask(graph, state, *, run, as_of):
    """Raw evidence result, with required caller bindings validated first."""
    if not isinstance(run,URIRef) or not str(run).startswith(('https://','http://')):
        raise ValueError('run must be an explicit absolute IRI')
    if not isinstance(as_of,Literal) or as_of.datatype!=XSD.dateTime:
        raise ValueError('as_of must be an explicit xsd:dateTime literal')
    instant=datetime.fromisoformat(str(as_of).replace('Z','+00:00'))
    if instant.tzinfo is None:raise ValueError('as_of must include a timezone')
    test=graph.value(state,PM.has_state_test)
    if test is None:raise ValueError('No state test is available; do not invent an evaluation')
    query=graph.value(test,PM.has_sparql_query)
    if query is None:raise ValueError('No executable SPARQL test is available')
    outcomes=set(graph.objects(PM.Lavatory_Frame_Transfer_Decision_01,PM.has_outcome))
    if len(outcomes)>1:raise ValueError('Conflicting decision evidence requires review; do not map ASK to a truth category')
    return bool(graph.query(str(query),initBindings={'run':run,'as_of':as_of}).askAnswer)

def check(source,entailments,repo):
    asserted=Graph().parse(source,format='xml')
    graph=Graph()
    for t in asserted:graph.add(t)
    graph.parse(entailments,format='nt')
    assert (PM.Lavatory_Collaboration_Execution,SULO.hasPart,PM.Lavatory_Transfer_Frame_Execution) in graph, 'Missing hasPart inferences'
    cutoff=lambda t:Literal(t,datatype=XSD.dateTime)
    run=PM.Lavatory_Collaboration_Execution
    def evaluate(key,t,g=graph,r=run):return ask(g,PM['Lavatory_'+key],run=r,as_of=cutoff(t))
    checks=[]
    def ok(name,condition):
        assert condition,name
        checks.append(name)
    # Replay every recorded synthetic evaluation, with the recorded time cutoff.
    evaluations=[]
    for e in asserted.subjects(PM.has_evaluated_execution,run):
        state=asserted.value(predicate=PM.has_state_evaluation,object=e)
        value=ask(graph,state,run=run,as_of=asserted.value(e,PM.has_evaluation_time))
        expected=asserted.value(e,PM.has_evaluation_result)==PM.Satisfied
        ok('Replay '+str(e).split('/')[-1],value==expected)
        at=datetime.fromisoformat(str(asserted.value(e,PM.has_evaluation_time)))
        for evidence in asserted.objects(e,PM.has_evidence):
            when=asserted.value(evidence,PROV.generatedAtTime)
            if when:ok('Evidence predates '+str(e).split('/')[-1]+' / '+str(evidence).split('/')[-1],datetime.fromisoformat(str(when))<=at)
        evaluations.append({'evaluation':str(e),'satisfied':value})
    ok('Eight synthetic evaluations replayed',len(evaluations)==8)
    ok('Manufactured before available',evaluate('Frame_Manufactured','2027-03-03T09:00:00Z') and not evaluate('Frame_Available','2027-03-03T09:00:00Z'))
    ok('No receipt before its event time',not evaluate('Frame_Available','2027-03-03T12:59:59Z'))
    ok('Receipt established at its event time',evaluate('Frame_Available','2027-03-03T13:00:00Z'))
    ok('Assembly enabled after transfer',evaluate('Assembly_Inputs_Ready','2027-03-03T13:05:00Z'))
    ok('Manufacture not completed early',not evaluate('Frame_Manufactured','2027-03-02T16:59:59Z'))
    ok('Different run cannot borrow evidence',not evaluate('Frame_Available','2027-03-04T12:00:00Z',r=PM.Customer_Portal_Execution))
    def clone():
        g=Graph()
        for t in graph:g.add(t)
        return g
    for predicate,wrong,name in [(PM.has_received_resource,PM.Lavatory_Transport_Cover_01,'Wrong received resource'),(PM.has_receiving_agent,PM.Exec_Co,'Wrong receipt recipient')]:
        probe=clone();probe.set((PM.Lavatory_Frame_Receipt_01,predicate,wrong))
        ok(name+' blocks readiness',not evaluate('Assembly_Inputs_Ready','2027-03-04T12:00:00Z',g=probe))
    probe=clone();probe.remove((PM.Lavatory_Other_Components_Receipt_01,PM.has_received_resource,None))
    ok('Missing other components blocks conjunction',not evaluate('Assembly_Inputs_Ready','2027-03-04T12:00:00Z',g=probe))
    probe=clone();probe.set((PM.Lavatory_Frame_Transfer_Decision_01,PM.has_outcome,PM.Rejected))
    ok('Rejected proposal does not authorize transfer',not evaluate('Frame_Available','2027-03-04T12:00:00Z',g=probe))
    probe=clone();probe.set((PM.Lavatory_Frame_Transfer_Decision_01,PM.has_subject_version,PM.Portal_Project_Narrative_V1))
    ok('Approval for another proposal is insufficient',not evaluate('Frame_Available','2027-03-04T12:00:00Z',g=probe))
    for run_arg,at_arg in [(None,cutoff('2027-03-04T12:00:00Z')),(run,None),(run,Literal('2027-03-04T12:00:00',datatype=XSD.dateTime))]:
        try:ask(graph,PM.Lavatory_Frame_Available,run=run_arg,as_of=at_arg)
        except ValueError:checks.append('Invalid/missing caller binding rejected')
        else:raise AssertionError('Invalid binding accepted')
    probe=clone();probe.add((PM.Lavatory_Frame_Transfer_Decision_01,PM.has_outcome,PM.Rejected))
    try:evaluate('Frame_Available','2027-03-04T12:00:00Z',g=probe)
    except ValueError:checks.append('Conflicting evidence rejected before ASK categorization')
    else:raise AssertionError('Conflicting outcomes silently accepted')
    # A hypothetical completed continuation is a test fixture, never saved to the ontology.
    probe=clone();module=PM.Probe_Module;delivery=PM.Probe_Delivery;receipt=PM.Probe_Delivery_Receipt
    probe.add((PM.Lavatory_Assemble_Module_Execution,PROV.endedAtTime,cutoff('2027-03-05T12:00:00Z')))
    for t in [(module,RDF.type,PM.Lavatory_Module),(module,PP.correspondsToVariable,PM.Lavatory_Module_Var),(module,PROV.wasGeneratedBy,PM.Lavatory_Assemble_Module_Execution),(module,PROV.generatedAtTime,cutoff('2027-03-05T12:00:00Z')),(run,SULO.hasPart,delivery),(delivery,PP.correspondsToStep,PM.Lavatory_Deliver_Module),(delivery,PROV.used,module),(delivery,PROV.used,PM.Lavatory_Transport_Cover_01),(delivery,PROV.endedAtTime,cutoff('2027-03-05T17:00:00Z')),(receipt,RDF.type,PM.Resource_Receipt),(receipt,PP.correspondsToVariable,PM.Lavatory_Delivery_Receipt_Var),(receipt,PROV.wasGeneratedBy,delivery),(receipt,PROV.generatedAtTime,cutoff('2027-03-05T17:00:00Z')),(receipt,PM.has_received_resource,module),(receipt,PM.has_receiving_agent,PM.Aerospace_Customer)]:probe.add(t)
    ok('Completed continuation satisfies parent goal',evaluate('Module_Delivered','2027-03-05T17:00:00Z',g=probe))
    probe.set((receipt,PM.has_received_resource,PM.Lavatory_Frame_01))
    ok('Delivery of wrong resource does not satisfy parent goal',not evaluate('Module_Delivered','2027-03-05T17:00:00Z',g=probe))
    # Check every started Activity against each of its specified preconditions at start.
    activity_checks=[]
    for activity in graph.objects(run,SULO.hasPart):
        step=graph.value(activity,PP.correspondsToStep)
        if step is None:continue
        at=graph.value(activity,PROV.startedAtTime)
        for state in asserted.objects(step,PM.has_precondition):
            answer=ask(graph,state,run=run,as_of=at)
            ok('Start precondition '+str(activity).split('/')[-1]+' / '+str(state).split('/')[-1],answer)
            activity_checks.append({'activity':str(activity),'state':str(state),'satisfied_at_start':answer})
    query_results=[]
    for path in sorted((repo/'queries/b2b_collaboration').glob('*.rq')):
        result=graph.query(path.read_text())
        if result.type=='CONSTRUCT':
            rows=set(result.graph)
            ok('Existing edges only: '+path.name,all(t in graph for t in rows))
        else:rows=list(result)
        query_results.append({'query':path.name,'results':len(rows),'kind':result.type})
        if path.name.startswith('02_'):
            expected={(s,p,o) for s,p,o in asserted if str(s).startswith(str(PM)+'Lavatory_') and p==PM.has_sub_goal}
            ok('Seven goal-decomposition edges returned',rows==expected and len(rows)==7)
        if path.name.startswith('05_'):ok('Seven planned steps in comparison',len(rows)==7)
        if path.name.startswith('05b_'):
            ok('Plan/actual graph includes seven steps and six correspondences',
               len(rows)==24 and sum(p==PM.has_step for s,p,o in rows)==7
               and sum(p==PP.correspondsToStep for s,p,o in rows)==6)
        if path.name.startswith('06_'):ok('Eight assessments in table',len(rows)==8)
        if path.name.startswith('07_'):ok('Six recorded operational Activities',len(rows)==6)
        if path.name.startswith('09_'):ok('No expected-type mismatches',len(rows)==0)
        print(path.name, len(rows), flush=True)
    states_checked=[]
    expected_true={'frame_design_ready','frame_manufactured','cover_ready','frame_transfer_arranged','frame_available','other_components_available','assembly_inputs_ready'}
    for path in sorted((repo/'queries/b2b_collaboration/state_tests').glob('*.rq')):
        answer=bool(graph.query(path.read_text()).askAnswer)
        ok('Runnable state test '+path.stem,answer==(path.stem in expected_true))
        states_checked.append({'query':path.name,'satisfied':answer})
    for s in asserted.subjects(RDF.type,OWL.NamedIndividual):
        if str(s).startswith(str(PM)+'Lavatory_') and (s,RDF.type,PP.Variable) in graph:
            expected=asserted.value(s,PM.has_expected_type)
            if expected:ok('Variable not typed as expected artifact: '+str(s).split('/')[-1],(s,RDF.type,expected) not in graph)
    ok('No pre-created delivery Activity',not list(graph.subjects(PP.correspondsToStep,PM.Lavatory_Deliver_Module)))
    ok('No fabricated completed module',not list(graph.subjects(PP.correspondsToVariable,PM.Lavatory_Module_Var)))
    ok('No reflexive root parthood',(run,SULO.hasPart,run) not in graph)
    result={'date':'2026-11-24','source':str(source.name),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_triples':len(asserted),'materialized_test_graph_triples':len(graph),'query_engine':'RDFLib','passed':True,'check_count':len(checks),'checks':checks,'state_evaluations':evaluations,'preconditions_at_actual_starts':activity_checks,'demonstration_queries':query_results,'state_test_queries':states_checked,'limits':['Synthetic scenario; dates and detailed operational choices are illustrative.','False is Unsatisfied only under the documented complete and unambiguous evidence contract; otherwise Unknown.','No live AllegroGraph/Gruff execution or LLM invocation.','Receipt-based availability assumes no withdrawal, revocation, consumption or competing allocation before assembly.','T1-T5 design-method execution, supplier matching, shared-input allocation and shared-output iterations remain future extensions.']}
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('entailments',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();repo=Path(__file__).resolve().parents[1]
    result=check(args.source,args.entailments,repo)
    text=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(text)
    print('Passed',result['check_count'],'checks.',flush=True)
