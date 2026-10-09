# Fallout 2 — Dialogue, Time and Map Persistence

Status: ACTIVE / targeted M0.2 pass

Scope: deepen the parts of Fallout 2 most relevant to the M2 proof `La Noche que Recuerda`: dialogue as authored reaction logic, simulation-time execution, location persistence and the boundary between loaded maps and persistent world state.

Engineering evidence in this pass comes from the public `alexbatalov/fallout2-ce` reimplementation. Findings are implementation observations unless separately verified behaviorally against Fallout 2 data/executable.

---

## 1. Dialogue is a script-driven interaction surface, not an isolated narrative database

### Verified structure

Entering dialogue with a scripted speaker dispatches that speaker's `TALK` script procedure. Dialogue reply/options are then assembled through script interpreter operations that call the dialogue subsystem.

An option can carry:

- localized message or direct text;
- a procedure identifier/callback to execute when selected;
- a reaction classification used by the dialogue presentation/reaction machinery.

When the player selects an option whose stored procedure is non-zero, the dialogue system executes that procedure in the dialogue script program.

The interpreter also exposes `giq_option`, which gates dialogue-option availability using player Intelligence plus the Smooth Talker perk. This confirms that at least some dialogue gating is authored through script/API composition rather than being a fixed dialogue-tree format with one universal condition system.

### Behavioral abstraction

The important reusable pattern is:

`TALK EVENT -> SCRIPT BUILDS CURRENT REPLY/OPTIONS FROM STATE -> PLAYER CHOOSES OPTION -> OPTION CALLBACK EXECUTES -> STATE/SYSTEM REQUESTS CHANGE -> NEXT DIALOGUE STATE`

This is more valuable to VampiroCRPG than copying the exact UI or opcode vocabulary.

### Strengths

- Dialogue conditions can inspect the same world/script state used by gameplay.
- Dialogue consequences are executable script behavior, not merely edges in a static text tree.
- Character stats/perks can alter available responses.
- The speaker owns contextual logic through its script.

### Limitations

- Conditions/consequences can be hidden imperatively inside scripts, making large narrative graphs harder to audit.
- The original state model often relies on integer vars/stages rather than explicit propositions, beliefs or relationship dimensions.
- A simple reaction value can conflate social meanings.
- Dialogue knowledge is not inherently protected from metagame/global-state access by the architecture itself; author discipline is required.

### VampiroCRPG disposition

KEEP the dynamic dialogue-as-state-query and option-as-action pattern.

MODIFY the authoring model so dialogue predicates and effects can query typed state:

- what this speaker knows/believes;
- provenance/confidence of that knowledge;
- relationship dimensions;
- active obligations/processes;
- player persona recognized by the speaker;
- evidence/records accessible to the speaker;
- current location/time/institution context.

A dialogue node must not become an omniscient portal into global truth.

### M2 requirement

W1, W2, I1 and H1 must be able to say different things about the same original supernatural event because they possess different observations/provenance. Dialogue should surface their own state, not resolve the objective event directly.

---

## 2. Dialogue option callbacks support consequence-oriented conversation design

The dialogue subsystem stores a procedure/callback with an option and invokes it on selection. That means a response can execute arbitrary authored consequence logic after the choice rather than only selecting another line.

### Reusable principle

A dialogue choice is an action request with narrative presentation, not merely text navigation.

### Candidate VampiroCRPG model

A dialogue option should contain or reference:

- availability predicate;
- player-visible text;
- speaker/player intent tags if useful;
- command/effect request(s);
- next conversational state;
- knowledge disclosure created by the exchange;
- relationship consequences;
- optional checks and their result branches.

Authoring should preferably remain declarative enough to audit, while complex consequences dispatch typed simulation commands/events.

### Validation

Selecting a line that threatens a witness should not directly set `WITNESS_SILENT = true`. It should create a threat/interaction event, update fear/trust/hostility, possibly create an obligation/coercion state, and let later communication behavior derive from those states.

---

## 3. Simulation time drives queued consequences

### Verified structure

Fallout 2's queue processes events whose scheduled time is less than or equal to current game time. Due events are removed in temporal order and dispatched to the event type's handler. A handler can stop the current processing pass.

Time-advancing systems explicitly process the queue after game-time movement. Verified call sites include Pip-Boy/rest-related time advancement, world-map time progression and script-driven time advancement.

### Behavioral abstraction

`ADVANCE SIMULATION TIME -> PROCESS ALL CURRENTLY DUE EVENTS IN ORDER -> HANDLERS MUTATE WORLD / SCHEDULE MORE WORK`

### Strengths

- Delayed consequences are tied to simulation time, not frame rate or real time.
- Rest/travel can cause the world to advance rather than merely teleporting the clock.
- Event processing is centralized and deterministic enough to serialize/replay with appropriate RNG-state handling.

### Limitations

- The original queue is designed around a relatively small fixed set of event types.
- It is not an explicit social-causality graph.
- Some handlers may stop processing, so exact ordering/interrupt semantics must be consciously specified in a new implementation.

### VampiroCRPG disposition

KEEP strongly.

The M2 scheduler should define:

- authoritative simulation timestamp;
- deterministic ordering for events sharing a timestamp;
- explicit cancellation/supersession rules;
- whether one event may schedule another for the current tick;
- bounded processing to avoid infinite same-time loops;
- stable parent-cause references;
- persisted RNG state where stochastic outcomes are allowed.

### M2 application

The following should be scheduled/process-driven rather than polled from a quest script:

- W1 gets a later opportunity to tell W2;
- G1 attempts cleanup during daylight;
- a record reaches I1 after institutional delay;
- H1 hears a rumor after a separate social delay;
- an investigation escalates after evidence correlation.

---

## 4. The queue is serialized as future causality

Fallout 2 does not save only current object variables. Its timed-event queue is explicitly included in the global save-handler contract. Queue entries persist scheduled time, event type, owner object identity and event-type-specific payload where applicable.

Script timer payloads likewise serialize their script ID and fixed parameter.

### Reusable principle

A save must preserve not only what the world is, but also what has already been scheduled to happen.

### VampiroCRPG disposition

KEEP strongly and extend.

A saved scheduled event should retain enough information to answer:

- what will happen;
- when;
- which persistent actors/processes it concerns;
- why it was scheduled;
- which event/process caused it;
- whether it is still valid after load;
- how deterministic ordering is restored.

For M2, saving between W1's observation and W1's later testimony must not erase the future testimony opportunity.

---

## 5. Leaving a saveable map persists a complete local simulation slice

### Verified map-save behavior

The in-game map save path performs substantially more than storing map variables.

For a saveable map, the map save routine records:

- map header/state, including last visit time;
- map-global variable array;
- map-local variable array backing script locals;
- tile/elevation data when present;
- all persistent scripts and their serializable state;
- all persistent map objects.

When performing an in-game map departure, the engine can run map-exit procedures, perform party/save preparation, update time-related scheduling, write the map as a `.SAV` map state, save automap state, then remove map objects/prototypes/reset map presentation state.

Random encounter maps can be treated differently and may be deliberately non-saveable.

### Strong conclusion

In Fallout 2, leaving a normal location is not equivalent to destroying its world state. The current local simulation is serialized so the location can later be reconstructed.

### Strengths

- Persistent environmental/object consequences survive leaving the map.
- Local script state and objects are co-saved coherently.
- Loaded-scene lifetime is distinct from persistent-location lifetime.

### Limitations

- Persistence is still heavily map-centric.
- Systems that conceptually span locations need separate global/world-map structures or global variables.
- A modern simulation with institutions, messages and processes should not require a map to be loaded to remain causally active.

### VampiroCRPG disposition

KEEP the loaded-scene vs persistent-state separation, but REPLACE map-as-primary-world-lifetime boundary.

`LocationState` should persist whether or not its scene is loaded. Cross-location actors/institutions/processes should live in simulation state above presentation scenes.

### M2 application

After V0 leaves L1:

- C1/E1 can remain at L1;
- W1 can travel elsewhere;
- G1 can later enter L1;
- P1/I1 can advance elsewhere;
- the investigation can continue while L1 is unloaded;
- re-entering L1 reconstructs relevant persistent local state without replaying the original incident.

---

## 6. Map exit is an explicit authored lifecycle event

The in-game map-departure path invokes map-exit script procedures before unloading a saveable map. Separately, map enter/update procedures are dispatched during map lifecycle.

### Reusable principle

Scene/location loading boundaries should emit semantic lifecycle events, but business causality should not depend on scene loading alone.

### Candidate VampiroCRPG distinction

Use two layers:

1. `PresentationSceneLoaded/Unloaded` — technical rendering/navigation lifecycle.
2. `ActorEnteredLocation/LeftLocation`, `LocationOpened/Closed`, `ScheduleWindowChanged` — simulation semantics.

Do not let Godot scene-tree presence determine whether an institution, memory or investigation exists.

---

## 7. Fallout 2 demonstrates useful persistence composition, not the final ontology

The public reimplementation shows a coherent composition:

`script callbacks + local/map/global state + persistent objects + simulation-time queue + map snapshots + coordinated save/load`

This architecture explains much of Fallout 2's ability to remember player actions cheaply across a large CRPG.

For VampiroCRPG the corresponding target is:

`typed events + actor-specific observations/beliefs/memories + evidence/records + multidimensional relationships + institutions/processes + persistent locations + deterministic scheduled transitions + versioned save contract`

The second model is deliberately richer because Vampire's Masquerade, misinformation, social debt, witnesses, occult secrecy and institutional investigation require distinctions Fallout 2 can often collapse into script variables.

---

## 8. Architecture implications promoted for review

These are research recommendations, not frozen implementation decisions:

1. KEEP a finite typed event surface between engine/simulation systems and authored content.
2. KEEP a request/command boundary so content asks authoritative systems to perform protected actions.
3. KEEP simulation-time scheduled events and persist them.
4. KEEP explicit state ownership/lifetime, but replace raw local/map/global arrays with typed stable-ID records.
5. KEEP loaded-location persistence, but allow cross-location processes to advance independently of loaded scenes.
6. KEEP dynamic dialogue generation from current state and option callbacks, but make information access actor-specific and auditable.
7. DO NOT inherit scalar NPC reaction as the complete relationship model.
8. DO NOT inherit a single global quest-stage integer as the complete causal model.
9. DO NOT make Godot scene lifecycle equivalent to simulation lifecycle.
10. Make save/load and deterministic time first-order architecture concerns before content production.

---

## Remaining targeted questions before M2 cross-corpus freeze

- Exact dialogue script patterns in representative Fallout 2 NPCs: how many independent vars/checks typically feed one conversation and how quest-stage-heavy authored practice actually is.
- Exact load path restoring saved `.SAV` maps, including object/script identity rebinding.
- Object ID and script ID stability semantics across map save/load.
- Script override behavior: how authored logic suppresses engine defaults and where that pattern is worth preserving.
- Global reputation/karma/local reputation structures versus per-NPC reaction.
- World-map encounter/time advancement interactions with persistent map states.
- Whether/how ordinary non-party NPC schedules advance while their maps are unloaded; do not assume a living offscreen world where Fallout 2 does not actually simulate one.

The last item is particularly important: VampiroCRPG intends a stronger offscreen causal simulation than Fallout 2. That should be a deliberate extension, not falsely attributed to the reference game.
