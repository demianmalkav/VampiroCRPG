#!/usr/bin/env python3
"""Check scoped container observations; do not rerun CE or accept Vampiro."""
import argparse
import hashlib
import json
from pathlib import Path
from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA, neighbors, require
from check_ce_door_evidence import identity

TARGETS={'locked':(491,132,14499,0),'empty-open':(968,132,14497,0),'cancel-approach':(968,132,14497,0)}

def anim(obj):return (obj['fid']>>16)&255

def private_content_absent(value):
    if isinstance(value,dict):
        require(not {'monitor_recent_hex','visible_tile_objects'} & value.keys(),'Private content published')
        for child in value.values():private_content_absent(child)
    elif isinstance(value,list):
        for child in value:private_content_absent(child)

def check(data):
    require(data['a2_06']==data['a2_03']=='REFERENCE_PARTIAL' and data['a2_08']=='NOT_EXECUTED' and data['vampiro_status']=='NOT_VERIFIED','Scope overclaim')
    private_content_absent(data)
    require(len(data['runs'])==3 and {r['role'] for r in data['runs']}==TARGETS.keys(),'Missing contrasting scenario')
    records_total=0
    for run in data['runs']:
        role=run['role'];target=TARGETS[role];case=run['cases'][0];records=run['native_pose_changes']
        require(run['ce_revision']==CE_REVISION and run['binary_sha256']==ELF_SHA,'Reference identity mismatch')
        require(run['input_hashes']==INPUTS and run['original_inputs_unchanged']=={n:True for n in INPUTS},'DAT preservation mismatch')
        require(run['adapter_source_sha256']==data['measured_source_hashes']['tools/research/ce_container_input.cc'] and run['controller_sha256']==data['measured_source_hashes']['tools/research/probe_ce_container_interaction.py'],'Probe identity mismatch')
        require(tuple(run['locker_identity'])==target and len(run['cases'])==1 and records,'Missing scoped observations')
        before,effect,after=(case[k] for k in ('before','effect','after'))
        require(identity(before['selected_object'])==identity(before['locker'])==target and before['mouse_mode']==1,'Wrong selected object or mode')
        require('LOCKER_LOOK' in before['monitor_line_kinds'] and len(before['monitor_line_sha256'])==2,'Visor observation missing')
        require(before['locker']['frame']==0 and not before['inventory_visible'],'Missing closed baseline')
        require(before['sequence']<case['release']['sequence']<effect['sequence']<after['sequence'],'Input chronology regressed')
        require(all(identity(r['locker'])==target for r in records),'Target identity changed')
        require(all(r['blocker_at_actor'] is None for r in records),'Occupied actor tile')
        require(all(a['sdl_tick_ms']<=b['sdl_tick_ms'] and a['input_sequence']<=b['input_sequence'] for a,b in zip(records,records[1:])),'Native chronology regressed')
        require(all(a['dude']['tile']==b['dude']['tile'] or b['dude']['tile'] in neighbors(a['dude']['tile']) for a,b in zip(records,records[1:])),'Route skipped hex')
        require(case['transfer'] is None and case['repeated_transfer'] is None,'Unmeasured transfer claimed')
        require(before['locker_inventory']==effect['locker_inventory']==after['locker_inventory'] and before['actor_inventory']==effect['actor_inventory']==after['actor_inventory']==[],'Ownership changed without measured transfer')
        gestures=[r for r in records if anim(r['dude'])==11]
        if role=='cancel-approach':
            interrupt=case['interrupt'];trigger=interrupt['trigger']
            require(anim(trigger['dude']) in (1,19) and (trigger['dude']['x'] or trigger['dude']['y']) and trigger['locker_distance']>1,'No approach in progress')
            require(case['release']['sequence']<trigger['sequence']<interrupt['verified']['sequence']<interrupt['release']['sequence']<effect['sequence'],'Interrupt not before effect')
            require(interrupt['verified']['mouse_mode']==0 and interrupt['verified']['cursor_tile_before']==interrupt['target']['roundtrip_tile']==interrupt['target']['requested_tile']==15709,'Redirection target unverified')
            states=[before,trigger,interrupt['release'],effect,after]+records
            require(all(not s['inventory_visible'] and s['locker']['frame']==0 and 'LOCKER_SEARCH' not in s['monitor_line_kinds'] for s in states),'Cancelled action still opened')
            require(not gestures and after['dude']['tile']==15709 and anim(after['dude'])==0,'Cancelled action not settled')
        else:
            require(before['locker_distance']==1 and gestures and all(r['locker_distance']==1 and r['dude']['rotation']==0 for r in gestures),'Interaction gesture/contact not observed')
            require(set(range(12))<={r['dude']['frame'] for r in gestures},'Incomplete measured gesture')
            if role=='locked':
                require(before['locker_data_flags'] & 0x02000000 and len(before['locker_inventory'])==4,'Locked fixture mismatch')
                require(all(not r['inventory_visible'] and r['locker']['frame']==0 for r in records) and not effect['inventory_visible'] and effect['locker']['frame']==0 and 'LOCKED' in effect['monitor_line_kinds'],'Locked container incorrectly opened')
                require(effect['monitor_start']>before['monitor_start'],'Missing refusal update')
            else:
                require(not before['locker_data_flags'] & 0x02000000 and before['locker_inventory']==[],'Empty fixture mismatch')
                opened=[r for r in records if r['inventory_visible']]
                require(opened and effect['inventory_visible'] and effect['locker_distance']==1 and identity(effect['inventory_target'])==target and 'LOCKER_SEARCH' in effect['monitor_line_kinds'],'Inventory opening not measured')
                require(all(identity(r['inventory_target'])==target and r['locker_distance']==1 for r in opened),'Wrong inventory target or distance')
                require(gestures[-1]['sdl_tick_ms']<=opened[0]['sdl_tick_ms'] and opened[0]['locker']['frame']==effect['locker']['frame']==1,'Gesture/open chronology differs')
                require(not after['inventory_visible'] and any(r.get('event')=='key' and r.get('key')=='Escape' for r in run['trace']),'Inventory exit not measured')
        records_total+=len(records)
    return {'status':'MEASURED_SCOPE_CHECKS_PASS','scenarios':3,'interaction_native_observations':records_total,'A2-06':'REFERENCE_PARTIAL','A2-08':'NOT_EXECUTED','vampiro_acceptance':'NOT_VERIFIED'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path);p.add_argument('--check-source-hashes',action='store_true');args=p.parse_args()
    data=json.loads(args.evidence.read_text());result=check(data)
    if args.check_source_hashes:
        root=Path(__file__).resolve().parents[2]
        for name,expected in data['measured_source_hashes'].items():require(hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,'Measured source changed: '+name)
    print(json.dumps(result))

if __name__=='__main__':main()
