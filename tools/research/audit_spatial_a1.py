"""Measure the rejected C baseline; this is not a Fallout runtime test.

Run from the repository root: python tools/research/audit_spatial_a1.py
An expected defect is evidence of a failure, never an acceptance PASS.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from proof.walk.world import WalkWorld, STEP_MS  # noqa: E402


def source_hash(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def logical_interpolation(world):
    """Equivalent to scene.js at receipt time; excludes speculative render advance."""
    view = world.view()
    if not view['path']:
        return view['pos']
    fraction = view['progress_ms'] / view['step_ms']
    return [a + (b - a) * fraction for a, b in zip(view['pos'], view['path'][0])]


def measure():
    crate = WalkWorld()
    crate_route = crate.route(crate.s['pos'], [3, 4])
    cardinal, diagonal = WalkWorld(), WalkWorld()
    cardinal.command('move', {'cell': [3, 9]})
    diagonal.command('move', {'cell': [4, 9]})
    cardinal.command('advance', {'ms': STEP_MS})
    diagonal.command('advance', {'ms': STEP_MS})
    redirect = WalkWorld()
    redirect.command('move', {'cell': [3, 9]})
    redirect.command('advance', {'ms': 150})
    before = logical_interpolation(redirect)
    before_progress = redirect.s['progress_ms']
    redirect.command('move', {'cell': [4, 10]})
    after = logical_interpolation(redirect)
    observations = [
        dict(id='A1-D01', status='DEFECT_REPRODUCED',
             observed={'crate_cell_free': crate.free([3, 4]), 'route': crate_route},
             expected_contract='Registered solid crate blocks route and entry.'),
        dict(id='A1-D02', status='DEFECT_REPRODUCED',
             observed={'duration_ms': STEP_MS, 'cardinal_arrived': cardinal.s['pos'],
                       'diagonal_arrived': diagonal.s['pos'],
                       'world_speed_ratio': math.sqrt(2)},
             expected_contract='World distance controls duration, not a constant per grid edge.'),
        dict(id='A1-D03', status='DEFECT_REPRODUCED',
             observed={'progress_before_ms': before_progress,
                       'progress_after_ms': redirect.s['progress_ms'],
                       'interpolated_before': before, 'interpolated_after': after,
                       'discontinuity_world_units': math.dist(before, after)},
             expected_contract='Redirect preserves current segment progress and position continuity.'),
    ]
    renderer = (ROOT / 'proof/walk/scene.js').read_text()
    defects_present = (
        crate.free([3, 4]) and crate_route[-1] == [3, 4]
        and cardinal.s['pos'] == [3, 9] and diagonal.s['pos'] == [4, 9]
        and before_progress == 150 and redirect.s['progress_ms'] == 0
        and math.dist(before, after) > 0
        and "asset:'crate',pos:[3,4]" in renderer
    )
    return {
        'kind': 'A1_BASELINE_AUDIT', 'project_base_commit': '8b34f2d2a778dd0922fe6623de9f9f248bd5c475',
        'scope': 'Executed existing Python C authority; renderer interpolation derived from source, no browser or upstream execution.',
        'sources_sha256': {p: source_hash(p) for p in (
            'proof/walk/world.py', 'proof/walk/map.json', 'proof/walk/scene.js',
            'proof/m2/world.py', 'tools/research/audit_spatial_a1.py')},
        'observations': observations,
        'baseline_matches_known_defects': defects_present,
        'acceptance': 'NOT_ACCEPTED', 'runtime_modified': False,
    }


if __name__ == '__main__':
    report = measure()
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    sys.exit(0 if report['baseline_matches_known_defects'] else 1)
