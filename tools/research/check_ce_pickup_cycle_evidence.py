#!/usr/bin/env python3
"""Check archived CE pickup-cycle claims, not execute or accept the game."""
import argparse,hashlib,json
from pathlib import Path
from ce_reference_identity import CE_REVISION, INPUTS
from check_ce_navigation_evidence import ELF_SHA,require
from check_ce_container_evidence import private_content_absent

def anim(s):return (s['dude']['fid']>>16)&255
def ground(s):return s['watched_item'] is not None and s['watched_item']['pid']==4 and s['watched_item']['tile']==12477 and s['watched_on_map'] and s['watched_owner'] is None and not s['actor_inventory']
def owned(s):
 slots=[x for x in s['actor_inventory'] if x['object']['pid']==4]
 owner=s['watched_owner'];actor=s['dude']
 return s['watched_item'] is not None and s['watched_item']['pid']==4 and s['watched_item']['tile']==-1 and not s['watched_on_map'] and owner is not None and (owner['id'],owner['pid'])==(actor['id'],actor['pid']) and len(slots)==1 and slots[0]['quantity']==1 and slots[0]['owner'] is not None and (slots[0]['owner']['id'],slots[0]['owner']['pid'])==(actor['id'],actor['pid'])
def cases(run):return {x['label']:x for x in run['cases']}
def check(data):
 private_content_absent(data)
 require(data['a2_08']=='REFERENCE_PARTIAL' and data['a2_09']=='REFERENCE_PARTIAL' and data['vampiro_status']=='NOT_VERIFIED' and data['effect_boundary_status']=='SAMPLED_QUEUE_AND_STATE','Scope overclaim')
 require(data['reference']['map_sha256']=='c293b1652f71f518f5e92915a1676ecb5ad75cf33f93a0d9db30de6fb53236db','Wrong map')
 runs={r['run_id']:r for r in data['runs']}
 require(set(runs)=={'cycle-03','cycle-04','cycle-05','cycle-06','cycle-07','cycle-08','cycle-09','cycle-10'},'Incomplete package')
 for r in runs.values():
  require(r['ce_revision']==CE_REVISION and r['binary_sha256']==ELF_SHA and r['input_hashes']==INPUTS and r['original_inputs_unchanged']=={n:True for n in INPUTS},'Reference drift')
  require(r['layout']['sequence_size']==4416 and r['layout']['description_size']==80 and r['layout']['delay']==36 and r['layout']['callback']==40,'Native layout drift')
  require(r['controller_sha256']==data['measured_source_hashes'][r['controller_path']] and r['adapter_source_sha256']==data['measured_source_hashes']['tools/research/ce_pickup_cycle_input.cc'] and r['layout_source_sha256']==data['measured_source_hashes']['tools/research/ce_animation_layout.cc'],'Probe drift')
  require('StartingMap=DENBUS1.MAP' in r['configs']['ddraw.ini'] and all(hashlib.sha256(v.encode()).hexdigest()==r['configs_sha256'][k] for k,v in r['configs'].items()),'Config drift')
  c=cases(r);require(ground(c['original-ground-item-fixture']['initial']) and c['original-ground-item-fixture']['initial']['dude']['tile']==13292,'Initial fixture mismatch')
  require(owned(c['pickup-complete']['after']) and owned(c['former-pixel-repeat']['after']),'Ownership not unique')
  records=r['native_pose_changes'];require(records and all(a['sdl_tick_ms']<=b['sdl_tick_ms'] and a['input_sequence']<=b['input_sequence'] for a,b in zip(records,records[1:])),'Chronology regression')
 # Observed queue explains the marker/ownership discrepancy in the silent lab.
 rec=runs['cycle-03']['native_pose_changes'];g=[s for s in rec if anim(s)==10]
 require(set(range(9))<={s['dude']['frame'] for s in g},'Incomplete gesture')
 for s in g:
  f=s['dude']['frame'];require(ground(s) if f<=6 else owned(s),'Unexpected sampled effect boundary')
  require(len(s['actor_sequences'])==1,'Actor queue ambiguous')
  q=s['actor_sequences'][0];ad=q['descriptions'];require(q['length']==7 and ad[4]['kind']==4 and ad[4]['anim']==10 and ad[5]['kind']==28 and ad[6]['kind']==11 and ad[6]['callback']=='pickup' and ad[6]['actor_param1'] and ad[6]['target_param2'],'Wrong gesture/CONTINUE/pickup chain')
 require(any(s['actor_sequences'][0]['descriptions'][5]['delay']==4 and s['actor_sequences'][0]['descriptions'][6]['delay']==4 for s in rec if s['actor_sequences'] and len(s['actor_sequences'][0]['descriptions'])==7),'Two initial delays not observed')
 require({0,1,2}<={s['actor_sequences'][0]['descriptions'][5]['delay'] for s in g if s['actor_sequences'][0]['cursor']==5},'CONTINUE countdown missing')
 require({0,1,2,3}<={s['actor_sequences'][0]['descriptions'][6]['delay'] for s in g if s['actor_sequences'][0]['cursor']==6},'Pickup countdown missing')
 early=cases(runs['cycle-07'])['cancel-gesture']
 for k in ('trigger','press','release'):
  s=early[k];require(anim(s)==10 and s['dude']['frame']<=2 and ground(s),'Early cancel window missed')
 require(early['press']['buttons']==1 and early['release']['buttons']==0 and early['press']['cursor_tile_before']==early['release']['cursor_tile_before']==12479 and early['press']['sequence']<early['release']['sequence'],'Cancel input unverified')
 require(early['after']['dude']['tile']==12479 and ground(early['after']) and anim(early['after'])==0,'Early cancel transferred or failed to move')
 late=cases(runs['cycle-04'])['cancel-gesture'];require(ground(late['verified']) and owned(late['release']) and owned(late['after']),'Late trial distinction lost')
 post=cases(runs['cycle-05'])['cancel-after-effect-request'];require(anim(post['trigger'])==10 and owned(post['trigger']) and owned(post['release']),'Post-effect trigger not owned')
 repeat=cases(runs['cycle-06'])['repeat-gesture'];require(repeat['verified']['mouse_mode']==1 and repeat['verified']['selected_object'] is not None and repeat['verified']['selected_object']['id']==200 and repeat['verified']['selected_object']['pid']==4,'Repeat target not selected');require(anim(repeat['trigger'])==10 and ground(repeat['trigger']) and ground(repeat['release']) and owned(repeat['after']),'Gesture repeat changed uniqueness')
 for n,label,want in [('cycle-08','before-effect',False),('cycle-09','after-effect',True),('cycle-10','during-gesture',False)]:
  c=cases(runs[n]);saved=c[label+'-saved'];loaded=c[label+'-loaded']['state'];altered=c[label+'-before-load']['state']
  require(saved['files'] and any(p.lower().endswith('/save.dat') for p in saved['files']),'No native save artifact')
  require((owned(saved['after']) and owned(loaded)) if want else (ground(saved['after']) and ground(loaded)),'Saved/loaded ownership mismatch')
  require(loaded['requested_tile']==-7 and loaded['dude']['tile']==saved['after']['dude']['tile'],'Rebound/save tile mismatch')
  require(owned(altered) if not want else altered['dude']['tile']!=saved['after']['dude']['tile'],'Load did not undo a distinct intervening state')
  receipt=runs[n]['input_receipts'];require(any(x['requested_tile']==-6 for x in receipt) and any(x['requested_tile']==-7 for x in receipt),'Watch not cleared/rebound around load')
  require(any(x['key']=='F6' for x in runs[n]['key_events']) and any(x['key']=='F7' for x in runs[n]['key_events']),'Save/load bypassed native keys')
 during=cases(runs['cycle-10']);trigger=during['save-during-gesture-request']['trigger'];loaded=during['during-gesture-loaded']['state'];require(anim(trigger)==10 and trigger['dude']['frame']<=2 and ground(trigger) and trigger['actor_sequences'] and anim(loaded)==0 and not loaded['actor_sequences'],'Pending gesture incorrectly reported preserved')
 return dict(status='MEASURED_SCOPE_CHECKS_PASS',runs=len(runs),native_observations=sum(len(x['native_pose_changes']) for x in runs.values()),reference_only=True)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('evidence',type=Path);p.add_argument('--check-source-hashes',action='store_true');a=p.parse_args();d=json.loads(a.evidence.read_text());r=check(d)
 if a.check_source_hashes:
  root=Path(__file__).resolve().parents[2]
  for path,h in d['measured_source_hashes'].items():require(hashlib.sha256((root/path).read_bytes()).hexdigest()==h,'Measured source changed: '+path)
 print(json.dumps(r))
if __name__=='__main__':main()
