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
M0 — Foundation / preproduction.

No game code should be added until the initial research and architecture pass defines the implementation target.

## Definition of Done
A feature is done only when it is implemented, tested, integrated, documented, regression-checked, and accepted by direction.
