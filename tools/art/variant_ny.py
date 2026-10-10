"""Material edit in the saved actor source; export separately without rebuilding."""
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets/walk/source'
bpy.ops.wm.open_mainfile(filepath=str(SRC/'ny-player.blend'))
bpy.data.materials['wool'].node_tree.nodes['Garment tint'].inputs[2].default_value=(.55,.33,.22,1)
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'ny-player-variant.blend'))
