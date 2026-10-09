"""Blender 4.5: shared editable models/materials -> transparent sprites.

Use Python 3.11 with bpy 4.5.14 and Pillow 11.3.0.
WALK_STYLE, WALK_OUT, WALK_SOURCE select an art variant; never alter simulation.
The playable bundle needs neither Blender nor Pillow.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
STYLE_FILE=Path(os.environ.get('WALK_STYLE',ROOT/'assets/walk/source/style.json'))
STYLE=json.loads(STYLE_FILE.read_text())
OUT=Path(os.environ.get('WALK_OUT',ROOT/'assets/walk/generated'))
SOURCE=Path(os.environ.get('WALK_SOURCE',ROOT/'assets/walk/source'))
OUT.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
SCALE=STYLE['render_scale'];PPU=STYLE['pixels_per_unit'];ELEV=math.radians(STYLE['camera_elevation'])
MATERIALS={};PARTS=[]


def material(name, color=None):
    if name in MATERIALS: return MATERIALS[name]
    hexcolor=color or STYLE['materials'][name]
    rgb=[int(hexcolor[i:i+2],16)/255 for i in (1,3,5)]
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*rgb,1);mat.use_nodes=True
    node=mat.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*rgb,1)
    node.inputs['Roughness'].default_value=.8
    if name in ('metal','brass'): node.inputs['Metallic'].default_value=.55
    MATERIALS[name]=mat;return mat


def clear():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    PARTS.clear()


def finish(obj,name,mat):
    obj.name=name;obj.data.materials.append(material(mat));PARTS.append(obj)
    return obj


def box(name,pos,size,mat,bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=pos);obj=bpy.context.object
    obj.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        modifier=obj.modifiers.new('Worn edges','BEVEL');modifier.width=bevel;modifier.segments=2
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return finish(obj,name,mat)


def sphere(name,pos,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=pos)
    obj=bpy.context.object;obj.scale=size
    for polygon in obj.data.polygons:polygon.use_smooth=True
    return finish(obj,name,mat)


def cylinder(name,a,b,radius,mat):
    vec=Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=vec.length,location=(Vector(a)+Vector(b))/2)
    obj=bpy.context.object;obj.rotation_euler=vec.to_track_quat('Z','Y').to_euler()
    obj.modifiers.new('Soft edges','BEVEL').width=.01
    return finish(obj,name,mat)


def link(obj,a,b,radius):
    vec=Vector(b)-Vector(a);obj.location=(Vector(a)+Vector(b))/2
    obj.rotation_euler=vec.to_track_quat('Z','Y').to_euler();obj.scale=(1,1,vec.length/obj['rest_length'])


def setup_camera(bounds=None):
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=STYLE['samples']
    scene.cycles.use_denoising=True;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.resolution_percentage=100;scene.render.threads_mode='FIXED';scene.render.threads=4
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=.2
    if bounds is None: bounds=(-64,-130,64,30)
    minx,miny,maxx,maxy=bounds;width=math.ceil(maxx-minx);height=math.ceil(maxy-miny)
    cx=(minx+maxx)/2;cy=(miny+maxy)/2
    target=Vector((-cx/(PPU*math.sqrt(2)),cx/(PPU*math.sqrt(2)),-cy/(PPU*math.cos(ELEV))))
    bpy.ops.object.camera_add(location=target+Vector((8,8,math.sqrt(128)*math.tan(ELEV))))
    camera=bpy.context.object;camera.name='Fixed production camera';camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.sensor_fit='VERTICAL';camera.data.ortho_scale=height/PPU;scene.camera=camera
    scene.render.resolution_x=width*SCALE;scene.render.resolution_y=height*SCALE
    for name,location,energy,color,size in [('Warm key',(-3,1,6),450,STYLE['light']['key'],4),('Cold fill',(3,-2,4),180,STYLE['light']['fill'],5)]:
        bpy.ops.object.light_add(type='AREA',location=location);light=bpy.context.object
        light.name=name;light.data.energy=energy;light.data.color=color;light.data.shape='DISK';light.data.size=size
        light.rotation_euler=(-light.location).to_track_quat('-Z','Y').to_euler()
    scene.world.use_nodes=True;world=scene.world.node_tree.nodes.get('Background');world.inputs[0].default_value=(.32,.40,.49,1);world.inputs[1].default_value=STYLE['light']['world_strength']
    return {'size':[width*SCALE,height*SCALE],'anchor':[-minx*SCALE,-miny*SCALE],'scale':1/SCALE}


def character(kind):
    clear();cfg=STYLE[kind];coat=cfg['coat_material']
    sphere('Torso',(0,0,1.21),(.235,.14,.33),coat)
    box('Coat hem',(0,0,.85),(.46,.27,.28),coat)
    box('Left lapel',(-.075,.15,1.34),(.08,.03,.21),'lining',.008)
    box('Right lapel',(.075,.15,1.34),(.08,.03,.21),'lining',.008)
    box('Shirt',(0,.15,1.27),(.08,.025,.24),'shirt',.008)
    cylinder('Neck',(0,0,1.46),(0,0,1.58),.065,'skin')
    sphere('Head',(0,0,1.67),(.128,.111,.17),'skin')
    sphere('Hair',(0,-.018,1.77),(.13,.105,.105),cfg['hair_material'])
    sphere('Nose',(0,.11,1.665),(.025,.035,.028),'skin')
    for x in (-.047,.047): sphere('Eye',(x,.105,1.70),(.017,.012,.010),'hair')
    for z in (1.06,1.17): sphere('Coat button',(0,.148,z),(.012,.012,.012),'metal')
    limbs=[];boots=[];hands=[]
    for side in (-1,1):
        hip=(side*.11,0,.83);knee=(side*.115,0,.43);foot=(side*.12,.035,.075)
        for name,a,b,r,mat in [('Thigh',hip,knee,.073,'denim'),('Shin',knee,foot,.060,'denim')]:
            obj=cylinder(name+str(side),a,b,r,mat);obj['rest_length']=(Vector(b)-Vector(a)).length;limbs.append(obj)
        boots.append(box('Boot'+str(side),(side*.12,.05,.07),(.16,.28,.14),'boots',.025))
        shoulder=(side*.225,0,1.38);elbow=(side*.28,0,1.13);hand=(side*.28,.02,.95)
        for name,a,b,r in [('Upper arm',shoulder,elbow,.067),('Sleeve',elbow,hand,.057)]:
            obj=cylinder(name+str(side),a,b,r,coat);obj['rest_length']=(Vector(b)-Vector(a)).length;limbs.append(obj)
        hands.append(sphere('Hand'+str(side),hand,(.055,.045,.075),'skin'))
    bpy.ops.object.empty_add(type='PLAIN_AXES');root=bpy.context.object;root.name=kind+' model root'
    for obj in PARTS:obj.parent=root
    root.scale.z=cfg['height']/1.86
    def pose(phase):
        for index,side in enumerate((-1,1)):
            swing=0 if phase is None else math.sin(phase+index*math.pi);lift=0 if phase is None else max(0,math.cos(phase+index*math.pi))*.08
            hip=(side*.11,0,.83);knee=(side*.115,swing*.08,.43+lift*.2);foot=(side*.12,swing*.18,.075+lift)
            offset=index*4
            link(limbs[offset],hip,knee,.073);link(limbs[offset+1],knee,foot,.06)
            boots[index].location=(side*.12,swing*.18+.05,.07+lift)
            shoulder=(side*.225,0,1.38);elbow=(side*.28,-swing*.085,1.13);hand=(side*.28,-swing*.14,.95)
            link(limbs[offset+2],shoulder,elbow,.067);link(limbs[offset+3],elbow,hand,.057);hands[index].location=hand
    meta=setup_camera();frame_files=[]
    count=9 if kind=='player' else 1;directions=STYLE['directions'] if kind=='player' else [(0,1)]
    temp=OUT/'frames';temp.mkdir(exist_ok=True)
    for direction,(dx,dy) in enumerate(directions):
        root.rotation_euler.z=math.atan2(-dx,dy)
        for frame in range(count):
            number=direction*count+frame+1;pose(None if frame==0 else (frame-1)*2*math.pi/8)
            for obj in [root,*PARTS]:
                obj.keyframe_insert(data_path='location',frame=number);obj.keyframe_insert(data_path='rotation_euler',frame=number);obj.keyframe_insert(data_path='scale',frame=number)
            bpy.context.scene.frame_set(number)
            file=temp/f'{kind}-{direction}-{frame}.png';bpy.context.scene.render.filepath=str(file)
            bpy.ops.render.render(write_still=True);frame_files.append(file)
    scene=bpy.context.scene;scene.frame_end=len(frame_files);scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/f'{kind}.blend'))
    w,h=meta['size'];sheet=Image.new('RGBA',(w*count,h*len(directions)))
    for i,file in enumerate(frame_files):sheet.alpha_composite(Image.open(file).convert('RGBA'),((i%count)*w,(i//count)*h))
    sheet.save(OUT/f'{kind}.png');meta.update(file=kind+'.png',columns=count,rows=len(directions),frames=count)
    return meta


def environment(kind):
    clear()
    if kind.startswith('wall'):
        along_y=kind.endswith('y');height=1.25 if 'low' in kind else 2.45
        box('Mortar',(0,0,height/2),(.22,1,height) if along_y else (1,.22,height),'mortar',.015)
        for row in range(int(height/.16)):
            for col in range(3):
                u=-.5+(col+.5)*.32+(row%2)*.09
                if u>.5: continue
                pos=(0,u,.08+row*.16) if along_y else (u,0,.08+row*.16)
                size=(.245,.30,.14) if along_y else (.30,.245,.14)
                box('Brick',pos,size,'brick',.009)
        box('Coping',(0,0,height+.025),(.29,1.02,.08) if along_y else (1.02,.29,.08),'metal',.013)
    elif kind=='dumpster':
        box('Dumpster',(0,0,.49),(1.9,1.9,.90),'metal',.05)
        box('Heavy lid',(0,0,.98),(2.02,2.02,.12),'metal',.04)
        for x in (-.72,.72):
            for y in (-.72,.72):sphere('Caster',(x,y,.07),(.10,.10,.08),'boots')
        for x in (-.62,0,.62):box('Reinforcement',(x,.961,.46),(.045,.025,.66),'rust',.006)
        box('Paper label',(.25,.981,.66),(.40,.01,.20),'paper',.002)
        for i in range(6):sphere('Bag',(-.70+(i%3)*.56,-.50+(i//3)*.63,1.08),(.27,.24,.19),'boots')
    elif kind in ('door','door_open'):
        box('Left jamb',(-.48,0,1.07),(.12,.2,2.14),'mortar')
        box('Right jamb',(.48,0,1.07),(.12,.2,2.14),'mortar')
        box('Lintel',(0,0,2.12),(1.08,.2,.15),'mortar')
        box('Door panel',(0,.01,1.025),(.86,.12,2.05),'metal',.035)
        box('Lower reinforcement',(0,.085,.35),(.75,.015,.045),'rust',.004)
        cylinder('Handle',(.26,.1,.99),(.26,.18,.99),.025,'brass')
        box('Small peephole',(0,.084,1.48),(.04,.015,.045),'boots',.003)
        if kind=='door_open':
            for obj in PARTS[3:]:
                p=obj.location.copy();obj.location.x=-.43+(p.y)*.94;obj.location.y=.43+(p.x)*.94;obj.rotation_euler.z+=math.pi/2
    elif kind=='key':
        bpy.ops.mesh.primitive_torus_add(major_segments=20,minor_segments=8,location=(0,0,.035),major_radius=.085,minor_radius=.018)
        finish(bpy.context.object,'Key ring','brass')
        box('Key shaft',(0,.145,.035),(.035,.19,.035),'brass',.005)
        box('Key teeth',(.04,.23,.035),(.095,.045,.035),'brass',.003)
        box('Red ribbon',(-.055,-.13,.015),(.06,.15,.015),'red',.006)
    elif kind=='lamp':
        cylinder('Pole',(0,0,0),(0,0,2.70),.045,'metal')
        cylinder('Arm',(0,0,2.7),(.35,0,2.7),.035,'metal')
        box('Lamp head',(.37,0,2.65),(.34,.18,.09),'metal')
        box('Warm glass',(.37,0,2.595),(.27,.14,.02),'brass',.004)
    elif kind=='window':
        box('Window frame',(0,0,1.0),(1.02,.16,1.25),'metal')
        box('Glass',(0,.09,1.0),(.88,.03,1.10),'glass',.01)
        for x in (-.28,0,.28): box('Bar',(x,.12,1.0),(.025,.025,1.12),'metal',.003)
    elif kind=='crate':
        box('Wooden crate',(0,0,.32),(.62,.55,.64),'wood')
        for z in (.1,.28,.46): box('Slat gap',(0,.281,z),(.6,.012,.012),'boots',.001)
    elif kind=='bottle':
        cylinder('Bottle',(0,0,.025),(0,0,.19),.045,'glass');cylinder('Neck',(0,0,.19),(0,0,.25),.022,'glass')
    bpy.context.view_layer.update();points=[]
    for obj in PARTS:
        for vertex in obj.bound_box:
            v=obj.matrix_world@Vector(vertex);points.append(((v.y-v.x)/math.sqrt(2)*PPU,(v.x+v.y)/math.sqrt(2)*math.sin(ELEV)*PPU-v.z*math.cos(ELEV)*PPU))
    bounds=(min(p[0] for p in points)-12,min(p[1] for p in points)-12,max(p[0] for p in points)+12,max(p[1] for p in points)+12)
    meta=setup_camera(bounds);bpy.context.scene.render.filepath=str(OUT/f'{kind}.png');bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE/f'{kind}.blend'));meta.update(file=kind+'.png')
    return meta


def main():
    requested=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    choices=requested or ['player','contact','wall_low_y','wall_tall_y','wall_tall_x','dumpster','door','door_open','key','lamp','window','crate','bottle']
    index_file=OUT/'index.json';index=json.loads(index_file.read_text()) if index_file.exists() else {'assets':{}}
    for kind in choices:
        index['assets'][kind]=character(kind) if kind in ('player','contact') else environment(kind)
        index.update(style=STYLE['id'],style_sha256=hashlib.sha256(STYLE_FILE.read_bytes()).hexdigest(),producer='Blender '+bpy.app.version_string,
                     pixels_per_unit=PPU,projection={'tile_width':88,'tile_height':44,'height_scale':PPU*math.cos(ELEV)})
        index_file.write_text(json.dumps(index,indent=2)+'\n')
        print('ASSET_DONE',kind,flush=True)
    print('ART_BUILD_COMPLETE',flush=True)


if __name__=='__main__': main()
