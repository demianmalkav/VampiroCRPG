"""Build an offline playable folder with editable art; smoke-test extracted bundle."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/'dist';BUNDLE=DIST/'El-pasaje'
if BUNDLE.exists():shutil.rmtree(BUNDLE)
BUNDLE.mkdir(parents=True)
selected=['proof/__init__.py','proof/m2','proof/m2b','proof/walk','assets/walk/generated','tools/art','LEEME.txt','iniciar-pasaje.cmd']
for name in selected:
    src=ROOT/name;dst=BUNDLE/name
    if src.is_dir():
        shutil.copytree(src,dst,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.blend1','frames','*.preview.png'))
    else:
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for src in (ROOT/'assets/walk/source').iterdir():
    if src.name.startswith('ny-') and src.suffix in ['.blend','.json'] or src.name in ['base-human.obj','material-atlas.png','style.json','MAKEHUMAN_LICENSE.md','NY_README.md']:
        target=BUNDLE/'assets/walk/source'/src.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
for name in ['art-result.json','browser-result.json','initial-desktop.png','completed-desktop.png','initial-mobile.png','pickup-desktop.png','coat-comparison.png','base-coat-in-scene.png','variant-coat-in-scene.png']:
    if (ROOT/'qa/walk'/name).exists():
        target=BUNDLE/'verification'/name;target.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'qa/walk'/name,target)
with tempfile.TemporaryDirectory() as temp:
    shutil.copytree(BUNDLE,Path(temp)/'El-pasaje')
    script="""from proof.walk.__main__ import make_server
from urllib.request import urlopen
import threading,json
s=make_server(0)
threading.Thread(target=s.serve_forever,daemon=True).start()
u=f'http://127.0.0.1:{s.server_port}'
assert urlopen(u).status==200
assert 'player' in json.load(urlopen(u+'/art/index.json'))['assets']
assert urlopen(u+'/art/player.png').read(8)==b'\\x89PNG\\r\\n\\x1a\\n'
s.shutdown();s.server_close()
print('EXTRACTED_BUNDLE_PASS')
"""
    subprocess.run([sys.executable,'-c',script],cwd=Path(temp)/'El-pasaje',check=True)
report={'status':'PASS','files':len(list(BUNDLE.rglob('*'))),'runtime':'Python 3.11+ stdlib + pre-exported PNG','fresh_folder_start':True,'blender_required_to_play':False}
(ROOT/'qa/walk/package-result.json').write_text(json.dumps(report,indent=2)+'\n')
# Artifact is the playable folder directly (GitHub adds the outer ZIP).
print(json.dumps(report))
