# Technical State

Phase: M2 — core A executable proof / preproduction  
Approval: director authorization recorded as D-011; game engine/language undecided.

DONE: implemented standard-library Python proof: causal knowledge/messages/records/processes, permissions, transactional scheduler, receipts and internal snapshots. Six actors/three locations, bounded cleanup and inquiry procedures. CLI can narrate, save/resume and execute acceptance tests.

EVIDENCE: 29 tests PASS, covering NQR-01–09 and F-01–07; four fixtures agree with expected outcomes; per-commit save/load states are semantically equal; CLI save/resume and wrong-case rejection verified. [Report](../tests/results/m2_core_a_run.json), [result](M2_CORE_A_RESULT_01.md), [run instructions](../proof/README.md).

OPEN: direction's review of observed behavior; minimum B rules (blood, feeding, Beast, willpower, morality, time/RNG). No graphics, general inventory/combat, production save compatibility or large-world performance validation. Godot is not installed or selected.

NEXT: prepare the minimum B rules proposal from existing translations and resolve open choices before implementation. Do not reopen completed source extraction without new evidence.

The authoritative executive state remains PROJECT_STATE_MASTER in Drive. This file tracks the technical branch; the PR remains a draft pending review and is not merged into main.

