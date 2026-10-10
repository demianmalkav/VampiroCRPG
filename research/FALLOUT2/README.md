# Asimilación vigente — A1 definido, A2 parcialmente observado en CE

**Vigente 2026-10-10:** [redirección/repetición/parada CE medidas](CE_REDIRECTION_2026-10-10.md), [poses y fronteras](CE_REDIRECTION_2026-10-10.json). Cinco escenarios completados: destino nuevo/último gana; repetir activa carrera; Escape pausa con opciones y retoma; solicitar tile actual detiene. Se mide reinicio de frame/offset al cambiar rumbo dentro de un tile, distinto de la continuidad propuesta para C. 429 instantáneas nativas, 25 tests PASS y DAT conservados. A2-03 parcial: 150ms/reloj y cancelación de interacción pendientes. Todo Vampiro sin verificar; no motor elegido ni arte/reglas integrados.

[Geometría/bloqueo previos](CE_NAVIGATION_2026-10-10.md): 21 solicitudes seleccionadas correctamente, seis vecinos/regresos, acercamiento y rodeo; bloqueo auxiliar del armario e IDs no únicos. A2-01/A2-02 parciales: tiempos, contenedor accesible/perímetros y huellas amplias abiertos. Nueve otros casos sin ejecutar. **NEXT:** puerta/acceso alcanzable mediante UI normal, medir frame/flags/bloqueador/pasabilidad/cruce; una prueba de contenedor accesible si lo permite. No repetir waypoints fallidos ni cerrar A2-05 con sólo abrir. Después visor/contacto/efectos/persistencia.

[Arranque previo CE](CE_EXECUTABLE_LAB_2026-10-10.md), [recuperación/auditoría del master](MASTER_RECOVERY_AND_MAP_AUDIT_2026-10-10.md): cerrados, no repetir preparación ni encuesta. Laboratorio Linux DAT-only silencioso, sin overrides/DLLs Windows; original sin ejecutar. Campaña individual de Nueva York y online posterior autorizados. [Contrato A1](../../docs/FALLOUT_ASSIMILATION_A1_SPATIAL_CONTRACT.md) · [adaptación de motor/reglas](../../docs/VAMPIRO_ENGINE_ADAPTATION_SINGLEPLAYER_01.md) · [tres fallas C aún abiertas](A1_BASELINE_AUDIT_2026-10-09.json) · [12 casos y cobertura](A2_ACCEPTANCE_CASES_01.json). Muestra 02 sigue rechazada.

# Fallout 2 System Analysis

Purpose: study Fallout 2 as a design and engineering corpus, and evaluate practical reuse alongside independent implementation. Preserve VampiroCRPG's own visual identity and rules. Engine adaptation is now an open candidate to compare, not a rejected or accepted architecture decision.

## Current priority — 2026-10-09 Argentina

Direction rejected the art and world consistency of playable sample 02 and requested a thorough reverse-engineering survey before assimilation. Research now covers 18 pinned repositories and 75 retrieved resources; targeted inspection is distinct from full reading and runtime verification. No upstream code/content was incorporated and no production engine was selected.

Read in this order:

1. [Research survey](RESEARCH_SURVEY_2026-10-09.md) — source availability, variants, formats, tools, rights and limits.
2. [Spatial/art/animation findings](SPATIAL_ART_ANIMATION_FINDINGS_01.md) — source-backed findings tied to the failed sample and direction's requirements.
3. [Assimilation plan](ASSIMILATION_PLAN_01.md) — bounded A1–A5 gates; A1 contract defined, current NEXT is A2.
4. [Pinned inventory](SOURCE_INVENTORY_2026-10-09.json) — exact source revisions and file blob identities; retrieval is not whole-corpus assimilation.

## Current research documents

Read these before making architecture claims from the Fallout 2 corpus:

- `SYSTEM_MATRIX.md` — promoted subsystem findings and KEEP / MODIFY / REPLACE dispositions.
- `DIALOGUE_TIME_PERSISTENCE.md` — targeted analysis for dialogue, simulation time, location persistence and M2 relevance.
- `QUEUE_LIFETIME_CORRECTION.md` — mandatory correction: the global event queue is save-persistent, but map departure deliberately clears/resolves some map-bound event types, including ordinary script timers in the inspected implementation. Do not claim that every queued timer survives leaving a map.
- `TACTICAL_ACTION_ECONOMY.md` — targeted source pass for combat rounds, AP budgeting, movement/action costs, tactical AI use, combat-time advancement and save/load behavior. Its findings are engineering evidence for later VTM reconciliation, not architecture decisions.

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

Behavioral understanding is mandatory whether we adapt an existing engine or build an independent implementation. Direct reuse requires exact licensing/compatibility review and an executable comparison; this research update does not authorize transplantation or select a production motor. Historical dispositions below remain mechanism-level findings and may be revisited only with concrete evidence.
