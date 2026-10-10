# Technical State

Phase: M2 C — first traversable sample verified and played by direction. Movement, observation visor and door worked broadly; initial art was rejected. Two improved conceptual references were approved as artistic direction, not as integrated game assets. First game location is New York. Routine technical/control work delegated.

DONE: isolated spatial authority, eight-neighbor deterministic routes without corner cutting, proximity interactions, acquired observations in visor, unique key ownership, locked door/threshold objective, movement save/load/replay, revision/receipt protocol, avatar controls/camera/depth rendering. Existing A/B authority and measurements preserved; this walkthrough does not yet integrate feeding/frenzy.

ART: shared editable Blender model recipe, fixed camera/lights/material palette, idle and eight walking frames in eight directions; regenerate coat material variant and render it in the unchanged session. Exported PNG and editable .blend files are included in the delivery; repository versions recipe/style sources. Initial geometry is simple, not final art.

EVIDENCE: code 05454dfb85e6c19e51c1976aa4a821c6828c8e90, [CI PASS](https://github.com/demianmalkav/VampiroCRPG/actions/runs/37993656561), 80 unit tests (59 A/B, 9 prior scene, 12 spatial), 8 actual browser checks, 72-frame coherence check for both coats, fresh-folder package startup. Additional unchanged B suite: 59 tests and 7 cases PASS. First browser run exposed a null camera on load/reset; guards fixed it and full second run passed. Browser screenshots do not constitute direction's aesthetic acceptance or a Windows runtime check.

DELIVERY: [Drive ZIP](https://drive.google.com/file/d/1EO6JA-I2w6Z9bWltBX-_RZqawpDRVscQ/view?usp=drivesdk), 09_BUILDS. Package includes runtime, pre-exported sprites, editable sources, variant and verification captures. Source runtime requires Python 3.11+ and local browser; no installed Godot or selected production engine.

OPEN: detailed animated art matching the approved references, editable-source reexport, general animation playback, lighting/perception/editor, inventory/combat, A/B spatial integration and production packaging. Turn-based combat is a direction requirement; vehicles/weather are expansion requirements, not implemented features. [Animation and interaction proposal](ANIMATION_INTERACTION_FOUNDATION_01.md). All draft branches remain unmerged. C saves use m2-walk-save-1, separate from unchanged A/B saves.

NEXT: targeted New York by Night review for initial sector/chronology; build the playable art sample using separate environment resources, a reusable edited character source, eight-direction walk and one additional integrated action. Establish named clips and edited-source export rather than scaling the primitive recipe. Night is seductive and hostile, with varied grooming, wear, fatigue and intoxication. Preserve authority and existing evidence; judge the new finish in motion.

PROJECT_STATE_MASTER remains the executive source.
