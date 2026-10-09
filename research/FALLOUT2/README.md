# Fallout 2 System Analysis

Purpose: study Fallout 2 as a design and engineering corpus, then abstract useful principles without inheriting its visual identity or assuming its concrete implementation should be copied.

## Current research documents

Read these before making architecture claims from the Fallout 2 corpus:

- `SYSTEM_MATRIX.md` — promoted subsystem findings and KEEP / MODIFY / REPLACE dispositions.
- `DIALOGUE_TIME_PERSISTENCE.md` — targeted analysis for dialogue, simulation time, location persistence and M2 relevance.
- `QUEUE_LIFETIME_CORRECTION.md` — mandatory correction: the global event queue is save-persistent, but map departure deliberately clears/resolves some map-bound event types, including ordinary script timers in the inspected implementation. Do not claim that every queued timer survives leaving a map.

The latest correction/narrower finding supersedes older wording when the documents conflict.

## Analysis template
For each subsystem:
- Original function
- Player-facing behavior
- Data/state involved
- Dependencies
- Strengths
- Limitations
- General design principle
- Our disposition: KEEP / MODIFY / REPLACE / REMOVE
- Candidate equivalent in VampiroCRPG
- Validation method

## Initial subsystems
- Movement and maps
- Interaction model
- Dialogue
- Scripting
- Quests and world state
- Combat and action points
- Inventory and items
- Skills / checks
- Reputation
- Time
- NPC AI
- Party
- Random encounters
- Save/load and persistence
- UI
- Animation
- Navigation / pathfinding

## Evidence rule

The primary behavioral target is Fallout 2. Public reimplementations such as `alexbatalov/fallout2-ce` are engineering evidence used to understand mechanisms. A pattern observed there is not automatically a project architecture decision and should not be silently generalized beyond what was inspected.

The goal is abstraction and behavioral understanding, not visual reproduction or source-code transplantation.
