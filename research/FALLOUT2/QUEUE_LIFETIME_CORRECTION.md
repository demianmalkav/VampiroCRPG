# Fallout 2 Queue Lifetime — Map Exit Correction

Status: VERIFIED TECHNICAL CORRECTION
Date: 2026-10-08

This note supersedes any earlier wording that could be read as saying every Fallout 2 queued event, especially script timers, automatically survives leaving the current map.

## Verified behavior in `fallout2-ce`

Fallout 2 has a general simulation-time queue and that queue is serialized by the full game save system. However, map departure has an additional lifecycle step: `_map_save_in_game(true)` calls `_queue_leaving_map()` before map exit scripts and map unloading.

`_queue_leaving_map()` iterates event types and clears those whose event-type descriptor marks them as map-leaving-clearable. In the inspected event table, `EVENT_TYPE_SCRIPT` is one of the marked types and has no special preservation handler, so ordinary queued script timer events are removed when leaving the map.

Other event families have their own leave-map behavior depending on the descriptor and optional handler.

Therefore two statements must remain separate:

1. **FULL SAVE/LOAD PERSISTENCE:** the queue is a first-class serialized subsystem, so queued events that remain in the queue can survive saving and loading the game.
2. **MAP-LIFETIME PERSISTENCE:** not every queued event survives a transition away from its current map. Some map-bound event types are deliberately cleared or resolved during map departure.

## Why this matters for VampiroCRPG

This is a decisive boundary for `La Noche que Recuerda`.

The project cannot simply clone Fallout 2 script timers for witness testimony, daytime cleanup, rumor propagation or institution processing, because those consequences must be able to continue after the incident location is unloaded.

The correct abstraction is at least two scheduling scopes:

- **LOCATION/SCENE-LIFETIME EVENTS:** may be cancelled, resolved or transformed when a location unloads.
- **WORLD/PROCESS-LIFETIME EVENTS:** remain scheduled independently of presentation-scene lifetime and can target actors, institutions or processes anywhere in the simulation.

Possible later refinement: actor-lifetime, institution-lifetime or process-owned events, but the critical requirement is that scheduler lifetime is explicit rather than inferred from scene ownership.

## Updated disposition

KEEP from Fallout 2:

- ordered simulation-time scheduling;
- typed event handlers;
- save/load serialization of future events;
- explicit lifecycle handling when leaving a location.

MODIFY/EXTEND:

- event ownership and lifetime must be explicit;
- world/process events must survive location unload;
- scheduled events require stable target IDs and causal parent IDs;
- scene-local event cleanup must never erase persistent social causality accidentally.

## M2 invariant added

**INV-SCHED-01 — LOCATION UNLOAD MUST NOT CANCEL WORLD-CAUSAL EVENTS.**

If W1 has already formed a memory and a future opportunity to tell W2 is scheduled as a world/process event, unloading L1 must not delete that future consequence. Only an explicit causal cancellation — death, loss of access, changed intention, intervention, etc. — may prevent it.

Conversely, purely local presentation events may be safely discarded on location unload when their semantics do not outlive the scene.

## Source locations inspected

- `src/queue.cc`: event-type descriptors, `_queue_clear_type`, `_queue_leaving_map`, queue save/load/process functions.
- `src/map.cc`: `_map_save_in_game(true)` calls `_queue_leaving_map()` before map exit/unload.
- `src/scripts.cc`: script timer creation and timed-procedure dispatch.

This correction should be consulted before freezing the scheduler contract.
