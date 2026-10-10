"""Fetch pinned CC0 mesh for authoring; verify inputs, never overwrite edited .blend."""
import hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
SRC=Path(__file__).resolve().parents[2]/'assets/walk/source'
spec=json.loads((SRC/'ny-provenance.json').read_text())
mesh=SRC/'base-human.obj'
if not mesh.exists():
    request=Request(spec['base_mesh']['url'],headers={'User-Agent':'VampiroCRPG-authoring'})
    with urlopen(request,timeout=60) as response:data=response.read()
    if hashlib.sha256(data).hexdigest()!=spec['base_mesh']['sha256']:raise ValueError('Upstream mesh hash mismatch')
    mesh.write_bytes(data)
for file,key in [('base-human.obj','base_mesh'),('material-atlas.png','material_atlas')]:
    if hashlib.sha256((SRC/file).read_bytes()).hexdigest()!=spec[key]['sha256']:raise ValueError('Authoring input hash mismatch: '+file)
print('NY_AUTHORING_INPUTS_VERIFIED')
