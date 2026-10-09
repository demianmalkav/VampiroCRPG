# Technical State

Phase: M2 — A/B verified; panel presentation does not meet the intended spatial CRPG experience / preproduction. Routine technical/control work delegated to the assistant; production engine undecided.

DONE: local stdlib Python server and HTML/CSS/canvas scene drive the existing A/B authority. Actual feeding, paid lucid choices, seal, travel, cleanup message, sleep, player observation and save/load. Fixtures supply only the first night boundary; later choices come from the player. No Godot or major runtime dependency introduced; B save schema unchanged.

EVIDENCE: [scene report](../tests/results/m2_scene_run.json): 68 tests PASS (59 A/B regression, nine scene), seven B cases PASS. Private save/reload during a paid action, retries/stale revisions, rejection rollback, acquired knowledge and HTTP boundaries checked. [Actual JS event harness](../tests/results/m2_scene_ui_run.json): eight checks PASS with real server; not browser layout coverage. Historical A/B reports preserved. [Scene result](M2_SCENE_RESULT_01.md), [run instructions](../proof/scene/README.md).

OPEN: browser appearance/layout UNVERIFIED (no executable; download failed), player experience/pace/balance, general perception/navigation, items/inventory/combat and production. Art is provisional. Trauma remains a pending marker; zero blood/torpor remain excluded. Draft branches unmerged.

DIRECTION: The user tried the panel and clarified that the target is a Fallout-like world traversed by an avatar. Inspecting people/objects should produce perceived descriptions in a text visor; actions must originate from contact with that world. Browser delivery is acceptable if it supports that experience. The existing choice panel is a rules harness, not an accepted game presentation.

NEXT: define the minimum spatial authority and implement one small traversable isometric map: avatar movement to clicked destinations, blocked terrain/pathfinding, depth ordering, selectable people/objects and a text visor of acquired observations. Bind existing feeding/actions to reachable proximity. Keep A/B evidence and save schemas intact; define any spatial extension separately before coding. Do not prioritize polishing the panel or infer a production-engine choice from this correction.

PROJECT_STATE_MASTER is the executive source. Control files are assistant-maintained continuity aids, not required reading for direction.
