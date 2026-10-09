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
M2 — verified headless A/B proof / preproduction. A and the minimum B profile are authorized for this isolated Python proof; production technology remains undecided.

No game code should be added until the initial research and architecture pass defines the implementation target.

## Direction and communication
- Direction delegates routine technical choices and control-file maintenance to the assistant. Execute NEXT from PROJECT_STATE_MASTER when asked to continue; do not require the user to follow GitHub/Drive control files.
- B's minimum headless profile was authorized in conversation. A request to continue does not require repeating an already resolved approval.
- When direction's judgment is actually needed, explain the concrete decision, alternatives and consequences in the conversation. Control documents are continuity aids, not a substitute for that explanation.
- Keep completion criteria, bounded retries, material checkpoints and small semantic commits. Reopen a closed phase only for a failure or new evidence.

## Definition of Done
A feature is done only when it is implemented, tested, integrated, documented, regression-checked, and accepted by direction.

