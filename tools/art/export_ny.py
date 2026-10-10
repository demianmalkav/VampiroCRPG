"""Export named clips/resources from edited .blend sources, preserving source edits."""
import argparse, hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Vector
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/walk/generated'
PPU=62.2253967444

def configure(bounds):
    minx,miny,maxx,maxy=bounds;w,h=maxx-minx,maxy-miny;cx=(minx+maxx)/2;cy=(miny+maxy)/2
    target=Vector((-cx/(PPU*math.sqrt(2)),cx/(PPU*math.sqrt(2)),-cy/(PPU*math.cos(math.pi/6))))
    camera=bpy.context.scene.camera;camera.location=target+Vector((8,8,math.sqrt(128)*math.tan(math.pi/6)));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.sensor_fit='VERTICAL';camera.data.ortho_scale=h/PPU
    s=bpy.context.scene;s.render.resolution_x=w*2;s.render.resolution_y=h*2;s.render.film_transparent=True;s.render.image_settings.color_mode='RGBA'
    return {'size':[w*2,h*2],'anchor':[-minx*2,-miny*2],'scale':.5}

def export(source,out,preview=False,only=None):
    out.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(source))
    manifest=json.loads(bpy.context.scene['export_manifest'])
    indexpath=out/'index.json';index={'assets':{}}
    for cfg in manifest:
        if only and cfg['key']!=only:continue
        for item in manifest:
            for o in bpy.data.collections[item['collection']].objects:o.hide_render=item['key']!=cfg['key']
        meta=configure(cfg['bounds']);clips=cfg.get('clips');frames_dir=out/'frames';frames_dir.mkdir(exist_ok=True)
        if clips:
            # This chooses existing saved animation frames, not a new procedural pose.
            root=bpy.data.objects[cfg['root']];dirs=cfg['directions'];columns=sum(c['count'] for c in clips.values());w,h=meta['size'];sheet=Image.new('RGBA',(w*columns,h*len(dirs)))
            for row,(dx,dy) in enumerate(dirs):
                if preview and row not in [2,4,6]:continue
                col=0
                for name,c in clips.items():
                    for f in range(c['count']):
                        if preview and (name!='idle' or f):col+=1;continue
                        bpy.context.scene.frame_set(c['start']+f);root.rotation_euler.z=math.atan2(-dx,dy)
                        file=frames_dir/f"{cfg['key']}-{name}-{row}-{f}.png";bpy.context.scene.render.filepath=str(file);bpy.ops.render.render(write_still=True)
                        im=Image.open(file).convert('RGBA');sheet.alpha_composite(im,(col*w,row*h));col+=1
            offset=0;metadata={}
            for name,c in clips.items():metadata[name]={'column':offset,'count':c['count'],'duration_ms':c['duration_ms'],'loop':c['loop']};offset+=c['count']
            meta.update(columns=columns,rows=len(dirs),frames=columns,clips=metadata,directions=dirs);sheet.save(out/(cfg['key']+('.preview.png' if preview else '.png')))
        else:
            bpy.context.scene.render.filepath=str(out/(cfg['key']+'.png'));bpy.ops.render.render(write_still=True)
        meta.update(file=cfg['key']+'.png',source=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        if not preview:index['assets'][cfg['key']]=meta
        print('EXPORT_DONE',cfg['key'],flush=True)
    if not preview:
        latest=json.loads(indexpath.read_text()) if indexpath.exists() else {'assets':{}}
        latest['assets'].update(index['assets']);index=latest
        index.update(style='ny-nocturno-02',producer='Blender '+bpy.app.version_string,pixels_per_unit=PPU,projection={'tile_width':88,'tile_height':44,'height_scale':PPU*math.cos(math.pi/6)})
        indexpath.write_text(json.dumps(index,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('--out',type=Path,default=OUT);p.add_argument('--preview',action='store_true');p.add_argument('--only');a=p.parse_args();export(a.source.resolve(),a.out.resolve(),a.preview,a.only)
