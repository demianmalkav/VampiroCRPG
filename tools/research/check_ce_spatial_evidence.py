#!/usr/bin/env python3
"""Verify archived spatial observations and limits; this does not execute CE."""
import argparse
import hashlib
import json
from pathlib import Path
from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA, neighbors, require
from check_ce_container_evidence import private_content_absent
from check_ce_door_evidence import identity

ROLES={'selection-exterior','depth-streetlight','selection-balanced','closed-open-access','depth-wall','wall-ground-input-hidden-roof-repeat','wall-sampling-diagnostic'}
LOCKER=(968,132,14497,0)

def case(run,label):
    found=[c for c in run['cases'] if c['label'].endswith(label)]
    require(len(found)==1,'Missing or ambiguous case '+label);return found[0]

def check(data):
    require(data['schema']=='ce-spatial-evidence-1','Unknown schema')
    require(data['reference_status']=='REFERENCE_PARTIAL' and data['vampiro_status']=='NOT_VERIFIED','Scope overclaim')
    require(data['a2_status']=={n:'REFERENCE_PARTIAL' for n in ('A2-06','A2-07','A2-10')},'Acceptance overclaim')
    require(data['reference_deviations']==['HIDDEN_ROOF_LOCKER_DISCLOSED','CONTACT_DISTANCE_GATE_NOT_GENERAL_BARRIER_PROOF'],'Deviation erased')
    private_content_absent(data)
    require(len(data['runs'])==7 and {r['plan']['role'] for r in data['runs']}==ROLES,'Scenario coverage missing')
    poses=0;trials=0;opaque=0;roof_blocked=0;cutaways=0;bridged=0
    for r in data['runs']:
        require(r['completed'] and r['failure'] is None,'Failed experiment promoted')
        require(r['ce_revision']==CE_REVISION and r['binary_sha256']==ELF_SHA,'Wrong executable reference')
        require(r['input_hashes']==INPUTS and r['original_inputs_unchanged']=={n:True for n in INPUTS},'Original input mismatch')
        for k in ('adapter','controller','plan'):
            require(r[k+'_source_sha256' if k=='adapter' else k+'_sha256']==data['measured_source_hashes'][r[k+'_file']],'Measured source binding mismatch')
        records=r['native_pose_changes'];require(bool(records),'No native pose evidence')
        require(all(s['blocker_at_actor'] is None for s in records),'Actor entered blocked tile')
        require(all(a['sdl_tick_ms']<=b['sdl_tick_ms'] and a['input_sequence']<=b['input_sequence'] for a,b in zip(records,records[1:])),'Native chronology regressed')
        for a,b in zip(records,records[1:]):
            if a['dude']['tile']==b['dude']['tile'] or b['dude']['tile'] in neighbors(a['dude']['tile']):continue
            matches=[g for g in data['transition_log_gaps'] if g['run']==r['private_run'] and g['from_sequence']==a['input_sequence'] and g['to_sequence']==b['input_sequence'] and g['from_tick']==a['sdl_tick_ms'] and g['to_tick']==b['sdl_tick_ms'] and g['from_tile']==a['dude']['tile'] and g['to_tile']==b['dude']['tile']]
            require(len(matches)==1,'Unexplained native route gap');g=matches[0]
            receipts={s['sequence']:s for c in r['cases'] for s in c.get('samples',[])}
            require(g['scope']=='POSE_LOG_OMISSION_BRIDGED_BY_INPUT_RECEIPTS' and g['cause']=='UNVERIFIED','Gap scope overclaim')
            require(all(q in receipts for q in g['bridge_input_sequences']),'Gap bridge observation missing')
            tiles=[receipts[q]['dude']['tile'] for q in g['bridge_input_sequences']]
            require(tiles==g['actor_tiles'] and tiles[0]==a['dude']['tile'] and tiles[-1]==b['dude']['tile'] and all(y==x or y in neighbors(x) for x,y in zip(tiles,tiles[1:])),'Gap bridge is not a contiguous observed route')
            require(a['input_sequence']<g['bridge_input_sequences'][0]<=g['bridge_input_sequences'][-1]<b['input_sequence'],'Bridge outside gap')
            bridged+=1
        for s in records:
            for q in s['actor_points']:
                if any(h['hit_flags']&4 for h in q['hits']):cutaways+=1
        poses+=len(records)
        for c in r['cases']:
            require(c['before']['sequence']<c['after']['sequence'],'Case chronology regressed')
            if c['action']['op']=='move':
                require(c['projection']['requested_tile']==c['projection']['roundtrip_tile']==c['verified']['cursor_tile_before']==c['action']['tile'],'Movement cursor unverified')
                require(c['settled'] and len(c['samples'])>=10 and c['frame_times_ms'] and c['label']+'.gif' in r['captures'],'Movement visual/settling evidence missing')
            for t in c.get('point_trials',[]):
                trials+=1;a=t['after'];q=a['cursor_point'];require(a['cursor_before']==t['verified']['cursor_before']==t['candidate']['xy'],'Pixel UI input mismatch')
                if q['roof'] and not q['egg_flags']:
                    require(a['selected_object'] is None,'Roof suppression contradicted');roof_blocked+=1
                elif len(q['hits'])>=2 and all(h['hit_flags']==1 for h in q['hits']):
                    require(identity(a['selected_object'])==identity(q['hits'][-1]['object']),'Opaque front selection contradicted');opaque+=1
    by={r['plan']['role']:r for r in data['runs']}
    require(bridged==len(data['transition_log_gaps'])==1,'Gap metadata does not match observations')
    diagnostic=by['wall-sampling-diagnostic']
    require(case(diagnostic,'repeat-first-wall-request')['after']['dude']['tile']==14110 and case(diagnostic,'return-origin')['after']['dude']['tile']==13915,'Discriminating repetition missing')
    depth=by['depth-streetlight'];moves=[c for c in depth['cases'] if c['action']['op']=='move']
    require([c['action']['tile'] for c in moves]==neighbors(13912)+neighbors(13912)[::-1]+[13915],'Perimeter inputs missing')
    require(all(c['after']['dude']['tile']==c['action']['tile'] for c in moves),'Streetlight perimeter not reached')
    overlap=[q for s in depth['native_pose_changes'] for q in s['actor_points'] if any(h['object']['pid']==33554724 for h in q['hits']) and any(h['object']['pid']==16777216 for h in q['hits'])]
    require(overlap and any(q['hits'][-1]['object']['pid']==33554724 for q in overlap),'Post/avatar foreground overlap missing')
    contact=by['closed-open-access'];closed=case(contact,'closed-access-use');blocked=case(contact,'closed-access-move');opened=case(contact,'open-access-use')
    require(identity(closed['selected_before']['selected_object'])==LOCKER,'Closed-access target not selected')
    require(closed['selected_before']['locker_distance']>1 and closed['after']['dude']['tile']==15711,'Closed access did not retain distant actor')
    require(all(not s['inventory_visible'] and s['locker']['frame']==0 and not s['door']['flags']&16 for s in closed['samples']+blocked['samples']),'Effect or passage before access')
    require(blocked['after']['dude']['tile']==15711,'Closed barrier movement did not stop')
    require(opened['after']['inventory_visible'] and opened['after']['locker_distance']==1 and identity(opened['after']['inventory_target'])==LOCKER,'Open-access contact/panel missing')
    require('LOCKER_SEARCH' in opened['after']['monitor_line_kinds'],'Search visor observation missing')
    require(closed['before']['actor_inventory']==closed['after']['actor_inventory']==opened['after']['actor_inventory']==[],'Unmeasured actor ownership change')
    require(not case(contact,'09-key')['after']['inventory_visible'],'Inventory exit missing')
    click=by['wall-ground-input-hidden-roof-repeat'];hover=case(click,'opaque-wall-hover');exam=case(click,'arrow-wall-examine')
    require(identity(hover['observed']['selected_object'])==identity(hover['observed']['hover_look_target']),'Visor target binding missing')
    require(exam['after']['dude']['tile']==exam['selected_before']['dude']['tile']==13915 and 'WALL_LOOK' in exam['selected_before']['monitor_line_kinds'],'Arrow-wall inspection unexpectedly moved')
    wall=case(click,'move-wall-cell');free=case(click,'move-free-ground')
    require(wall['projection']['blocker'] is not None and wall['after']['dude']['tile']!=14310 and free['after']['dude']['tile']==13915,'Wall/free-ground distinction missing')
    hidden=case(click,'hidden-locker-hover');refusal=case(click,'hidden-locker-use-refused')
    require(identity(hidden['observed']['selected_object'])==identity(hidden['observed']['hover_look_target'])==LOCKER and 'LOCKER_LOOK' in hidden['observed']['monitor_line_kinds'],'Hidden disclosure repetition missing')
    require(not hidden['observed']['cursor_point']['roof'] and not hidden['observed']['cursor_point']['egg_flags'],'Roof query mismatch erased')
    require(refusal['after']['dude']['tile']==15711 and not refusal['after']['inventory_visible'] and refusal['after']['locker']['frame']==0,'Hidden inaccessible use caused effect')
    require(opaque>=30 and roof_blocked>=40 and cutaways>0,'Spatial coverage too narrow')
    require(data['counts']==dict(starts=7,native_pose_observations=poses,point_trials=trials,opaque_front_trials=opaque,roof_blocked_trials=roof_blocked,actor_cutaway_points=cutaways),'Coverage counts mismatch')
    require(data['visual_review']['hidden_roof_locker_repeated'] and len(data['visual_review']['reviewed_captures'])>=6,'Visual evidence review missing')
    return dict(status='MEASURED_SCOPE_CHECKS_PASS',**data['counts'],vampiro_acceptance='NOT_VERIFIED')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path);p.add_argument('--check-source-hashes',action='store_true');a=p.parse_args()
    d=json.loads(a.evidence.read_text());result=check(d)
    if a.check_source_hashes:
        root=Path(__file__).resolve().parents[2]
        for n,h in d['measured_source_hashes'].items():require(hashlib.sha256((root/n).read_bytes()).hexdigest()==h,'Measured source changed: '+n)
    print(json.dumps(result))

if __name__=='__main__':main()
