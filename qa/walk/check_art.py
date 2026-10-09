import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
base=ROOT/'assets/walk/generated'
one=json.loads((base/'index.json').read_text())['assets']['player']
two=json.loads((base/'variant/index.json').read_text())['assets']['player']
assert one==two
a=Image.open(base/'player.png').convert('RGBA')
b=Image.open(base/'variant/player.png').convert('RGBA')
w,h=one['size'];assert a.size==(w*9,h*8) and b.size==a.size
frames=[]
for row in range(8):
    for column in range(9):
        crop=(column*w,row*h,(column+1)*w,(row+1)*h)
        ca=a.crop(crop);cb=b.crop(crop)
        assert ca.getchannel('A').getbbox() and ca.getchannel('A').getextrema()[0]==0
        assert ImageChops.difference(ca.convert('RGB'),cb.convert('RGB')).getbbox()
        if column>0:
            idle=a.crop((0,row*h,w,(row+1)*h))
            assert ImageChops.difference(ca.convert('RGB'),idle.convert('RGB')).getbbox()
        frames.append([row,column])
# A clear small comparison rather than a huge animation atlas.
sheet=Image.new('RGB',(8*128,2*180+45),'#182125');d=ImageDraw.Draw(sheet)
d.text((14,10),'Shared model | coat variation | 8 directions',fill='#dcc498')
for row in range(8):
    for i,img in enumerate((a,b)):
        tile=img.crop((0,row*h,w,(row+1)*h)).resize((128,160))
        sheet.paste(tile,(row*128,40+i*180),tile)
sheet.save(ROOT/'qa/walk/coat-comparison.png')
report={'status':'PASS','frames':len(frames),'directions':8,'walk_frames_per_direction':8,'idle_per_direction':1,'identical_anchors_and_dimensions':True,'all_frames_changed_by_material_edit':True,'projection':{'width':88,'height':44},'atlas_sha256':hashlib.sha256((base/'player.png').read_bytes()).hexdigest(),'variant_sha256':hashlib.sha256((base/'variant/player.png').read_bytes()).hexdigest()}
(ROOT/'qa/walk/art-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
