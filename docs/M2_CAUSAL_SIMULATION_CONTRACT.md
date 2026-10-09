# M2 Causal Simulation Contract — La Noche que Recuerda

Status: DRAFT FOR ARCHITECTURE REVIEW
Phase: M0.2 → M2 specification bridge

This document is an engine-agnostic technical contract for the first systemic proof, **La Noche que Recuerda**. It reconciles the VTM Pass 5 causal requirements with verified Fallout 2 engineering patterns without copying Fallout 2's concrete implementation.

No Godot node tree, database, ECS, serialization technology, or scripting language is selected here.

## 1. Contract objective

Prove deterministically that:

`world event -> observation -> proposition -> belief/memory -> evidence/record -> transmission -> relationship/process/institution change -> delayed consequence -> new world event`

can occur persistently, partly offscreen, survive save/load, and later be discovered by the player through explicit causal provenance.

The proof fails if it requires:

- faction-global omniscience;
- one authoritative quest-stage variable;
- deleting history when evidence is removed;
- scene loading as the lifetime of world causality;
- runtime LLM reasoning;
- hidden nondeterministic wall-clock behavior.

---

## 2. Cross-corpus disposition

### KEEP from the Fallout 2 reference pattern

- finite event/callback surfaces between engine systems and authored/contextual logic;
- command/request boundary: authored logic requests, authoritative systems execute;
- explicit state ownership/lifetime rather than putting every fact in one global scope;
- deterministic simulation time;
- ordered scheduled events;
- save/load as a coordinated multi-subsystem contract;
- serialized stable identities and explicit post-load reference restoration;
- persistent location state separate from loaded presentation state;
- dynamic dialogue built from current state with executable consequences;
- controlled authored override points where the engine explicitly permits them.

### EXTEND beyond Fallout 2

- world/process-lifetime scheduled events that survive location unload;
- actor-specific observation, belief and memory state;
- evidence and documentary custody/provenance;
- institutions that know only what their actors/records transmit to them;
- multidimensional relationships;
- persistent processes such as investigations and cover-ups;
- causal ancestry/debug queries;
- persona/documentary identity separate from actor identity.

### REPLACE

- anonymous indexed integer arrays as the primary world ontology;
- scalar quest stage as the primary causal authority;
- scalar NPC reaction as the complete social model;
- implicit pointer/reference persistence;
- generic script override as an unrestricted escape hatch.

---

## 3. Stable identity contract

Every persistent simulation entity or record participating in causal chains MUST have a stable ID that survives save/load and presentation unload.

Minimum persistent ID families for M2:

- `ActorId`
- `PersonaId`
- `LocationId`
- `InstitutionId`
- `WorldEventId`
- `ObservationId`
- `PropositionId`
- `BeliefId`
- `MemoryId`
- `EvidenceId`
- `RecordId`
- `RelationshipId`
- `MessageId`
- `ProcessId`
- `ScheduledEventId`

Requirements:

1. Serialized data stores IDs, never raw runtime pointers as authority.
2. Runtime references are reconstructed from IDs after load.
3. Missing targets are validation errors with defined handling; they must not silently retarget.
4. IDs are not reused during the lifetime of a save lineage unless an explicit migration strategy guarantees safety.
5. Presentation-scene object identity may be ephemeral; it maps to persistent simulation IDs rather than replacing them.

---

## 4. Authoritative state ownership

M2 state is divided by semantic ownership, not merely storage convenience.

### World-owned

- simulation clock;
- deterministic RNG state/streams;
- world events;
- propositions whose objective status is known by the simulation;
- world/process scheduler;
- stable-ID registry/version data.

### Actor-owned

- current persistent location reference;
- active persona(s);
- observations made by that actor;
- memories;
- belief states;
- motives relevant to M2;
- relationship edges;
- memberships/roles needed for M2.

### Location-owned

- semantic context;
- persistent devices/sensors;
- persistent evidence physically present there;
- local access/security state;
- local presentation-independent state.

### Institution-owned

- records in custody;
- institution-level propositions/beliefs only when produced by an explicit procedure or authorized aggregation;
- active cases/processes;
- relevant members/roles/resources.

### Process-owned

- objective;
- participants/owner;
- phase;
- accumulated evidence/claims/resources;
- deadlines/windows;
- scheduled transitions;
- success/failure/cancellation state.

No store may become a shortcut for omniscience.

---

## 5. Event envelope contract

Every state-changing simulation event MUST have a common envelope conceptually containing:

- `event_id`
- `event_type`
- `simulation_time`
- `initiator_id` or system source
- zero or more target IDs
- `location_id` when spatially relevant
- typed payload
- zero or more causal parent IDs
- deterministic ordering key
- optional process ID
- optional source command ID if commands are tracked separately

The event is the authoritative fact that the state transition occurred.

An event does **not** automatically grant knowledge of itself to any actor.

---

## 6. Command / execution boundary

Systems and authored content interact through a request/command boundary inspired by Fallout 2's script-request pattern.

A command expresses intent, for example:

- `PerformSupernaturalAction`
- `SendMessage`
- `CreateRecord`
- `AlterEvidence`
- `StartInvestigation`
- `TransferEvidence`
- `ThreatenActor`
- `AttemptCleanup`
- `ChangeLocation`

A command MUST be validated by the subsystem that owns the protected state.

The result is either:

- rejection/no state change with a reason; or
- one or more authoritative world events.

Content logic MUST NOT directly edit protected state when a system owns the invariant.

---

## 7. Observation contract

A `WorldEvent` may produce zero or more observations.

Observation creation depends on explicit channels such as:

- direct human perception;
- camera/sensor capture;
- later inspection of evidence;
- access to a record;
- supernatural perception if/when implemented.

An observation stores only perceived features plus uncertainty/context. It must not copy inaccessible objective event fields.

Required M2 distinction:

`WorldEvent != Observation`

Two observers of the same event may produce conflicting observations without corrupting objective event state.

---

## 8. Proposition and belief contract

A `Proposition` is a claim that actors or institutions may believe, reject, doubt or leave unresolved.

Minimum simulation-level objective status:

- `True`
- `False`
- `Unknown`
- `ScenarioDependent` reserved for later/content-level use if necessary

A `BeliefState` belongs to a holder and references a proposition.

Minimum belief dimensions for M2:

- holder ID;
- proposition ID;
- confidence;
- provenance source ID/type;
- acquired/updated time;
- optional interpretation/frame;
- secrecy/disclosure constraint if relevant;
- supporting/opposing observation/evidence/record/message references.

Required distinction:

`Proposition objective status != holder belief confidence`

The simulation may know something is true while every actor believes otherwise.

---

## 9. Memory contract

A memory is persistent actor state derived from direct observation, interaction, message, record access or inference.

Minimum fields:

- memory ID;
- owner actor ID;
- provenance type;
- source IDs;
- referenced propositions;
- confidence;
- simulation timestamp;
- emotional salience needed for M2, at minimum fear relevance if used;
- secrecy/disclosure state if relevant.

Memory decay/distortion algorithms are NOT frozen in M2. Rumor transformation is sufficient to test information mutation.

Memory removal is not allowed as a side effect of deleting external evidence.

---

## 10. Evidence and record contract

### Evidence

Evidence is a trace that exists independently of what actors believe it proves.

Minimum fields:

- evidence ID;
- evidence type;
- origin event IDs if known by simulation;
- current custody/location;
- integrity/condition;
- access/visibility;
- copy relationships if applicable.

### Record

A record is a durable information carrier created by an actor/device/institution.

Minimum fields:

- record ID;
- creator/source;
- creation time;
- stored propositions/claims and/or evidence references;
- custody/storage institution/location;
- access policy;
- integrity/authenticity state;
- copy/derivation links.

Required distinctions:

`Evidence != Interpretation`

`Record contents != Objective truth`

Removing one evidence item MUST NOT erase copies, memories or records already derived from it.

---

## 11. Relationship contract

Relationships are multidimensional state, not one approval score.

M2 minimum dimensions where used:

- trust;
- fear;
- hostility;
- obligation/debt;
- loyalty/affiliation;
- willingness to share information.

The representation may use normalized numbers, bands, typed values or another deterministic form later. The exact scale is NOT frozen.

Invariant:

An actor may simultaneously fear, distrust, owe and cooperate with another actor.

A relationship state is distinct from a proposition about that relationship. Actors may dispute whether a debt, right or obligation exists.

---

## 12. Institution contract

An institution is persistent collective state with members, records, processes and procedures.

An institution MUST NOT automatically know everything any member knows.

Institutional knowledge can be created only through explicit mechanisms such as:

- record submission;
- briefing/report;
- database/file access;
- case assignment;
- defined aggregation procedure.

Minimum M2 institution behavior:

1. receive a record or evidence through a valid path;
2. evaluate configured threshold/procedure;
3. start or advance an investigation process;
4. assign an actor such as I1;
5. preserve the record across time/save/load.

---

## 13. Process contract

M2 processes represent multi-event causal activities that persist beyond one scene.

Required process types for the proof:

- `InvestigationProcess`
- `CleanupProcess`

Optional:

- `RumorPropagationProcess`
- `InstitutionReviewProcess`

Minimum process fields:

- process ID;
- type;
- owner/participants;
- objective;
- phase/state;
- relevant propositions/evidence/records;
- deadlines/windows;
- scheduled event IDs;
- secrecy if relevant;
- causal parent IDs or initiating event IDs.

A process may continue while none of its actors are present in the player's loaded scene.

---

## 14. Scheduler contract

The scheduler is one of the most important explicit extensions beyond Fallout 2's map-bound timer behavior.

Every scheduled event MUST declare a lifetime/scope.

Minimum scopes:

### `LocationLifetime`

May be cancelled/resolved/transformed when the owning location presentation/simulation slice unloads, if its semantics are truly local.

Examples: local ambient/presentation callbacks, some scene-local object behavior.

### `WorldProcessLifetime`

Survives location unload and full travel. Ends only when fired or causally cancelled/superseded.

Examples:

- W1's opportunity to contact W2;
- G1 daylight cleanup;
- a record review deadline;
- I1 follow-up;
- rumor/institution escalation.

Required scheduler fields:

- scheduled event ID;
- due simulation time or explicit trigger condition;
- event type/payload;
- scope/lifetime;
- owner/target persistent IDs;
- parent cause/process IDs;
- deterministic ordering key;
- cancellation/supersession state.

Required semantics:

1. Simulation time, not real time, is authoritative.
2. Equal-time ordering is deterministic and documented.
3. Save/load restores future events exactly.
4. Location unload MUST NOT cancel `WorldProcessLifetime` events.
5. Cancellation requires an explicit cause.
6. Same-tick self-scheduling must have loop protection.

---

## 15. Location / presentation boundary

Persistent simulation location state is distinct from a loaded Godot scene or future presentation object.

For M2:

- L1 may unload from presentation memory;
- its persistent camera/evidence/access state remains;
- W1 can move elsewhere;
- G1 can later interact with L1 through simulation or a newly loaded presentation;
- P1/I1 processes can advance elsewhere;
- re-entering L1 reconstructs presentation from persistent state.

Required rule:

`Scene unloaded` is not a semantic event equivalent to `world ceased to exist`.

---

## 16. Persona / identity contract

Actor identity and recognized persona are distinct.

Minimum fields:

- persona ID;
- owning actor ID;
- alias/name;
- documentary footprint/reference set needed for M2;
- known-to actor/institution relations or derivable knowledge;
- compromise state per observer/institution, not necessarily one global boolean.

I1 may link an anomalous event to a persona without learning that persona's full vampiric identity.

---

## 17. Determinism contract

For the M2 headless proof:

`same initial state + same seed + same ordered external/player inputs => same ordered causal log + same final state`

Required measures:

- deterministic simulation clock;
- persisted RNG state or named deterministic RNG streams;
- stable event ordering;
- no wall-clock calls in simulation outcomes;
- no iteration-order dependence on unordered runtime containers unless normalized;
- deterministic serialization/state hash for test checkpoints.

---

## 18. Save/load contract

A save after the incident but before later transmission MUST preserve enough state to resume the exact causal chain.

Minimum persistent categories:

- schema/save version;
- simulation time;
- RNG state/streams;
- stable ID allocator/registry state;
- actors and persistent location references;
- personas;
- world events needed by causal history;
- observations;
- propositions;
- beliefs;
- memories;
- evidence and custody/integrity;
- records and copies/access;
- relationships;
- institutions;
- processes;
- scheduled world/process events;
- messages already sent/received;
- causal parent links needed for debugging/explanation.

Post-load phase MUST:

1. reconstruct records by stable ID;
2. rebuild runtime references/indexes;
3. validate referential integrity;
4. restore scheduler ordering;
5. restore deterministic RNG state;
6. fail loudly or quarantine invalid records rather than silently changing causal targets.

---

## 19. Causal log/debug contract

Every state-changing event in M2 MUST produce a compact deterministic log entry or equivalent inspectable history.

Minimum fields:

- event ID;
- simulation time;
- type;
- source/initiator;
- targets;
- affected persistent IDs;
- parent-cause IDs;
- process ID if any;
- deterministic result/state-delta reference.

The debug layer MUST eventually answer:

- Who knows proposition P?
- Why does that holder believe it?
- Who directly observed EVT-001?
- Who only heard about it?
- Which evidence still exists?
- Who can access each record/evidence item?
- Why did an investigation start?
- What did cleanup alter?
- Which later events descend from EVT-001?
- Which persona is compromised to which observer/institution and why?

---

## 20. M2 deterministic scenario contract

Required actors/objects:

- V0 player vampire;
- W1 direct mortal witness;
- W2 hearsay recipient;
- G1 cleanup/daylight proxy;
- I1 investigator;
- P1 mortal institution;
- optional H1 Kindred social receiver;
- L1 incident location;
- optional C1 camera/sensor;
- E1 evidence;
- R1 institutional record;
- investigation process;
- cleanup process.

Required sequence:

1. V0 performs overt supernatural action -> world event.
2. W1 receives a direct observation.
3. W1 forms proposition/belief/memory.
4. Optional C1/E1 creates independent evidence path.
5. V0 may leave/intervene/request cleanup.
6. Location may unload; world/process causal events survive.
7. W1 later transmits a possibly transformed claim to W2.
8. W2 may create R1 through its own decision/rules.
9. P1 receives R1 through explicit procedure.
10. I1 gains access and investigation advances.
11. Optional H1 learns a separate distorted/social version through another path.
12. Player later discovers that the world changed while absent.

No step may read inaccessible global truth to manufacture knowledge.

---

## 21. Acceptance tests

### AT-01 No hidden information leak

Only W1/C1 may know/capture the incident immediately unless another explicit channel exists.

### AT-02 Direct observation differs from hearsay

W1 and W2 can hold related propositions with different provenance/confidence.

### AT-03 Rumor mutation

A deterministic transmission rule can alter detail, certainty, attribution or interpretation while preserving ancestry.

### AT-04 Evidence custody

Evidence can move, be altered or be removed without deleting source events or memories.

### AT-05 Institution requires an information path

P1 cannot start an investigation from telepathic/global knowledge.

### AT-06 Daylight/proxy causality

G1 can act while V0 lacks direct agency and can create new traces.

### AT-07 Save/load equivalence

Uninterrupted run and save/reload run converge to the same state/log for identical inputs/seed.

### AT-08 Causal ancestry query

I1's suspicion can be traced back through record/message/memory/observation/event ancestry.

### AT-09 Branch sensitivity

Silencing W1, removing E1, disabling C1 or preventing W2's report produces causally different downstream states.

### AT-10 No institution-global memory

One member learning something privately does not grant it to all institution members.

### AT-11 Deterministic replay

Replay of the same seed/input log reproduces state hashes/checkpoints.

### AT-12 Cover-up can create traces

Cleanup may generate access logs, witnesses or contradictions that increase suspicion.

### AT-13 Player knowledge is separate

The player does not automatically see W1/W2/I1 internal beliefs.

### AT-14 Persona linkage is partial

I1 may link evidence to a persona without resolving V0's full supernatural identity.

### AT-15 Relationship consequence is systemic

Fear/trust/etc. change because of observed interactions, not because a quest stage changed.

### AT-16 Scheduler lifetime

Unload L1 after W1 forms a memory but before a scheduled world-process testimony event. The testimony event remains scheduled and can fire later unless explicitly cancelled by a causal event.

### AT-17 Scene-local event cleanup

A deliberately `LocationLifetime` test event may be discarded on L1 unload without altering persistent social causality.

### AT-18 Reference restoration

Save/load restores every persistent ID reference and scheduled target. Any unresolved reference fails validation deterministically.

---

## 22. Explicit non-goals for this contract

Not selected or implemented here:

- Godot node/resource hierarchy;
- ECS vs object model;
- SQL/JSON/binary save format;
- networking;
- full dialogue authoring format;
- full police AI;
- full city simulation;
- full VTM character sheet;
- Disciplines/combat implementation;
- sophisticated memory decay;
- final reputation/Status systems;
- UI/art presentation;
- LLM runtime NPC reasoning.

---

## 23. Architecture review gate

This contract is ready to move from research to architecture only if direction accepts the following non-trivial commitments:

1. Knowledge is actor/institution-specific and provenance-bearing.
2. World/process scheduling survives location unload.
3. Persistent IDs are semantic and versioned; runtime pointers are reconstructible only.
4. Save/load preserves future causality, not just current snapshots.
5. Quest-stage variables cannot substitute for causal state in M2.
6. Relationships are not one scalar.
7. Loaded presentation scenes are not the lifetime boundary of the simulated world.
8. Headless deterministic tests are mandatory before visual implementation of M2.

If accepted, the next artifact is an **M2 Data Contract** specifying record schemas/interfaces at field level while still remaining independent of Godot presentation.
