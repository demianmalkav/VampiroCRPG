# AGENTS.md

This repository is the technical source of truth for VampiroCRPG.

## Before changing anything
1. Inspect the existing implementation and related docs.
2. Do not invent architecture that conflicts with accepted decisions.
3. If requirements are ambiguous, mark `NEEDS_DECISION` rather than guessing.
4. If a fact cannot be verified, mark `UNVERIFIED`.
5. If a requested change conflicts with architecture, mark `ARCHITECTURE_CONFLICT`.

## Permanent project rules
- `main` should remain coherent and recoverable.
- Prefer small, reviewable changes.
- Every non-trivial system change should include tests and documentation.
- Do not introduce major dependencies or change save schemas without an approved architectural decision.
- Content should be data-driven when practical.
- Keep engine, simulation, gameplay, narrative, presentation, and content concerns separated.
- Core runtime systems should be deterministic and work offline without an LLM.
- Do not scale content production before validating the relevant systems.

## Source-of-truth split
- Google Drive: project state, roadmap, decisions, vision, design bibles.
- GitHub: code, tests, tools, schemas, technical documentation, implemented architecture.

## Current phase
Preproduction / Fallout 2 assimilation. A/B are authorized and verified within their isolated Python proof; traversable C sample 02 is rejected and has three known spatial defects. CE Linux reference behavior is partially measured. Campaign: single-player New York first, possible online later; production technology remains undecided. Read PROJECT_STATE_MASTER and docs/TECHNICAL_STATE.md for live scope.

Initial A/B/C prototype scopes were defined before their implementation. Production changes require a bounded target and relevant contract; do not treat this historical gate as a ban on already authorized prototype work.

## Direction and communication
- Direction delegates routine technical choices and control-file maintenance to the assistant. Execute NEXT from PROJECT_STATE_MASTER when asked to continue; do not require the user to follow GitHub/Drive control files.
- B's minimum headless profile was authorized in conversation. A request to continue does not require repeating an already resolved approval.
- When direction's judgment is actually needed, explain the concrete decision, alternatives and consequences in the conversation. Control documents are continuity aids, not a substitute for that explanation.
- Keep completion criteria, bounded retries, material checkpoints and small semantic commits. Reopen a closed phase only for a failure or new evidence.

## Presentation target
- Direction wants a Fallout-like traversable world with an avatar, world inspection and an observation text visor. The existing scene choice panel validates rules but is not an accepted game format.
- Browser execution is permitted if it delivers that spatial experience. Do not confuse delivery technology with interaction design. Prioritize a small navigable scene over adding or polishing choice buttons.

## Definition of Done
A feature is done only when it is implemented, tested, integrated, documented, regression-checked, and accepted by direction.

