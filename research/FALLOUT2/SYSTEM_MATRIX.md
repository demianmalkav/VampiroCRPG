# Fallout 2 System Matrix

Status: ACTIVE / REOPENED SPATIAL AND PRODUCTION INVESTIGATION — 2026-10-10

Purpose: record verified behavioral and engineering patterns from Fallout 2 and public reimplementations, then decide what VampiroCRPG should KEEP, MODIFY, REPLACE, or REMOVE. This file is an abstraction layer, not a source-code transplant.

## Current evidence and priority

Sample 02 has been rejected for art and world consistency. The current research pass inventories 18 repositories and 75 retrieved files at exact revisions. Source-observed findings are in [Spatial/art/animation findings](SPATIAL_ART_ANIMATION_FINDINGS_01.md), source availability in [Research survey](RESEARCH_SURVEY_2026-10-09.md), and NEXT in [Assimilation plan](ASSIMILATION_PLAN_01.md). Engine adaptation is an open option, not yet selected. That survey checkpoint did not execute external runtimes/tools or parse original data. It is superseded by the measured CE and private-DAT work below.

| New cluster | Source observation | Candidate disposition / required verification |
| --- | --- | --- |
| F2-SPA-001 | Distinct object hex geometry and floor/roof tile geometry with projection helpers. | KEEP explicit coordinate contracts; choose grid after comparison. |
| F2-SPA-002 | Routing and drawing consult registered object instances, elevation and flags; multihex blocking has specific neighbor rules. | KEEP shared identity/occupancy; extend authored footprints. Test visible volume and collision together. |
| F2-SPA-003 | Dedicated flat/nonflat/roof rendering and tile/object lighting. | KEEP layering and occlusion policy; validate visually in motion. |
| F2-SPA-004 | Cursor selection drives object look/examine and text monitor. | KEEP direct world inspection; EXTEND actor-specific perception/knowledge. |
| F2-SPA-005 | Movement checks blockers again while executing and can recalculate. | KEEP execution validation; specify uninterrupted positions and save phases. |
| F2-ART-001 | FRM carries direction, timing, offsets and action-frame metadata. | KEEP metadata discipline; format/color limits depend on selected renderer. |
| F2-ANI-001/002 | Registered sequences coordinate approach, animation and pickup effect at an action frame. | KEEP phases/markers; REPLACE presentation-owned mutation with a tested authority contract. |
| F2-EQU-001 | Armor chooses body art and weapon animation category selects held/attack art. | EXTEND per-item identity; original model does not meet arbitrary layered clothes or exact weapon identity automatically. |
| F2-EXT-001 | sfall adds appearance/animation controls, with executable/runtime dependencies. | Variant-tagged comparison; do not assume CE supports every sfall function. |
| ALT-001 | Modern FOnline has static/dynamic blocking and model layers/attachments. | Candidate comparison only; local single-player cost and VTM turn scheduling unverified. |

The historical scripting/time/persistence cluster remains useful within its scope. [QUEUE_LIFETIME_CORRECTION.md](QUEUE_LIFETIME_CORRECTION.md) explicitly supersedes any wording in F2-SYS-006/007/009 that might imply ordinary script timers survive map departure. Research availability is not implementation acceptance.

## Current measured evidence — 2026-10-10

- [Installation inspection](INSTALLATION_INSPECTION_2026-10-10.md) and [master/full MAP structural audit](MASTER_RECOVERY_AND_MAP_AUDIT_2026-10-10.md) record private input identities and reader bounds.
- [CE executable lab](CE_EXECUTABLE_LAB_2026-10-10.md) records pinned Linux startup; it does not execute the original Windows installation.
- [Navigation](CE_NAVIGATION_2026-10-10.md): 21 requests, six directions/returns, occupied-destination approach and bypass, 53 native tile observations. A2-01/A2-02 remain REFERENCE_PARTIAL.
- [Redirection](CE_REDIRECTION_2026-10-10.md): five scenarios, 429 poses, last target wins, repeated destination selects run, Escape pauses via options/resumes, current-tile click stops. Frame/offset resets differ from C's proposed continuous-next-node policy; A2-03 remains REFERENCE_PARTIAL.
- Native raw object IDs can repeat: wall and guard ID 47 in this measured map. Earlier identity principles below do not establish globally unique native object IDs.
- [A2 cases](A2_ACCEPTANCE_CASES_01.json) keep nine other cases unexecuted and all Vampiro acceptance unverified. Current priority comes from the master and [assimilation plan](ASSIMILATION_PLAN_01.md), not the historical inspection list at the end of this file.
- 25 reader/evidence tests and source-hash guards validate the published evidence. They do not rerun CE or choose an engine.

## Evidence policy

- Primary behavioral target: Fallout 2 as shipped.
- Engineering inspection source for this pass: public `alexbatalov/fallout2-ce` reimplementation, default branch inspected 2026-10-08.
- Findings below describe observed architecture/behavior in that implementation unless separately verified in the original executable/data.
- Do not copy proprietary Fallout assets, scripts, dialogue, maps, or content into this repository.
- A useful implementation pattern is not automatically a project architecture decision.

---

## Cluster 01 — Scripting / World State / Time / Persistence

### F2-SYS-001 — Engine events dispatch to script procedures

**Original function / observed behavior**

The engine exposes a finite script callback surface. Script procedure kinds include start, spatial trigger, description/look, pickup/drop/use, talk, critter update, combat/damage, map enter/exit/update, create/destroy, timed event, push, and combat boundary callbacks. Engine subsystems call the relevant procedure when the corresponding world action occurs.

Examples verified in `fallout2-ce`:

- dialogue entry dispatches the speaker's TALK procedure;
- inventory pickup dispatches PICKUP;
- combat can dispatch COMBAT and DAMAGE;
- object destruction dispatches DESTROY;
- map lifecycle dispatches MAP_ENTER / MAP_UPDATE / MAP_EXIT;
- spatial scripts fire from tile/radius checks;
- timed script events dispatch the TIMED procedure.

**Data/state involved**

A script instance carries a stable script ID, type, owner ID, local-variable range, current source/target objects, fixed parameter, current action, override state, and procedure lookup table.

**Strengths**

- Local content logic can react to a compact world-event vocabulary.
- The engine owns physical/system execution while scripts own contextual behavior.
- Interactions compose without requiring one giant quest manager.
- The same callback model serves critters, items, maps, spatial triggers and timed behavior.

**Limitations**

- Callback semantics are strongly coupled to the original engine and script VM.
- Generic integer parameters and implicit conventions can hide meaning.
- The original model does not distinguish objective event, observation, belief, memory and evidence at the granularity required by VampiroCRPG.

**General design principle**

Use explicit world/system events as the boundary between deterministic simulation and authored contextual reactions.

**Disposition**: KEEP principle / REPLACE implementation.

**Candidate equivalent in VampiroCRPG**

Typed simulation events with stable IDs and explicit payloads. Content handlers may react to events, but knowledge-sensitive reactions require an explicit information path. The M2 causal chain must preserve `WORLD_EVENT != OBSERVATION != BELIEF`.

**Validation**

Headless test: one supernatural world event must create reactions only for actors/sensors that receive a valid observation or later transmission.

---

### F2-SYS-002 — Script request boundary separates intent from engine execution

**Original function / observed behavior**

Scripts can request engine-level actions such as combat, dialogue, map transitions, explosions, looting and stealing. A central request handler later delegates execution to the relevant engine subsystem.

**Strengths**

- Authored scripts do not need to implement engine operations directly.
- The engine remains authoritative for subsystem transitions.
- Requests create a useful command boundary between content logic and simulation machinery.

**Limitations**

- The original request surface is a compact bitfield/global request structure and is not suitable as a scalable typed command system.
- Some requests are highly specific to Fallout 2 UI/gameplay flows.

**General design principle**

Authored logic should request actions; authoritative systems should validate and execute them.

**Disposition**: KEEP principle / MODIFY representation.

**Candidate equivalent in VampiroCRPG**

Typed command/request objects such as `StartDialogue`, `AttemptFeed`, `AlterEvidence`, `StartInvestigation`, `TransferRecord`, `Travel`, `BeginCombat`, with explicit initiator, target, context and validation result.

**Validation**

A content handler cannot directly mutate protected simulation state when an authoritative subsystem owns that state.

---

### F2-SYS-003 — Three practical variable scopes: script-local, map, game-global

**Original function / observed behavior**

The script interpreter exposes distinct local, map and global variable accessors. Script-local values are associated with a script instance through an offset/count into map-local storage. Map variables are accessed through map-level storage. Game-global variables live in a game-wide array and are independently persisted.

**Strengths**

- State lifetime/scope is explicit enough for a large authored CRPG.
- Local reactions need not consume global quest variables.
- Map-specific state can persist independently of unrelated locations.

**Limitations**

- Values are essentially anonymous indexed slots whose meaning lives outside the storage mechanism.
- Integer/global flag usage can become a hidden coupling network.
- Scope is storage-oriented rather than ontology-oriented.

**General design principle**

State should have explicit ownership and lifetime; not every change belongs in global state.

**Disposition**: KEEP scoping principle / REPLACE raw variable model.

**Candidate equivalent in VampiroCRPG**

Stable-ID typed records with explicit scopes such as actor, relationship, location, institution, process and world. Avoid a universal `global_flags[]` as the primary causal model.

**Validation**

A witness's memory remains owned by that actor; a police record remains owned/custodied by the institution; a local camera state remains location/device state; none becomes globally known merely because it is persistent.

---

### F2-SYS-004 — Quest presentation is derived from global state thresholds

**Original function / observed behavior**

The Pip-Boy quest list loads quest descriptors containing a location, description, referenced global variable, display threshold and completion threshold. Whether a quest appears and whether it is shown as completed are derived from the value of that referenced game-global variable.

**Strengths**

- Very cheap and deterministic quest-journal derivation.
- UI is downstream of world-state values rather than an entirely separate manual journal state.

**Limitations**

- A single scalar/global variable can become the de facto authoritative quest stage.
- It encourages authored progression to collapse multiple causes into a stage number.
- It cannot represent contested knowledge, independent witnesses, evidence provenance or parallel institutional processes without proliferating flags.

**General design principle**

UI should derive from simulation state where possible; the simulation should not exist merely to feed UI quest stages.

**Disposition**: KEEP derived-UI principle / REMOVE scalar quest-stage authority as the default.

**Candidate equivalent in VampiroCRPG**

Journal/case UI derives from propositions the player knows, active obligations/processes, discovered records and explicit objectives. A convenience quest-state field may exist for authored content only when it is genuinely the state being modeled, not as a substitute for causality.

**Validation**

`La Noche que Recuerda` must progress with no `QUEST_STAGE` variable. The player-facing journal may change only after the player obtains a valid information path.

---

### F2-SYS-005 — Per-NPC reaction is stored locally, but as a scalar

**Original function / observed behavior**

The reaction subsystem reads and writes an NPC reaction value through that critter script's local variable 0 and translates ranges into broad reaction categories.

**Strengths**

- Reaction is actor-local rather than purely global reputation.
- Dialogue/content can preserve individual history cheaply.

**Limitations**

- A single number conflates qualitatively different relationships.
- Fear, trust, gratitude, obligation, hostility and ideological alignment cannot coexist independently.
- The storage convention (`local var 0`) is implicit and brittle.

**General design principle**

Individual actors need persistent relationship state, but it should be multidimensional where the fiction requires it.

**Disposition**: MODIFY heavily.

**Candidate equivalent in VampiroCRPG**

Typed relationship edges with independent dimensions such as trust, fear, hostility, obligation, loyalty/affiliation and information-sharing willingness. Avoid reducing NPC social state to one approval score.

**Validation**

An NPC can simultaneously fear the player, owe the player a boon, distrust the player and still cooperate for self-interest.

---

### F2-SYS-006 — First-class sorted simulation-time event queue

**Original function / observed behavior**

Fallout 2 maintains an ordered event queue. Each queued item stores execution time, event type, optional owner object and event-specific data. New events are scheduled at current game time plus delay and inserted in temporal order. Event types have dedicated handlers and optional read/write/free functions.

Verified event families include script timers, game-time updates, poison/radiation, explosions, item behavior and map updates.

**Strengths**

- Delayed causality is a first-class runtime concept.
- Different systems share one temporal scheduling mechanism.
- Event-specific payload serialization supports persistent delayed effects.
- Simulation time, not wall-clock time, drives execution.

**Limitations**

- The event vocabulary and payloads are engine-specific.
- Owner-object coupling is too narrow for institution/process-centric delayed causality.
- The queue itself does not explain higher-level causal provenance.

**General design principle**

Persisted simulation-time scheduling is foundational for a world that changes while the player is elsewhere.

**Disposition**: KEEP strongly / REIMPLEMENT typed.

**Candidate equivalent in VampiroCRPG**

Deterministic scheduled-event service with stable event IDs, execution time, target/owner references, typed payload, parent-cause references and cancellation/supersession semantics.

**Validation**

Schedule W1's later testimony, G1's daytime cleanup and I1's follow-up; save before execution; reload; assert identical ordered outcomes for the same seed and inputs.

---

### F2-SYS-007 — Script timers bridge authored logic into the persistent queue

**Original function / observed behavior**

A script can schedule a timed event with its script ID, delay and fixed parameter. The event is stored in the general event queue. When fired, the script receives the parameter and its TIMED procedure executes. Script-event payloads have explicit save/load functions.

**Strengths**

- Authored content can express delayed behavior without polling every frame.
- Timers survive the same persistence machinery as other world events.
- The callback is associated with a stable script identity rather than a transient stack frame.

**Limitations**

- A single integer parameter has weak semantics.
- Timer ownership is script/object-centric, not process-centric.

**General design principle**

Delayed authored consequences should be scheduled, persisted and event-driven rather than represented by ad hoc elapsed-time checks scattered through content.

**Disposition**: KEEP principle / MODIFY data model.

**Candidate equivalent in VampiroCRPG**

Scheduled typed transitions attached to persistent processes or actors, with causal parent IDs. Example: `WitnessTransmissionOpportunity`, `CleanupAttempt`, `RecordReview`, `RumorPropagation`, `InstitutionEscalation`.

**Validation**

No per-frame quest polling is needed to advance the M2 witness chain.

---

### F2-SYS-008 — Map lifecycle and spatial triggers are authored event surfaces

**Original function / observed behavior**

Spatial scripts are evaluated against triggering object position and configured tile/radius, then receive a SPATIAL callback. Map lifecycle exposes enter, update and exit callbacks across relevant scripts.

**Strengths**

- Geography can trigger authored behavior without hard-coding map-specific logic into the engine.
- Map lifecycle gives content explicit synchronization points.

**Limitations**

- Radius/tile triggers are presentation/map centric and do not by themselves encode semantic location context, witness density, jurisdiction or surveillance.
- Map-update callbacks can tempt content toward periodic polling.

**General design principle**

Location transitions and spatial context should emit deterministic events into authored/systemic logic.

**Disposition**: KEEP event surface / MODIFY semantics.

**Candidate equivalent in VampiroCRPG**

Location/zone events augmented by semantic context: public/private, active schedule, jurisdiction, witness potential, access/security, surveillance availability and routes.

**Validation**

The same supernatural action at two different semantic locations can generate different observations/evidence without bespoke scene scripts.

---

### F2-SYS-009 — Map state serializes map variables and script-local backing state

**Original function / observed behavior**

Map serialization writes map header state and map-global/map-local variable arrays when present. Script-local variables are backed by map-local storage through each script's offset/count. Loading restores the corresponding map variable state.

**Strengths**

- Leaving a location need not reset its authored state.
- Script-instance state and map-level state can survive map transitions/save cycles.

**Limitations**

- Raw variable arrays have weak type/provenance semantics.
- State is strongly organized around loaded/saved maps, while VampiroCRPG requires cross-location institutions, messages and processes that may advance independently.

**General design principle**

Location state must be persistable independently of whether the location is currently loaded.

**Disposition**: KEEP persistence principle / REPLACE scope model.

**Candidate equivalent in VampiroCRPG**

Simulation records persist independently of presentation scene loading. Location is one ownership/context dimension, not the lifetime boundary for every process or actor.

**Validation**

W1 can leave L1, communicate elsewhere, and alter P1/I1 state while L1 is unloaded; later reloading L1 preserves its evidence/device/access state.

---

### F2-SYS-010 — Save/load is a coordinated multi-subsystem contract

**Original function / observed behavior**

The save system invokes an ordered set of subsystem save handlers and a mirrored load-handler list. Persisted systems include game globals, map state, player/critter state, skills, random state, perks, combat/AI, stats, items, traits, automap, world map, Pip-Boy, movies, party state, the timed-event queue and interface state.

The event queue itself is explicitly serialized and restored rather than reconstructed loosely after load.

**Strengths**

- Persistence responsibilities are explicit by subsystem.
- The save format covers both current values and future scheduled causality.
- Random-state persistence is compatible with deterministic continuation.

**Limitations**

- Order-coupled handler arrays and original binary-format assumptions are not a model to copy literally.
- VampiroCRPG needs schema versioning, stable semantic IDs and migration strategy from the beginning.

**General design principle**

Save/load is an architectural contract across state-owning systems, not a late serialization feature.

**Disposition**: KEEP strongly / REIMPLEMENT with versioned schemas.

**Candidate equivalent in VampiroCRPG**

Versioned save snapshot that explicitly persists actors, personas, propositions/beliefs/memories, evidence/records, relationships, institutions, processes, scheduled events, deterministic RNG state and causal parent references. Scene/UI state remains separate from simulation truth where possible.

**Validation**

Uninterrupted M2 run and save/reload M2 run must converge to identical state hashes and causal logs for equal inputs/seed.

---

## Cross-corpus convergence with VTM Pass 5

The first strong engineering convergence is now visible:

**Fallout 2 provides a proven CRPG pattern for:**

`engine event -> contextual script callback -> scoped state mutation -> scheduled delayed event -> persistent save/load -> later callback/consequence`

**VTM requires that pattern to be expanded into:**

`world event -> observation -> proposition -> actor belief/memory -> evidence/record -> transmission -> relationship/process/institution change -> scheduled consequence -> new world event`

The important conclusion is therefore not to copy Fallout 2 globals or scripts. It is to preserve its compositional/event-driven/persistent strengths while replacing opaque scalar state with explicit causal records.

### Current project rule candidate

`KEEP Fallout 2's event-driven content boundary, state lifetime discipline, deterministic simulation time and persisted delayed queue.`

`REPLACE anonymous global/local quest variables as the primary world model with typed, stable-ID, provenance-bearing simulation records.`

`REPLACE scalar NPC reaction as the social model with multidimensional relationships.`

`KEEP derived UI/journal behavior, but derive it from player-known propositions/processes rather than authoritative quest-stage integers.`

This remains a research conclusion until promoted through project architecture review.

---

## Next Fallout 2 inspection targets

1. Dialogue option construction and how script conditions/state changes compose with TALK procedures.
2. Exact map-save lifecycle across leaving/re-entering locations and save slots.
3. Global variable conventions used by quests/reputation and how much causality is encoded as stage numbers versus independent facts.
4. Time advancement/rest/world-map transitions and when queued events are processed.
5. Object IDs/script IDs and restoration across map/save boundaries.
6. Script override semantics and engine-default suppression.
7. World-map/local-map persistence boundary.
8. NPC scheduling/AI state that survives map unloads, if any.

The next matrix gate is reached when scripting, dialogue, time, world state and save/load are understood well enough to cross-check the M2 technical contract without guessing about Fallout 2 behavior.

