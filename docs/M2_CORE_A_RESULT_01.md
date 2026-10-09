# Resultado 01 — La Noche que Recuerda, núcleo A

**DONE:** prueba desnuda implementada y ejecutada con Python 3.12.14 y biblioteca estándar. No se instaló Godot. Dirección autorizó el contrato 0.2; D-011 registrada en DECISION_REGISTER.

**EVIDENCE:** 29 tests, cero fallos/errores. Cobertura NQR-01–09 y F-01–07. [Informe reproducible](../tests/results/m2_core_a_run.json) con inputs, seed, versiones, actual/expected y hashes. [Traza causal completa](../tests/results/late_copy_trace.json).

| Escenario ejecutado | Original | Copia | Encargo | Presupuesto G1 | Base de revisión |
| --- | --- | --- | --- | --- | --- |
| Retirada tardía | Retirado | Sobrevive | Completado | 1 | Informe + copia |
| Retirada temprana | Retirado | No se crea | Completado | 1 | Informe |
| Acceso denegado | Disponible | Sobrevive | Bloqueado al llegar | 1 | Informe + copia |
| Información insuficiente | Disponible | Sobrevive | Bloqueado antes de viajar | 2 | Informe + copia |

La visita puede ocurrir en los cuatro: el informe testimonial sigue siendo una vía elegible. Cambian los indicios que la sostienen, sin obligar a cada variante a tener otra misión final. El protagonista sólo recibe el mensaje limitado y percibe la indagación pública; no conoce la copia privada.

Se comparó cada frontera de operación de los cuatro escenarios en ejecución continua y serializando/restaurando antes y después de cada commit. Estados, causas, cola, contadores y receipts coinciden. La visita pendiente al guardar t9 ocurre t12; los cargos/copia/retirada no se duplican. Se verificó guardar a disco y reanudar por CLI, rechazando un escenario diferente.

También pasaron: cámara sin testigo; testigo sin cámara; ausencia de ambos sin caso omnisciente; negativa a informar; alias sin atribución automática; bitácora adquirida por acceso; recursos insuficientes; permisos/disponibilidad revalidados; idempotencia y colisión; consultas puras; orden simultáneo; descarga sólo visual; límite de 128 handlers conservado al cargar; carga inválida sin publicar; interrupción con rollback; cancelación sin restaurar evidencia; agente indisponible sin comunicación mágica.

Corrección de fixture: viaje explícito del protagonista al refugio t1–t2. Dormir no cambia su localización. El incidente y la alimentación entran resueltos como estímulo exclusivo del harness.

**OPEN:** microhistoria causal bajo perfiles finitos. No implementa planificación general de NPC, sangre/Bestia/moralidad, combate, Disciplinas, inventario general o arte. Snapshot JSON interno y rollback por copia completa son herramientas de ensayo; no congelan saves o rendimiento del juego final. Revisión de dirección sobre el comportamiento aún abierta.

**NEXT:** preparar el perfil mínimo de B con las decisiones pendientes, usando las traducciones existentes; cerrar sus reglas antes de programarlo. Gráficos y tecnología de producción pendientes.

[Comandos para repetir](../proof/README.md). PROJECT_STATE_MASTER en Drive conserva el checkpoint ejecutivo; el código y resultados son la evidencia técnica.
