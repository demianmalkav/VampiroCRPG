#!/usr/bin/env python3
"""Validate archived pickup/ownership scope without rerunning CE."""
import argparse
import hashlib
import json
from pathlib import Path
from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA, require
from check_ce_container_evidence import private_content_absent
ITEM=(200,4)
def ident(obj):return (obj['id'],obj['pid']) if obj else None
def anim(obj):return (obj['fid']>>16)&255
def ground(s):return s['watched_owner'] is None and s['watched_on_map'] and s['watched_item']['tile']==12477
def owned(s):
    slots=[x for x in s['actor_inventory'] if ident(x['object'])==ITEM]
    return ident(s['watched_owner'])==ident(s['dude']) and not s['watched_on_map'] and s['watched_item']['tile']==-1 and len(slots)==1 and slots[0]['quantity']==1 and ident(slots[0]['owner'])==ident(s['dude'])
def check(data):
    require(data['a2_08']=='REFERENCE_PARTIAL' and data['vampiro_status']=='NOT_VERIFIED' and data['effect_boundary_status']=='SAMPLED_TRANSITION_ONLY','Scope overclaim')
    private_content_absent(data)
    require(data['reference']['map_sha256']=='c293b1652f71f518f5e92915a1676ecb5ad75cf33f93a0d9db30de6fb53236db' and data['reference']['observed_initial_tile']==13292,'Wrong map fixture')
    require(len(data['runs'])==2 and {r['scenario'] for r in data['runs']}=={'complete','cancel'},'Missing contrasting run')
    total=0
    for run in data['runs']:
        require(run['completed'] and run['ce_revision']==CE_REVISION and run['binary_sha256']==ELF_SHA,'Reference identity mismatch')
        require(run['input_hashes']==INPUTS and run['original_inputs_unchanged']=={n:True for n in INPUTS},'DAT preservation mismatch')
        require(run['controller_sha256']==data['measured_source_hashes'][run['controller_path']] and run['adapter_source_sha256']==data['measured_source_hashes']['tools/research/ce_pickup_input.cc'],'Probe identity mismatch')
        require('StartingMap=DENBUS1.MAP' in run['configs']['ddraw.ini'] and all(hashlib.sha256(v.encode()).hexdigest()==run['configs_sha256'][k] for k,v in run['configs'].items()),'Config identity mismatch')
        cases={c['label']:c for c in run['cases']};initial=cases['original-ground-item-fixture']['initial'];case=cases['pickup-complete'];records=run['native_pose_changes']
        require(initial['dude']['tile']==13292 and ident(initial['watched_item'])==ITEM and initial['watched_portable'] and initial['watched_type']==3 and ground(initial) and initial['actor_inventory']==[],'Wrong initial item or owner')
        require(ident(case['before']['selected_object'])==ITEM and case['before']['mouse_mode']==1 and ground(case['before']),'Wrong pickup selection')
        require(case['before']['sequence']<case['release']['sequence']<case['effect']['sequence']<case['after']['sequence'],'Input chronology regressed')
        require(owned(case['effect']) and owned(case['after']),'Ownership/map transition missing or duplicated')
        lo,hi=case['before']['sequence'],case['after']['sequence'];scope=[r for r in records if lo<=r['input_sequence']<=hi]
        require(scope and all(ident(r['watched_item'])==ITEM and r['blocker_at_actor'] is None for r in scope),'Missing target log or occupied actor')
        gestures=[r for r in scope if anim(r['dude'])==10]
        require(set(range(9))<={r['dude']['frame'] for r in gestures},'Ground gesture incomplete')
        require(all(r['watched_distance']==1 and ground(r) for r in gestures if r['dude']['frame']<=6),'Premature ownership or absent proximity')
        require(any(r['dude']['frame']==7 and owned(r) for r in gestures) and all(owned(r) for r in gestures if r['dude']['frame']>=7),'Observed transition frame differs')
        first=next(i for i,r in enumerate(scope) if owned(r));require(all(ground(r) for r in scope[:first]) and all(owned(r) for r in scope[first:]),'Ownership reversal or unobserved transition')
        require(all(a['sdl_tick_ms']<=b['sdl_tick_ms'] and a['input_sequence']<=b['input_sequence'] for a,b in zip(records,records[1:])),'Native chronology regressed')
        repeat=cases['former-pixel-repeat'];require(owned(repeat['before']) and owned(repeat['after']) and ident(repeat['before']['selected_object'])!=ITEM,'Second UI click duplicated item')
        if run['scenario']=='cancel':
            c=cases['pickup-cancel-approach'];inter=c['interrupt'];trigger=inter['trigger']
            require(anim(trigger['dude']) in (1,19) and (trigger['dude']['x'] or trigger['dude']['y']) and ground(trigger),'Interruption not during approach')
            require(inter['verified']['mouse_mode']==0 and inter['verified']['cursor_tile_before']==inter['target']['requested_tile']==inter['target']['roundtrip_tile']==13292,'Cancel movement unverified')
            require(c['before']['sequence']<trigger['sequence']<inter['release']['sequence']<c['after']['sequence']<case['before']['sequence'],'Cancel/retry chronology invalid')
            states=[c['before'],trigger,inter['release'],c['after']]+inter['samples'];require(all(ground(s) and s['actor_inventory']==[] for s in states),'Cancelled pickup transferred item')
            require(c['after']['dude']['tile']==13292 and anim(c['after']['dude'])==0,'Cancel arrival unmeasured')
            extra=cases['retry-second-ui-click'];require(case['release']['sequence']<extra['before']['sequence']<extra['release']['sequence']<case['effect']['sequence'],'Additional retry click unrecorded')
        total+=len(records)
    return dict(status='MEASURED_SCOPE_CHECKS_PASS',runs=2,native_observations=total,a2_08='REFERENCE_PARTIAL',vampiro_acceptance='NOT_VERIFIED',effect_boundary='SAMPLED_TRANSITION_ONLY')
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path);p.add_argument('--check-source-hashes',action='store_true');args=p.parse_args();data=json.loads(args.evidence.read_text());result=check(data)
    if args.check_source_hashes:
        root=Path(__file__).resolve().parents[2]
        for name,expected in data['measured_source_hashes'].items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,'Measured source changed: '+name)
    print(json.dumps(result))
if __name__=='__main__':main()
