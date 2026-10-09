# M2 revision 0.2 — revisión e implementación del núcleo A

Status: APPROVED FOR CORE A PROOF / IMPLEMENTED  
Dirección autorizó la prueba sin gráficos; D-011 registrada. [Resultados reales](M2_CORE_A_RESULT_01.md).

## Alcance aceptado

Se mantienen las ocho obligaciones de mundo persistente. El núcleo A de la reconciliación 01–14 usa seis actores, tres lugares, un encargo y un caso. G1 es mortal; alimentación entra resuelta. Sangre/Bestia/voluntad/moralidad esperan B; combate/poderes/política completa esperan C.

Se implementaron orden (due_tick, enqueue_seq), commits indivisibles, receipts idempotentes, límite de handlers, carga validada y acceso explícito. Caso e informes pueden continuar aunque el original desaparezca; descubrirlos es otro cambio de estado.

## Decisión y revisión

La autorización explícita comprende las obligaciones de 0.1 y el núcleo 0.2 para este prototipo. Se eligió Python/biblioteca estándar como entorno de ensayo. La aceptación no procede de un merge ni elige el lenguaje o motor del juego. Los tests PASS demuestran el alcance de prueba; no equivalen a aceptación del juego completo.

## Material para revisar

- [Contrato](M2_CAUSAL_SIMULATION_CONTRACT.md).
- [Ensayos y fronteras](M2_CORE_A_ACCEPTANCE.md).
- [Ejecución y comandos](../proof/README.md).
- [Informe JSON](../tests/results/m2_core_a_run.json).
- [Traza baseline](../tests/results/late_copy_trace.json).
- [Alcance de diseño](https://docs.google.com/document/d/1GbWEeyIQvvoVT-ohiAIQkQ-uSZypaU3deCQPWOXHdow/edit).
- [Corrección Fallout](../research/FALLOUT2/QUEUE_LIFETIME_CORRECTION.md).

## Verificación y próximo paso

Se ejecutaron 29 tests y cuatro escenarios, incluyendo continuidad en cada commit antes/después de Save/Load, cargas inválidas, rollback, acceso y orden simultáneo. Se corrigió el regreso al refugio que faltaba como input en el fixture candidato. Informe y traza versionados.

NEXT: revisar resultados y cerrar el perfil mínimo de B (sangre, hambre/Bestia y moralidad) antes de implementarlo. Presentación y producción masiva posteriores.

