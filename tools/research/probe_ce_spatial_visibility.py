#!/usr/bin/env python3
"""Private original-map spatial probes. Normal SDL inputs, native read queries.

Plans describe bounded UI actions; no teleport, flag, object, MAP or engine edits.
Raw screenshots, visor text and censuses remain private. This is CE reference,
not Windows equivalence or acceptance of a Vampiro feature.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from PIL import ImageGrab
from run_fallout_ce_lab import CE_REVISION, CONFIGS, INPUTS, sha, symbols, read_state
from probe_ce_container_interaction import NAMES as CONTAINER_NAMES, BASELINE_BINARY

NAMES = dict(CONTAINER_NAMES, HITS='fallout::_obj_create_intersect_list(int, int, int, int, fallout::ObjectWithFlags**)',
    FREE_HITS='fallout::_obj_delete_intersect_list(fallout::ObjectWithFlags**)',
    INTERSECT='fallout::_obj_intersects_with(fallout::Object*, int, int)',
    EGG='fallout::gEgg', ROOF='fallout::_square_roof_intersect(int, int, int)')

def identity(obj):
    return [obj[k] for k in ('id','pid','tile','elevation')] if obj else None

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('binary','ce-source','inputs','output','lab-deps','plan'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    binary,source,inputs,out,deps,plan_path=[getattr(args,k).resolve() for k in ('binary','ce_source','inputs','output','lab_deps','plan')]
    plan=json.loads(plan_path.read_text())
    assert plan['map']=='NCR1.MAP' and 0<len(plan['actions'])<=80
    assert sha(binary)==BASELINE_BINARY
    assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==CE_REVISION
    assert not subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
    for n,h in INPUTS.items():assert sha(inputs/n)==h,n
    out.mkdir(parents=True,exist_ok=False);work=out/'work';work.mkdir();(work/'data').mkdir()
    for n in INPUTS:(work/n).symlink_to(inputs/n)
    (work/'fallout2-ce').symlink_to(binary)
    for n,s in CONFIGS.items():(work/n).write_text(s)
    nm=subprocess.check_output(['nm','-C',str(binary)],text=True)
    addresses={l.split(maxsplit=2)[2]:int(l.split()[0],16) for l in nm.splitlines() if len(l.split(maxsplit=2))==3 and l.split(maxsplit=2)[2] in NAMES.values()}
    offsets={k:addresses[v] for k,v in NAMES.items()}
    (out/'ce_probe_offsets.h').write_text('\n'.join(f'constexpr uintptr_t OFF_{k}=0x{v:x};' for k,v in offsets.items())+'\n')
    adapter_source=Path(__file__).with_name('ce_spatial_visibility_input.cc').resolve();adapter=out/'ce_spatial_visibility_input.so'
    subprocess.run(['g++','-shared','-fPIC','-std=c++17','-O2','-I'+str(deps/'usr/include/SDL2'),'-I'+str(deps/'usr/include/x86_64-linux-gnu'),'-I'+str(source/'src'),'-I'+str(out),str(adapter_source),'-o',str(adapter),'-ldl'],check=True)
    env=os.environ.copy();env['PATH']=str(deps/'usr/bin')+os.pathsep+env['PATH'];env['LD_LIBRARY_PATH']=str(deps/'usr/lib/x86_64-linux-gnu')
    env.update(DISPLAY='127.0.0.1:27875',SDL_AUDIODRIVER='dummy',DEBUGACTIVE='log',LD_PRELOAD=str(adapter),
        CE_CONTAINER_TILE='14497',CE_CONTAINER_ID='968',CE_CONTAINER_PID='132',
        CE_PROBE_COMMAND=str(out/'command'),CE_PROBE_RECEIPT=str(out/'receipt.json'),CE_PROBE_MOTION=str(out/'motion.jsonl'))
    seq=0;trace=[];cases=[];start=time.monotonic();game=None;x=None;failure=None
    def note(event,**data):trace.append(dict(t_ms=round((time.monotonic()-start)*1000),event=event,**data))
    def command(tile=-1,buttons=0,xy=(0,0)):
        nonlocal seq
        seq+=1;t=out/'command.tmp';t.write_text(f'{seq} {tile} {buttons} {xy[0]} {xy[1]}\n');t.replace(out/'command')
        for _ in range(1500 if tile==-8 else 150):
            try:
                r=json.loads((out/'receipt.json').read_text())
                if r['sequence']==seq:note('native_input_receipt',**r);return r
            except (OSError,json.JSONDecodeError):pass
            if game.poll() is not None:raise RuntimeError('CE exited')
            time.sleep(.02)
        raise RuntimeError('Native receipt timeout')
    def key(k):subprocess.run(['xdotool','key',k],env=env,check=True);note('key',key=k)
    def capture(label):
        f=label+'.png';ImageGrab.grab(xdisplay=env['DISPLAY']).save(out/f);note('capture',file=f)
    def mode(wanted):
        if command()['mouse_mode']!=wanted:
            command(buttons=4);time.sleep(.12);command();time.sleep(.2)
        assert command()['mouse_mode']==wanted
    def point(xy):
        receipt=command(-3,xy=xy);time.sleep(.08);state=command()
        assert state['cursor_before']==list(xy),'UI cursor did not reach requested pixel'
        return receipt,state
    def settle(label,seconds=12):
        frames=[];times=[];samples=[];begin=time.monotonic();prior=None;stable=0;last=-1
        while time.monotonic()-begin<seconds:
            s=command();samples.append(s);a=s['dude'];pose=tuple(a[k] for k in ('tile','fid','frame','x','y'))
            stable=stable+1 if pose==prior else 0;prior=pose
            dt=round((time.monotonic()-begin)*1000)
            if dt-last>=140:frames.append(ImageGrab.grab(xdisplay=env['DISPLAY']));times.append(dt);last=dt
            if time.monotonic()-begin>.8 and stable>=10 and ((a['fid']>>16)&255)==0:break
            time.sleep(.05)
        if frames:frames[0].save(out/(label+'.gif'),save_all=True,append_images=frames[1:],duration=[max(20,b-a) for a,b in zip(times,times[1:])]+[700],loop=0)
        capture(label);return dict(samples=samples,after=command(),settled=stable>=10,frame_times_ms=times)
    def target_point(field,wanted):
        s=command();rect=s[field+'_rect'];attempts=[]
        for fy in (.5,.25,.75,.1,.9):
            for fx in (.5,.25,.75,.1,.9):
                xy=(round(rect[0]+(rect[2]-rect[0])*fx),round(rect[1]+(rect[3]-rect[1])*fy))
                if not (0<=xy[0]<800 and 0<=xy[1]<500):continue
                _,r=point(xy);attempts.append(r)
                if identity(r.get('selected_object'))==wanted:return xy,r,attempts
        return None,command(),attempts
    with (out/'xvfb.log').open('w') as xl,(out/'runtime.log').open('w') as rl:
        try:
            x=subprocess.Popen(['Xvfb',':27875','-screen','0','800x600x24','-nolisten','unix','-nolisten','local','-listen','tcp','-ac'],env=env,stdout=xl,stderr=xl)
            for _ in range(80):
                try:
                    with socket.create_connection(('127.0.0.1',33875),timeout=.1):break
                except OSError:
                    if x.poll() is not None:raise RuntimeError('Xvfb exited')
                    time.sleep(.1)
            game=subprocess.Popen(['./fallout2-ce'],cwd=work,env=env,stdout=rl,stderr=rl)
            time.sleep(5);key('n');time.sleep(2);key('t');time.sleep(2);key('Escape');time.sleep(5)
            sym=symbols(binary);deadline=time.monotonic()+40
            while time.monotonic()<deadline:
                s=read_state(game.pid,binary,sym)
                if s['map_name']=='NCR1.MAP' and s['actor']['tile']==13915:break
                if game.poll() is not None:raise RuntimeError('CE exited during startup')
                time.sleep(.25)
            else:raise RuntimeError('Original map not ready')
            time.sleep(1);capture('initial');(out/'initial-census.json').write_text(json.dumps(command(-2)))
            for index,action in enumerate(plan['actions']):
                label=f'{index:02d}-'+action.get('label',action['op']);before=command();case=dict(label=label,action=action,before=before)
                op=action['op']
                if op=='mode':mode(action['value'])
                elif op=='key':key(action['key']);time.sleep(.5)
                elif op=='move':
                    mode(0);r=command(action['tile']);time.sleep(.08);v=command();assert r['roundtrip_tile']==v['cursor_tile_before']==action['tile']
                    command(buttons=1);time.sleep(.12);release=command();case.update(projection=r,verified=v,release=release,**settle(label))
                elif op=='point':
                    mode(1);r,v=point(action['xy']);time.sleep(.8);case.update(projection=r,verified=v,observed=command());capture(label)
                elif op=='scan':
                    mode(1);scan=command(-8);case['scan']=scan;points=scan['scan_points']
                    # Prefer special roof/egg cases, then front/behind pairs. Query candidates are not UI acceptance.
                    points=sorted(points,key=lambda q:(not any(h['hit_flags']&4 for h in q['hits']),not q['roof']))
                    case['point_trials']=[]
                    for i,q in enumerate(points[:action.get('limit',24)]):
                        r,v=point(q['xy']);time.sleep(.7);after=command();capture(label+f'-point-{i:02d}')
                        case['point_trials'].append(dict(candidate=q,projection=r,verified=v,after=after))
                elif op=='use-target':
                    mode(1);xy,v,attempts=target_point(action['field'],action['identity']);case.update(selected_pixel=xy,selection_attempts=attempts)
                    if xy is not None:
                        time.sleep(.7);case['selected_before']=command();capture(label+'-selected');command(buttons=1);time.sleep(.12);case['release']=command();case.update(**settle(label,action.get('seconds',12)))
                    else:case['blocked']='NO_NORMAL_UI_PIXEL_SELECTS_TARGET';capture(label+'-unselectable')
                elif op=='wait':time.sleep(action.get('seconds',.5));capture(label)
                else:raise ValueError('Unknown plan operation '+op)
                case.setdefault('after',command());cases.append(case)
                print(label,'actor',case['after']['dude']['tile'],'selected',identity(case['after'].get('selected_object')),'inventory',case['after']['inventory_visible'],flush=True)
            (out/'final-census.json').write_text(json.dumps(command(-2)))
        except BaseException as exc:failure=repr(exc);raise
        finally:
            if game and game.poll() is None:game.terminate();game.wait(timeout=5)
            if x and x.poll() is None:x.terminate();x.wait(timeout=5)
            unchanged={n:sha(inputs/n)==h for n,h in INPUTS.items()}
            result=dict(kind='CE_NATIVE_SPATIAL_EXPERIMENT',completed=failure is None,failure=failure,plan=plan,plan_sha256=sha(plan_path),
                binary_sha256=sha(binary),ce_revision=CE_REVISION,input_hashes=INPUTS,original_inputs_unchanged=unchanged,
                adapter_source_sha256=sha(adapter_source),adapter_binary_sha256=sha(adapter),controller_sha256=sha(Path(__file__)),
                controller_dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in ('probe_ce_container_interaction.py','run_fallout_ce_lab.py')},
                native_symbol_offsets=offsets,cases=cases,trace=trace,
                native_pose_changes=[json.loads(l) for l in (out/'motion.jsonl').read_text().splitlines()] if (out/'motion.jsonl').exists() else [],
                captures={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.png','.gif')},
                intervention='Normal mouse/keyboard input and native read queries only; hit lists allocate/free query cache, no authoritative gameplay writes.',
                limitations=['CE Linux silent DAT-only, not original Windows or Vampiro acceptance','Native samples are not atomic contact instrumentation','NPCs may move under original default seed','Private frames are visual evidence, not pixel-perfect renderer equivalence'])
            (out/'evidence.json').write_text(json.dumps(result,separators=(',',':'))+'\n');assert all(unchanged.values())

if __name__=='__main__':main()
