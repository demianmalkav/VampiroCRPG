# Technical State

Phase: M0 — preproduction / M2 architecture review  
Architecture status: DRAFT / NEEDS DIRECTOR ACCEPTANCE

## Implemented

Repository and research/documentation infrastructure. No engine, simulation or gameplay runtime. No M2 acceptance tests executed.

## Current review branch

M2 revision 0.2 proposal reconciles [scope 01–14](https://docs.google.com/document/d/1GbWEeyIQvvoVT-ohiAIQkQ-uSZypaU3deCQPWOXHdow/edit) with the existing causal contract.

Prepared: six-actor/three-location core A; field responsibilities; scheduler/commit/idempotency/load policies; NQR-01–09 and F-01–07 specifications; four declarative case fixtures. Static document/fixture validation is separate from simulation results.

See [review package](M2_REVIEW_02.md). Stage B/C remain deferred with their explicit rules questions. Broad source acquisition is not the next technical task.

## Gate before first prototype

The [contract review gate](M2_CAUSAL_SIMULATION_CONTRACT.md#15-puerta-de-revisión-y-siguientes-decisiones) still requires direction's explicit acceptance. No approval is inferred from creating a draft PR or merging documentation.

After acceptance: select implementation runtime/runner, record the decision, implement core A and execute its acceptance suite. Engine/presentation, save serialization technology and B rules are not silently frozen.

