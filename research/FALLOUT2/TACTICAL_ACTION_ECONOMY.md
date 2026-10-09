# Fallout 2 Tactical Action Economy — Targeted Pass

Status: ACTIVE / TARGETED PASS

Purpose: document the combat-turn and action-budget behavior observed in the public `alexbatalov/fallout2-ce` reimplementation, then extract reusable engineering/design principles for later reconciliation with Vampire: The Masquerade Revised. This file is evidence, not an architecture decision and not a source-code transplant.

## Evidence boundary

- Primary behavioral target: Fallout 2.
- Engineering inspection source for this pass: `alexbatalov/fallout2-ce` at commit `e97087b9582f37075db347a89898887320753f8b`.
- Principal inspected files: `src/combat.cc`, `src/stat.cc`, `src/item.cc`, `src/inventory.cc`, `src/animation.cc`, `src/game_mouse.cc`, `src/combat_ai.cc`.
- Findings describe the inspected implementation unless separately verified against the original executable/data.
- A useful Fallout pattern is not automatically a VampiroCRPG design choice.

---

## F2-TAC-001 — Combat uses a finite per-actor Action Point budget

### Observed behavior

Each combatant has current combat AP stored on the critter combat state. At the start of a combat round, active combatants receive a fresh AP budget from `STAT_MAXIMUM_ACTION_POINTS`.

The default derived statistic is:

`Maximum Action Points = Agility / 2 + 5`

The final stat can be reduced by encumbrance and other Fallout-specific rules.

Actions such as movement, weapon attacks, reloading, inventory access and item use consume AP. The actor may end its turn with AP remaining.

### Strengths

- One finite resource makes turn planning legible.
- Movement and actions compete for the same tactical budget.
- Player and NPC action selection can reason about the same resource.
- Costs are visible enough for predictive UI.

### Limitations

- The SPECIAL-derived formula is Fallout-specific.
- Some cost modifiers are hard-coded around player-only perks.
- Additional player-only movement state exists separately from ordinary AP.

### General principle

A turn-based isometric CRPG benefits from an explicit finite action-opportunity budget that is shared by movement and other tactical actions.

### Disposition candidate

KEEP the finite per-actor budget principle. REPLACE the Fallout-specific stat formula and hard-coded modifier paths.

---

## F2-TAC-002 — Round boundaries replenish AP and advance simulation time

### Observed behavior

The combat loop executes actors sequentially. After all active actors have received a turn, the next round sequence is prepared, AP is refreshed, and the game clock advances by five seconds.

Thus tactical combat is not temporally detached from the world clock: a completed combat round represents elapsed simulation time.

### Strengths

- Combat consumes world time rather than existing in a timeless minigame.
- Delayed systems can remain conceptually connected to tactical play.
- Round boundaries are deterministic synchronization points.

### Limitations

- Five seconds is a Fallout-specific calibration.
- Other game systems may use different abstractions of time.

### General principle

Tactical rounds should advance authoritative simulation time through an explicit, deterministic conversion rather than pausing world causality indefinitely.

### Disposition candidate

KEEP the shared-time principle. RE-EVALUATE the exact seconds-per-round value against VTM action cadence, feeding timing, Celerity and the final tactical model.

---

## F2-TAC-003 — Turn order is deterministic and stat-driven after the opening round

### Observed behavior

Fallout 2 uses `STAT_SEQUENCE`, whose base derived value is:

`Sequence = 2 * Perception`

After the initial combat ordering, active combatants are sorted by Sequence descending. Ties are resolved by Luck descending.

The opening sequence contains additional behavior: the initiating attacker is forced first, the defender second, and the player may be positioned specially when neither is one of those actors.

### Strengths

- Deterministic order is easy to reason about and replay.
- A visible actor stat can drive tactical tempo.

### Limitations

- The opening-round exceptions are implementation/game-specific quirks.
- Sequence and Luck are SPECIAL-specific concepts.
- Static full-round ordering may or may not be ideal for VTM powers that alter speed or interrupt behavior.

### General principle

Actor order should be deterministic, inspectable and derived from explicit state, while combat-start exceptions should be semantic rather than ad hoc positional hacks.

### Disposition candidate

KEEP deterministic ordering. REPLACE the specific Sequence/Luck formula and first-round forced ordering unless later design deliberately adopts equivalents.

---

## F2-TAC-004 — Movement consumes AP incrementally along the path

### Observed behavior

Combat movement is evaluated against path length and movement-point cost. Each movement step consumes the applicable movement allowance/AP. If the available budget is exhausted, the actor stops rather than completing an unaffordable path.

The UI can preview movement cost before execution.

The player can also have `_combat_free_move`, derived from Bonus Move, which is consumed before ordinary AP.

### Strengths

- Route selection has direct tactical opportunity cost.
- Partial movement remains valid when a longer route becomes unaffordable.
- Previewable cost supports deliberate positioning.

### Limitations

- `_combat_free_move` is a global/player-specific implementation artifact.
- Movement cost rules are tied to Fallout critter state, crippled-leg handling and perks.

### General principle

Movement should consume action budget through a path-cost service that can be previewed and resolved incrementally.

### Disposition candidate

KEEP incremental path budgeting and preview. REPLACE player-global free movement with typed actor-specific modifiers/allowances if an analogous concept survives design.

---

## F2-TAC-005 — Attack modes have data/rule-derived AP costs

### Observed behavior

Weapon attack modes expose AP costs through weapon/item data and helper rules. Unarmed modes can have their own costs. Aimed attacks add an AP surcharge. Fallout-specific perks can reduce attack costs. Reloading has a defined AP cost with weapon/perk exceptions.

Before an attack, the game validates that enough AP remains. After execution, the corresponding cost is deducted.

### Strengths

- Different tactical actions can trade efficiency, precision and power.
- Cost is tied to the selected action/mode rather than a universal attack constant.
- Prevalidation makes the UI predictable.

### Limitations

- Many concrete costs and perk exceptions are Fallout-specific.
- Hit chance, critical and damage resolution are tightly coupled to Fallout combat math.

### General principle

Each tactical action should expose an explicit cost specification, including optional surcharges such as precision/aiming, and should be validated against the actor budget before execution.

### Disposition candidate

KEEP the action-cost contract and precision-cost idea. REPLACE Fallout hit/damage probability math with the VTM-derived resolution grammar where applicable.

---

## F2-TAC-006 — Inventory and item interaction are tactical actions during combat

### Observed behavior

Opening/using the player inventory during combat consumes AP. In the inspected implementation the normal inventory cost is `4 - 2 * Quick Pockets rank`, subject to a minimum behavior determined by the rule. Using an inventory item on a target also consumes AP.

### Strengths

- Equipment access during combat is not a free pause exploit.
- Non-attack utility actions compete with offensive actions.

### Limitations

- The exact cost/perk logic is Fallout-specific and player-special-cased.
- A modal inventory window is a presentation choice, not a general tactical requirement.

### General principle

Combat-relevant item/equipment manipulation should participate in the same action economy instead of bypassing it through UI modality.

### Disposition candidate

KEEP the principle. REPLACE exact costs and hard-coded player/perk branches.

---

## F2-TAC-007 — Unspent AP can become defensive value

### Observed behavior

When querying Armor Class outside the critter's own turn, Fallout 2 adds remaining combat AP to Armor Class. HtH Evade can further modify this relationship for the player.

### Strengths

- Creates a meaningful choice between spending all AP and retaining defensive value.
- Gives unspent budget tactical purpose.

### Limitations

- This is a specifically Fallout defensive model.
- It may interact poorly with VTM dodge/defense rules and supernatural speed.
- It can make a general scheduling resource double as a defense stat in a way that obscures ownership.

### General principle

Unused action capacity may be convertible into reactions/defense, but such conversion should be explicit rather than an accidental stat side effect.

### Disposition candidate

DO NOT inherit automatically. REPLACE with a deliberate reaction/defense policy if the VTM combat design needs one.

---

## F2-TAC-008 — NPC AI plans around the same AP budget

### Observed behavior

Combat AI checks available AP, required attack cost, reload cost and movement requirements. It can move toward a target while preserving enough AP to attack, select weapons/modes, reload, use drugs, retreat and finish with AP remaining.

AI behavior is substantially parameterized by data packets, including target preference, aggression, minimum hit chance, preferred distance, weapon preference, called-shot frequency, area-attack caution, retreat policy, chem use and disposition.

### Strengths

- Player and AI share the same tactical resource constraints.
- High-level tactical personality can be data-driven.
- AI can reserve budget for a planned downstream action.

### Limitations

- Specific heuristics are tuned for Fallout weapons, SPECIAL stats and party behavior.
- AI has many hard-coded branches around the original combat model.

### General principle

NPC tactical planning should reason over the same action-cost service and legal-action surface as the player, while tactical preferences remain data-driven.

### Disposition candidate

KEEP shared budget/legal-action mechanics and data-driven policy. REPLACE Fallout-specific heuristic code.

---

## F2-TAC-009 — Combat can end by disengagement/state, not only extermination

### Observed behavior

Combat-end checks examine the active combatant list and relevant hostile/team opposition. Combat can terminate when no meaningful opposition remains, not only when every non-player actor is dead.

### Strengths

- Supports fleeing, incapacitation and de-escalation.
- Avoids treating combat as an arena that only ends in annihilation.

### Limitations

- The exact team/active-list semantics are Fallout-specific.

### General principle

Combat is a tactical engagement state and should end when its semantic engagement conditions cease to hold.

### Disposition candidate

KEEP strongly; extend to surrender, frenzy state, concealment, social interruption, flight and supernatural disengagement where appropriate.

---

## F2-TAC-010 — Combat save/load persists substantial tactical state, but resume semantics are imperfect

### Observed behavior

The combat save path persists combat state, turn-running state, free-move state, combatant counts/order, actor identity references and selected AI tactical memory. Runtime references are rebuilt through serialized identities.

However, the inspected resume behavior contains a recovery quirk: a loaded in-combat state can force the player turn before resuming the remainder of the combat sequence rather than restoring a conceptually exact current-actor continuation.

### Strengths

- Tactical state is treated as persistent state rather than reconstructed from the map.
- Combatant identity/order and AI context are serialized.

### Limitations

- Resume semantics are not a clean deterministic continuation contract.
- Pointer/reference restoration and ordering are bound to the original engine implementation.

### General principle

A save made during combat should preserve the exact semantic scheduler state: round, current actor, remaining budget, pending reactions/actions and deterministic RNG position.

### Disposition candidate

KEEP persistence principle. REPLACE the resume quirk with exact deterministic continuation.

---

## F2-TAC-011 — Script combat callbacks can override default turn behavior

### Observed behavior

A critter combat script can execute during a turn. Script override state can suppress the default player/AI turn behavior.

### Strengths

- Authored exceptions can replace default behavior where necessary.

### Limitations

- A generic override flag is broad and difficult to reason about.
- It can bypass normal tactical invariants if used indiscriminately.

### General principle

The tactical system needs controlled extension points, but authored content should not gain unrestricted authority to bypass action-budget or state-ownership rules.

### Disposition candidate

KEEP controlled extension hooks. REPLACE generic unrestricted script override with typed override/command policies.

---

## F2-TAC-012 — Animation is downstream of tactical intent but movement animation can participate in AP consumption

### Observed behavior

Fallout 2 builds animation sequences for movement and action presentation. Movement execution consumes movement/AP budget as path steps are advanced. Combat animation state is coordinated with the turn system.

### Strengths

- Presentation can express a validated tactical action without redefining its intent.
- Movement interruption can correspond to actual exhausted budget.

### Limitations

- Animation and simulation concerns are more intertwined than desirable for deterministic headless testing.

### General principle

Authoritative tactical scheduling and result resolution should remain headless; presentation/animation consumes the resulting action plan/events without owning causal truth.

### Disposition candidate

KEEP intent-before-presentation principle. Further separate simulation from rendering/animation in VampiroCRPG.

---

## Cross-corpus implications for VampiroCRPG

The strongest reusable Fallout tactical skeleton is:

`round boundary -> deterministic actor order -> per-actor budget refresh -> actor chooses legal budgeted actions -> movement/actions consume shared budget -> semantic result -> next actor -> next round -> world time advances`

The strongest VTM requirement from `VTM_TO_CRPG_TRANSLATION_08_TRAITS_DICE_ACTION_RESOLUTION` is:

`ActionEconomy authorizes/schedules ActionIntent -> owning system builds ActionCheckSpec when uncertainty exists -> ActionResolution resolves d10 mechanics -> owning system applies semantic result -> world events/consequences propagate`

These are compatible because they answer different questions:

- Fallout-style action economy answers **when/how much may I act?**
- VTM-derived action resolution answers **what happens when the uncertain action is attempted?**

This separation prevents double-charging the same concept with both full AP restrictions and literal tabletop multiple-action penalties.

## Preliminary KEEP / EXTEND / REPLACE direction

### KEEP

- finite per-actor tactical action budget;
- deterministic turn/round order;
- round-boundary budget refresh;
- movement competing with other actions for budget;
- explicit data/rule-derived action costs;
- precision/aimed-action surcharge pattern;
- player/NPC parity in action-budget mechanics;
- data-driven tactical AI preferences;
- semantic combat exit conditions;
- combat advancing authoritative simulation time;
- save/load of tactical scheduler state.

### EXTEND

- generalized typed action-cost/modifier service;
- actor-specific movement/reaction/supernatural modifiers instead of player globals;
- supernatural capability costs integrating with AP only when their rule/action timing requires it;
- explicit reaction/reflexive windows;
- Beast/Frenzy action policy using the same legal action surface and budget;
- Celerity integration through one action-economy mechanism rather than duplicated extra-action rules;
- exact combat scheduler persistence including current actor and pending action/reaction state;
- combat time feeding the same global scheduler used by dawn, investigations and delayed consequences.

### REPLACE / DO NOT INHERIT AUTOMATICALLY

- `Agility / 2 + 5` AP formula;
- `Sequence = 2 * Perception` initiative formula;
- opening-round attacker/defender/player forced positions;
- player-global `_combat_free_move` state;
- hard-coded player-only perk cost branches;
- Fallout hit chance, critical and damage mathematics;
- remaining AP automatically adding to Armor Class;
- generic script override;
- in-combat save/load recovery that forces a player turn;
- Fallout-specific AI decision heuristics.

---

## Open verification items

The current pass is sufficient for first cross-corpus action-economy design, but the following may need targeted inspection before final combat freeze:

1. exact stand-up / recovery AP costs and state transitions;
2. weapon/equipment switching AP behavior through all UI/action paths;
3. combat-entry edge cases and surprise/ambush semantics;
4. party-member turn/control behavior;
5. detailed reaction to knockdown/lose-turn states;
6. exact interaction of Bonus Move/free movement with all movement modes;
7. any animation-completion dependencies that materially affect action scheduling;
8. combat exit/re-entry edge cases after fleeing/concealment;
9. save/load behavior with queued animations or partially executed tactical actions.

Do not broaden the Fallout investigation beyond issues that can materially change the VampiroCRPG tactical contract.

## Next action

Produce the VTM↔Fallout tactical reconciliation document. Freeze only the interface between `ActionEconomy` and the already-defined VTM `ActionResolution`; leave exact AP totals, initiative formula, seconds-per-round, Celerity adaptation and reaction policy as `NEEDS_DECISION` until the first headless tactical prototype can compare candidate values.
