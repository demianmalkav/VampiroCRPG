# M2 revision 0.2 — revisión concreta de arquitectura

Status: PROPOSED / NEEDS DIRECTOR ACCEPTANCE  
No game code added; no simulation acceptance test run.

## Qué cambia frente a 0.1

El contrato conserva las ocho obligaciones de mundo persistente, pero reduce el primer ensayo al núcleo A de la reconciliación 01–14. Son seis actores, tres lugares, un encargo y un caso. G1 es mortal; alimentación entra ya resuelta. Sangre/Bestia/voluntad/moralidad se agregan en B; combate/poderes/política completa esperan C.

Se precisan orden (due_tick, enqueue_seq), commits indivisibles, receipts idempotentes, límites de trabajo en un tick, carga validada y canales explícitos de acceso. Caso e informes pueden continuar aunque el original desaparezca. Lo que el jugador descubre y lo que ya hizo el mundo son estados diferentes.

## Decisión para dirección

Aprobar este núcleo A como base del primer prototipo headless, o señalar correcciones a su alcance/comportamiento. La aceptación comprende las ocho obligaciones de 0.1 y la política candidata de scheduler/commit/save de 0.2. No elige automáticamente engine/lenguaje ni cierra los pendientes de B.

La revisión no equivale a aprobar una implementación inexistente. Un merge de documentación tampoco debe cambiar por sí solo NEEDS DIRECTOR ACCEPTANCE a ACCEPTED; la decisión debe quedar registrada en Drive.

## Material para revisar

- [Contrato candidato](M2_CAUSAL_SIMULATION_CONTRACT.md).
- [Ensayos y fronteras](M2_CORE_A_ACCEPTANCE.md).
- [Cuatro fixtures declarativos](../tests/specs/m2_core_a_cases.json).
- [Alcance de diseño](https://docs.google.com/document/d/1GbWEeyIQvvoVT-ohiAIQkQ-uSZypaU3deCQPWOXHdow/edit).
- [Corrección Fallout que condiciona el scheduler](../research/FALLOUT2/QUEUE_LIFETIME_CORRECTION.md).

## Verificación de este cambio

Se valida JSON, unicidad de actores/entradas/casos, localizaciones y rutas, orden de inputs, existencia de paths de overrides, campos requeridos y cobertura documental de ensayos. No se ejecuta la simulación porque aún no existe. Las expectativas JSON permanecen NOT_RUN.

## Después de aprobación

Registrar decisión; escoger runtime/runner mínimo para A; implementar núcleo y ensayos; contrastar estados continuos con guardado/carga; diagnosticar causas; recién luego cerrar B e integrar presentación mínima. No producción masiva antes de esa validación.

