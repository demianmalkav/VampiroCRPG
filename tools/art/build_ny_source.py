"""Author editable NY sources once. export_ny.py re-renders edits without rebuilding.

Authoring only: Blender/bpy 4.5 + Pillow. Runtime remains Python stdlib + PNG.
MakeHuman base mesh: CC0; provenance in assets/walk/source/MAKEHUMAN_LICENSE.md.
"""
import json, math, random, sys
from pathlib import Path
import bpy
from mathutils import Vector, Matrix
import build_walk as B

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets/walk/source'
PPU=62.2253967444
RIG=None
MATS={}
COLL=None
DIRECTIONS=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]]

def mat(name,color,patch=None,rough=.78,metal=0,emission=0):
    if name in MATS:return MATS[name]
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    srgb=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))
    c=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in srgb)
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;noise.inputs['Detail'].default_value=3
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.006
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    if patch is not None:
        image=n.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(SRC/'material-atlas.png'),check_existing=True)
        uv=n.new('ShaderNodeTexCoord');frac=n.new('ShaderNodeVectorMath');frac.operation='FRACTION';l.new(uv.outputs['UV'],frac.inputs[0])
        scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.492;l.new(frac.outputs[0],scale.inputs[0])
        shift=n.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(.004+(patch%2)*.5,.504 if patch<2 else .004,0)
        l.new(scale.outputs[0],shift.inputs[0]);l.new(shift.outputs[0],image.inputs['Vector'])
        tint=n.new('ShaderNodeMixRGB');tint.name='Garment tint';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(1,1,1,1)
        l.new(image.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],p.inputs['Base Color'])
    if emission:
        p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
    MATS[name]=m;return m

def materials():
    mat('skin','#b8a290',rough=.66);mat('eye','#9a9b90');mat('iris','#202222')
    mat('wool','#252c32',2);mat('denim','#283139',3);mat('leather','#23282a',rough=.42)
    mat('shirt','#2a171c');mat('hair','#141718',rough=.82);mat('metal','#343c3e',rough=.47,metal=.66)
    mat('brick','#423631',0);mat('stone','#313b3e',1,rough=.51);mat('mortar','#464843');mat('wood','#584e3e')
    mat('rust','#573c2e',rough=.93);mat('dumpster','#354638',rough=.55,metal=.45);mat('paper','#a79e80')
    mat('glass','#293b35',rough=.24,metal=.15);mat('red','#702526');mat('brass','#927a44',rough=.32,metal=.72)
    mat('fluorescent','#b9d3c7',rough=.3,emission=2.4);mat('amber','#b7793e',emission=.55)
    mat('water','#30474b',rough=.12,metal=.6)

def register(obj,material):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    COLL.objects.link(obj);obj.data.materials.append(MATS[material])
    if obj.type=='MESH':
        for p in obj.data.polygons:p.use_smooth=True
    return obj

def mesh(name,verts,faces,material,uv=None,bone=None):
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);register(obj,material)
    layer=data.uv_layers.new()
    for poly in data.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]))
        for li in poly.loop_indices:
            vi=data.loops[li].vertex_index;v=data.vertices[vi].co
            layer.data[li].uv=uv[vi] if uv else ((v.y if axis==0 else v.x)/2.5,(v.y if axis==2 else v.z)/2.5)
    if RIG is not None:bind(obj,bone)
    return obj

def box(name,p,size,material,bevel=.016):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);register(o,material)
    for poly in o.data.polygons:poly.use_smooth=False
    if bevel:
        mod=o.modifiers.new('Soft worn edges','BEVEL');mod.width=bevel;mod.segments=3;o.modifiers.new('Face normals','WEIGHTED_NORMAL')
    layer=o.data.uv_layers.active
    for poly in o.data.polygons:
        axis=max(range(3),key=lambda i:abs(poly.normal[i]))
        for li in poly.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co+o.location
            layer.data[li].uv=((v.y if axis==0 else v.x)/2.5,(v.y if axis==2 else v.z)/2.5)
    if RIG is not None:bind(o)
    return o

def ball(name,p,scale,material,bone=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=p);o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);register(o,material)
    if RIG is not None:bind(o,bone)
    return o

def rod(name,a,b,r,material,bone=None):
    d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();register(o,material)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    if RIG is not None:bind(o,bone)
    return o

def dist_segment(v,a,b):
    d=b-a;t=max(0,min(1,(v-a).dot(d)/d.length_squared));return (v-a-d*t).length

def bind(o,bone=None):
    groups={b.name:o.vertex_groups.new(name=b.name) for b in RIG.data.bones}
    for v in o.data.vertices:
        p=o.matrix_world@v.co
        if bone:groups[bone].add([v.index],1,'REPLACE');continue
        side='L' if p.x>=0 else 'R'
        if p.z>1.57:names=['head','neck']
        elif abs(p.x)>.20 and p.z>1.02:names=['arm.'+side,'forearm.'+side,'hand.'+side]
        elif p.z<.95:names=['thigh.'+side,'shin.'+side,'foot.'+side,'hips']
        else:names=['hips','spine','chest','neck']
        ranked=sorted((dist_segment(p,RIG.data.bones[n].head_local,RIG.data.bones[n].tail_local),n) for n in names)[:2]
        weights=[1/max(.015,d)**4 for d,n in ranked];total=sum(weights)
        for w,(_,n) in zip(weights,ranked):groups[n].add([v.index],w/total,'REPLACE')
    mod=o.modifiers.new('Shared character skeleton','ARMATURE');mod.object=RIG;o.parent=RIG

def parse_human():
    vs=[];uvs=[];fs=[];groups={};g=''
    for l in (SRC/'base-human.obj').read_text().splitlines():
        if l.startswith('v '):vs.append(tuple(map(float,l.split()[1:4])))
        elif l.startswith('vt '):uvs.append(tuple(map(float,l.split()[1:3])))
        elif l.startswith('g '):g=l[2:];groups.setdefault(g,[])
        elif l.startswith('f '):
            f=[tuple(int(a)-1 for a in x.split('/')[:2]) for x in l.split()[1:]];groups[g].append(f)
    body_ids={vi for f in groups['body'] for vi,ui in f};lo=min(vs[i][1] for i in body_ids);hi=max(vs[i][1] for i in body_ids);s=1.86/(hi-lo)
    vs=[Vector((x*s,z*s,(y-lo)*s)) for x,y,z in vs]
    return vs,uvs,groups

def subset(name,faces,vs,uvs,material,offset=0,bone=None):
    remap={};out=[];uv=[];ff=[]
    for f in faces:
        face=[]
        for vi,ui in f:
            key=(vi,ui)
            if key not in remap:remap[key]=len(out);p=vs[vi].copy();p.x*=1+offset;p.y*=1+offset;out.append(tuple(p));uv.append(uvs[ui])
            face.append(remap[key])
        ff.append(face)
    return mesh(name,out,ff,material,uv,bone)

def skeleton(vs,groups):
    def joint(g):
        ids={vi for f in groups['joint-'+g] for vi,ui in f};return sum((vs[i] for i in ids),Vector())/len(ids)
    joints={n:joint(n) for n in ['pelvis','spine-3','spine-1','neck','head','head-2']}
    definitions=[('hips',joints['pelvis'],joints['spine-3'],None),('spine',joints['spine-3'],joints['spine-1'],'hips'),('chest',joints['spine-1'],joints['neck'],'spine'),('neck',joints['neck'],joints['head'],'chest'),('head',joints['head'],joints['head-2'],'neck')]
    for side,prefix in [('L','l'),('R','r')]:
        for n,a,b,parent in [('thigh','upper-leg','knee','hips'),('shin','knee','ankle','thigh.'+side),('foot','ankle','foot-1','shin.'+side),('arm','shoulder','elbow','chest'),('forearm','elbow','hand','arm.'+side)]:
            definitions.append((n+'.'+side,joint(prefix+'-'+a),joint(prefix+'-'+b),parent))
        hand=joint(prefix+'-hand');definitions.append(('hand.'+side,hand,hand+Vector((.012 if side=='L' else -.012,.06,-.07)),'forearm.'+side))
    data=bpy.data.armatures.new('NY actor skeleton');o=bpy.data.objects.new('ActorRig',data);COLL.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name,a,b,parent in definitions:
        bone=data.edit_bones.new(name);bone.head=a;bone.tail=b
        if parent:bone.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False);return o

def set_bone(name,a,b):
    bone=RIG.data.bones[name];p=RIG.pose.bones[name]
    q=(bone.tail_local-bone.head_local).rotation_difference(Vector(b)-Vector(a))@bone.matrix_local.to_quaternion()
    p.matrix=Matrix.Translation(Vector(a))@q.to_matrix().to_4x4()
    # Children must use the evaluated parent transform, not the previous frame.
    bpy.context.view_layer.update()

def pose(mode,t=0,contact=False):
    swing=math.sin(t*math.tau) if mode=='walk' else 0
    dip=math.sin(t*math.pi)**2 if mode=='pickup' else 0
    def length(name):return RIG.data.bones[name].length
    dz=-.50*dip
    hip=Vector((0,.016+.06*dip,.993+dz))
    sp=hip+Vector((0,.14*dip,.127)).normalized()*length('hips')
    ch=sp+Vector((0,-.024+.39*dip,.275-.39*dip)).normalized()*length('spine')
    ne=ch+Vector((0,.016+.075*dip,.175-.23*dip)).normalized()*length('chest')
    he=ne+Vector((0,.01+.06*dip,.121-.121*dip)).normalized()*length('neck')
    top=he+Vector((0,.08*dip,.159-.10*dip)).normalized()*length('head')
    if contact:ch.x-=.022;ne.x-=.029;he.x-=.032
    for n,a,b in [('hips',hip,sp),('spine',sp,ch),('chest',ch,ne),('neck',ne,he),('head',he,top)]:set_bone(n,a,b)
    for side,sgn in [('L',1),('R',-1)]:
        sw=swing*sgn;lift=max(0,math.cos(t*math.tau+(.0 if sgn==1 else math.pi)))*.065 if mode=='walk' else 0
        h=hip+Vector((sgn*.123,-.002,-.027));a=Vector((sgn*.16,.02+sw*.19,.080+lift))
        # Two-bone leg solve preserves lengths while crouching and stepping.
        axis=a-h;distance=min(axis.length,length('thigh.'+side)+length('shin.'+side)-.0001);axis.normalize();a=h+axis*distance
        l1=length('thigh.'+side);l2=length('shin.'+side);along=(l1*l1-l2*l2+distance*distance)/(2*distance)
        bend=Vector((0,1,0));bend=(bend-axis*bend.dot(axis)).normalized()
        k=h+axis*along+bend*math.sqrt(max(0,l1*l1-along*along));f=a+Vector((0,.135,-.065))
        set_bone('thigh.'+side,h,k);set_bone('shin.'+side,k,a);set_bone('foot.'+side,a,f)
        sh=ch+Vector((sgn*.187,.024,.102-.03*dip));el=sh+Vector((sgn*.045,-sw*.065+.10*dip,-.235)).normalized()*length('arm.'+side);hand=el+Vector((sgn*.016,-sw*.065+.08*dip,-.235)).normalized()*length('forearm.'+side)
        if contact and side=='R':el.y+=.055;hand.y+=.09
        set_bone('arm.'+side,sh,el);set_bone('forearm.'+side,el,hand);set_bone('hand.'+side,hand,hand+Vector((0,.025,-.085)))
    bpy.context.view_layer.update()

def coat(contact=False):
    rings=[(.50,.25,.145),(.62,.245,.14),(.78,.234,.135),(.98,.205,.12),(1.12,.198,.128),(1.25,.228,.146),(1.40,.257,.143),(1.49,.208,.116)]
    if contact:rings=rings[3:];rings[0]=(1.0,.22,.135)
    vs=[];faces=[];steps=32
    for z,rx,ry in rings:
        for i in range(steps+1):
            angle=math.pi/2+.29+i*(math.tau-.58)/steps
            fold=.004*math.sin(angle*11+z*4);vs.append(((rx*1.06+fold)*math.cos(angle),(ry*1.22+fold)*math.sin(angle)+.018,z+.003*math.sin(angle*5)))
    for j in range(len(rings)-1):
        for i in range(steps):a=j*(steps+1)+i;faces.append((a,a+1,a+steps+2,a+steps+1))
    o=mesh('Leather jacket shell' if contact else 'Open wool overcoat',vs,faces,'leather' if contact else 'wool')
    mod=o.modifiers.new('Garment thickness','SOLIDIFY');mod.thickness=.012
    for side in [-1,1]:
        x=side*.08
        mesh('Notched lapel',[(side*.035,.162,1.39),(side*.11,.174,1.47),(side*.145,.17,1.28),(side*.055,.17,1.18)],[(0,1,2,3)],'leather' if contact else 'wool',bone='chest')
    for z in [1.03,1.14,1.25]:ball('Old coat button',(.066,.155,z),(.008,.006,.008),'metal',bone='spine')
    if not contact:
        for side in [-1,1]:mesh('Welt pocket',[(side*.14,.105,.98),(side*.23,.057,.99),(side*.23,.066,.97),(side*.14,.113,.96)],[(0,1,2,3)],'leather',bone='hips')

def actor(kind):
    global RIG,COLL
    B.clear();MATS.clear();materials();COLL=bpy.data.collections.new('Actor');bpy.context.scene.collection.children.link(COLL)
    vs,uvs,groups=parse_human();RIG=skeleton(vs,groups);contact=kind=='contact'
    skin=[];pants=[];shirt=[];sleeves=[]
    for f in groups['body']:
        p=sum((vs[vi] for vi,ui in f),Vector())/len(f)
        if p.z<.97:pants.append(f)
        elif 1.23<p.z<1.54 and abs(p.x)>.23:sleeves.append(f)
        elif p.z<1.55 and abs(p.x)<.235:shirt.append(f)
        else:skin.append(f)
    subset('Anatomical face neck and hands',skin,vs,uvs,'skin');subset('Denim trousers',pants,vs,uvs,'denim',.018)
    subset('Shirt',shirt,vs,uvs,'shirt',.022);subset('Garment sleeves',sleeves,vs,uvs,'leather' if contact else 'wool',.045)
    for g in ['helper-l-eye','helper-r-eye']:subset('Eye globe',groups[g],vs,uvs,'eye',bone='head')
    for side in [-1,1]:ball('Iris',(side*.0344,.149,1.725),(.008,.006,.009),'iris',bone='head')
    hair=[]
    for f in groups['body']:
        p=sum((vs[vi] for vi,ui in f),Vector())/len(f)
        if p.z>1.773 or (p.z>1.68 and p.y<.025):hair.append(f)
    subset('Hair cap',hair,vs,uvs,'hair',.018,bone='head')
    for i in range(12):
        a=i*math.tau/12;x=.094*math.cos(a);y=.061*math.sin(a)
        ball('Loose hair strand',(x,y-.022,1.753),(.011,.016,.068 if contact else .042),'hair',bone='head')
    coat(contact)
    # Boots replace the clothed foot surface with a strong, anatomically anchored shape.
    for side in [-1,1]:
        x=side*.245;ball('Worn boot toe',(x,.13,.052),(.074,.14,.054),'leather',bone='foot.'+('L' if side==1 else 'R'))
        box('Boot sole',(x,.104,.023),(.14,.26,.04),'metal',.012)
        for z in [.11,.14,.17]:rod('Boot lace',(x-.035,.044,z),(x+.035,.044,z),.003,'mortar',bone='shin.'+('L' if side==1 else 'R'))
    if contact:
        rod('Cigarette',(-.49,.23,1.14),(-.49,.28,1.14),.004,'paper',bone='hand.R');ball('Ember',(-.49,.28,1.14),(.004,.004,.004),'red',bone='hand.R')
    clips={'idle':{'start':1,'count':1,'duration_ms':1000,'loop':True},'walk':{'start':2,'count':8,'duration_ms':600,'loop':True},'pickup':{'start':10,'count':10,'duration_ms':950,'loop':False}}
    if contact:clips={'idle':clips['idle']}
    for key,cfg in clips.items():
        for i in range(cfg['count']):
            frame=cfg['start']+i;bpy.context.scene.frame_set(frame);pose(key,i/max(1,cfg['count']-1) if key=='pickup' else i/cfg['count'],contact)
            for p in RIG.pose.bones:
                p.rotation_mode='QUATERNION';p.keyframe_insert('location',frame=frame);p.keyframe_insert('rotation_quaternion',frame=frame);p.keyframe_insert('scale',frame=frame)
    if contact:RIG.scale=(.97,.97,.96)
    # All actor parts and clips remain in this source, editable independently of export.
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=19 if not contact else 1;scene.frame_set(1)
    B.STYLE['samples']=24;B.STYLE['light']['key']=[.71,.81,.84];B.STYLE['light']['fill']=[.35,.47,.57];B.setup_camera((-76,-135,76,26))
    scene['export_manifest']=json.dumps([{'key':kind,'collection':'Actor','root':'ActorRig','bounds':[-76,-135,76,26],'clips':clips,'directions':DIRECTIONS if not contact else [[0,1]]}])
    save(SRC/f'ny-{kind}.blend');RIG=None

def save(path):
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(path));print('SOURCE_SAVED',path.name,flush=True)

def environment():
    global COLL,RIG
    RIG=None;B.clear();MATS.clear();materials();manifest=[]
    def begin(key):
        global COLL
        COLL=bpy.data.collections.new(key);bpy.context.scene.collection.children.link(COLL);manifest.append({'key':key,'collection':key})
    for axis in ['x','y']:
        for variant in ['low','tall']:
            key=f'wall_{variant}_{axis}';begin(key);h=1.2 if variant=='low' else 4.45
            size=(1,.20,h) if axis=='x' else (.20,1,h)
            box('Old brick masonry',(0,0,h/2),size,'brick',.008)
            box('Concrete foundation',(0,0,.19),(1,.235,.38) if axis=='x' else (.235,1,.38),'mortar',.008)
            box('Coping',(0,0,h+.025),(1.025,.255,.075) if axis=='x' else (.255,1.025,.075),'mortar',.006)
            if variant=='tall':
                def panel(name,u,z,w,hh,dep,material):
                    return box(name,(u,.12+dep/2,z) if axis=='x' else (.12+dep/2,u,z),(w,dep,hh) if axis=='x' else (dep,w,hh),material,.006)
                panel('Recessed frame',0,2.82,.70,1.28,.075,'metal');panel('Dark glass',0,2.82,.58,1.13,.082,'glass')
                for u in [-.25,0,.25]:panel('Window bar',u,2.82,.018,1.16,.11,'metal')
                panel('Window sill',0,2.19,.77,.075,.18,'mortar');panel('Sash',0,2.80,.61,.035,.12,'metal')
                panel('Lintel',0,3.50,.80,.16,.04,'brick')
    begin('fire_escape')
    for z in [2.05,3.9]:
        for x in [-.5,.5]:rod('Platform beam',(x,-.5,z),(x,.6,z),.018,'metal')
        for y in [-.42+i*.1 for i in range(11)]:rod('Grating',(-.5,y,z),(.5,y,z),.011,'metal')
        for x in [-.5+i*.125 for i in range(9)]:rod('Railing upright',(x,.57,z),(x,.57,z+.57),.012,'metal')
        rod('Railing top',(-.52,.57,z+.57),(.52,.57,z+.57),.018,'metal')
    for i in range(14):
        z=.4+i*.25;rod('Ladder rung',(.65,0,z),(.97,0,z),.015,'metal')
    for x in [.65,.97]:rod('Ladder rail',(x,0,.3),(x,0,4.0),.02,'metal')
    for o in COLL.objects:
        x,y,z=o.location;o.location=(-y,x,z);o.rotation_euler.z+=math.pi/2
    begin('service_pipe');rod('Drainpipe',(0,0,0),(0,0,4.30),.045,'metal')
    for z in [.3,1.3,2.4,3.7]:box('Wall bracket',(0,-.04,z),(.15,.10,.04),'rust',.003)
    begin('aircon');box('Air conditioner',(0,0,2.60),(.70,.45,.43),'mortar');
    for z in [2.45+i*.04 for i in range(8)]:box('Vent slot',(0,.234,z),(.56,.018,.012),'metal',.001)
    for opened in [False,True]:
        begin('door_open' if opened else 'door')
        for x in [-.48,.48]:box('Jamb',(x,0,1.04),(.10,.23,2.08),'mortar')
        box('Lintel',(0,0,2.12),(1.1,.23,.16),'mortar')
        panel=box('Scored steel door',(0,.025,1.02),(.86,.1,2.04),'metal');parts=[panel]
        parts.append(box('Inspection hatch',(0,.086,1.44),(.19,.025,.16),'leather',.003))
        parts.append(rod('Handle',(.29,.084,1.04),(.29,.16,1.04),.014,'brass'))
        parts.append(box('Kick plate',(0,.084,.22),(.77,.015,.22),'rust',.002))
        for i in range(8):parts.append(rod('Scratched paint',(-.30+i*.08,.082,.72+i*.065),(-.24+i*.07,.082,.79+i*.066),.002,'mortar'))
        if opened:
            for o in parts:
                p=o.location.copy();o.location=(-.43+p.y,.43+p.x,p.z);o.rotation_euler.z+=math.pi/2
    begin('lamp');box('Service lamp',(0,0,2.64),(.82,.16,.13),'metal');box('Fluorescent tube',(0,.1,2.63),(.72,.05,.05),'fluorescent',.008)
    rod('Service lamp pole',(-.41,-.08,0),(-.41,-.08,2.64),.035,'metal');box('Pole footing',(-.41,-.08,.04),(.16,.16,.08),'rust',.012)
    begin('window');box('Barred window',(0,0,1.0),(.85,.10,1.0),'glass')
    for x in [-.35,-.175,0,.175,.35]:rod('Iron bar',(x,.07,.52),(x,.07,1.48),.012,'metal')
    begin('dumpster');box('Dented bin',(0,0,.62),(1.90,1.90,1.13),'dumpster',.06);box('Lid',(0,0,1.21),(2.02,2.02,.09),'metal',.025)
    for x in [-.70,-.35,0,.35,.70]:box('Lid ridge',(x,0,1.27),(.045,1.86,.018),'metal',.008)
    for x in [-.75,.75]:
        for y in [-.75,.75]:ball('Caster',(x,y,.065),(.085,.085,.07),'leather')
    rng=random.Random(12)
    for i in range(10):
        x=rng.uniform(-1,1);y=rng.uniform(-1.1,.9);z=1.32 if i<4 else .14
        sack=ball('Rubbish sack',(x,y,z),(.23,.23,.21),'leather')
        for v in sack.data.vertices:
            wrinkle=1+.10*math.sin(math.atan2(v.co.y,v.co.x)*9+v.co.z*41);v.co.x*=wrinkle;v.co.y*=wrinkle
        rod('Bag tie',(x,y,z+.14),(x+.016,y,z+.24),.012,'leather')
    box('Faded label',(.30,.96,.78),(.47,.009,.22),'paper',.001)
    for i in range(14):rod('Oxidized weld',(-.82+i*.12,.958,.25),(-.8+i*.115,.958,.63+rng.random()*.3),.004,'rust')
    begin('crate');box('Packing crate',(0,0,.27),(.58,.5,.54),'wood')
    for z in [.07,.22,.37]:box('Slat gap',(0,.259,z),(.57,.009,.012),'leather',.001)
    begin('bottle');rod('Bottle',(0,0,0),(0,0,.20),.045,'glass');rod('Neck',(0,0,.20),(0,0,.28),.018,'glass')
    begin('key');bpy.ops.mesh.primitive_torus_add(major_radius=.074,minor_radius=.014,location=(0,0,.024));register(bpy.context.object,'brass')
    box('Shaft',(0,.13,.024),(.023,.18,.023),'brass',.004);box('Teeth',(.029,.205,.024),(.075,.024,.024),'brass',.002);box('Ribbon',(-.03,-.11,.009),(.05,.14,.012),'red',.003)
    for i in range(4):
        begin('floor'+str(i));o=box('Wet paving',(0,0,-.023),(1,1,.046),'stone',0)
        layer=o.data.uv_layers.active
        for p in layer.data:p.uv.x+=i*.19;p.uv.y+=i*.23
        if i==1:box('Discarded flyer',(.22,.1,.003),(.18,.12,.003),'paper',0)
        if i==2:
            for k in range(3):rod('Cigarette end',(-.25+k*.13,.11,.013),(-.20+k*.13,.14,.013),.009,'paper')
    begin('drain')
    box('Drain recess',(0,0,.004),(.70,.50,.006),'leather',.001)
    for y in [-.21+i*.06 for i in range(8)]:box('Grating',(0,y,.012),(.66,.018,.015),'metal',.003)
    B.STYLE['samples']=24;B.STYLE['light']['key']=[.71,.81,.84];B.STYLE['light']['fill']=[.35,.47,.57];B.setup_camera()
    bpy.context.view_layer.update()
    for cfg in manifest:
        points=[]
        for o in bpy.data.collections[cfg['collection']].objects:
            if o.type!='MESH':continue
            for v in o.bound_box:
                p=o.matrix_world@Vector(v);points.append(((p.y-p.x)*44,(p.x+p.y)*22-p.z*53.888))
        cfg['bounds']=[math.floor(min(p[0] for p in points)-3),math.floor(min(p[1] for p in points)-3),math.ceil(max(p[0] for p in points)+3),math.ceil(max(p[1] for p in points)+3)]
    bpy.context.scene['export_manifest']=json.dumps(manifest);save(SRC/'ny-environment.blend')

if __name__=='__main__':
    requested=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['player','contact','environment']
    for kind in requested:environment() if kind=='environment' else actor(kind)
