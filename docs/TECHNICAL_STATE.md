# Technical State

Phase: M2 — A/B verified with a minimal scene presentation / preproduction. Routine technical/control work delegated to the assistant; production engine undecided.

DONE: local stdlib Python server and HTML/CSS/canvas scene drive the existing A/B authority. Actual feeding, paid lucid choices, seal, travel, cleanup message, sleep, player observation and save/load. Fixtures supply only the first night boundary; later choices come from the player. No Godot or major runtime dependency introduced; B save schema unchanged.

EVIDENCE: [scene report](../tests/results/m2_scene_run.json): 68 tests PASS (59 A/B regression, nine scene), seven B cases PASS. Private save/reload during a paid action, retries/stale revisions, rejection rollback, acquired knowledge and HTTP boundaries checked. [Actual JS event harness](../tests/results/m2_scene_ui_run.json): eight checks PASS with real server; not browser layout coverage. Historical A/B reports preserved. [Scene result](M2_SCENE_RESULT_01.md), [run instructions](../proof/scene/README.md).

OPEN: browser appearance/layout UNVERIFIED (no executable; download failed), player experience/pace/balance, general perception/navigation, items/inventory/combat and production. Art is provisional. Trauma remains a pending marker; zero blood/torpor remain excluded. Draft branches unmerged.

NEXT: verify this scene in a real browser and play both decision paths; fix observed issues. Then define one small playable increment for items/editing or navigation, explaining the experience choice in conversation when direction's judgment is needed. Do not reopen closed A/B or select/install a production engine merely to present this proof.

PROJECT_STATE_MASTER is the executive source. Control files are assistant-maintained continuity aids, not required reading for direction.
