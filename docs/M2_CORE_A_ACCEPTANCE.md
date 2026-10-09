# M2 núcleo A — especificación de aceptación

Status: APPROVED FOR PROOF; EXECUTED IN PYTHON PROTOTYPE  
Runtime results: NQR-01–09 / F-01–07 PASS. [Resultado y límites](M2_CORE_A_RESULT_01.md). Fixtures validated statically are not acceptance tests passed.

## Protocolo común

Cada ensayo carga un mundo nuevo con versiones explícitas de contrato/perfil, seed y entradas ordenadas. A produce un incidente ya resuelto: no afirma reglas de alimentación, poderes, AP o daño implementadas.

Aplicar overrides antes de inicializar. Las salidas esperadas se evalúan mediante queries de prueba; no se insertan en el mundo como instrucciones de resultado. Los labels de objetos derivados del JSON permiten identificar resultados del harness; su sintaxis no es un formato publicado de save.

El runner construye el estado, registra inputs, avanza ticks mediante el scheduler y compara actual/expected. Ningún ensayo pasa por sólo existir el objeto JSON. Error de fixture es distinto de fallo de simulación.

## Entradas finitas y procedimientos

[m2_core_a_cases.json](../tests/specs/m2_core_a_cases.json) contiene baseline tardío, retirada temprana, acceso denegado e información insuficiente. Las rutas y el coste de viaje son sintéticos. Los overrides cambian condiciones previas, jamás establecen el estado final.

Un permiso existente pertenece a P1 y G1; V0 comunica su referencia y no crea autorización institucional. La tarea localiza la grabación mediante dispositivo/tick/office, no mediante conocimiento de una copia oculta. Si faltan datos, queda bloqueada antes de reservar/viajar. Si el permiso se revoca después de aceptar o está denegado al llegar, el viaje real sigue costando su unidad.

Para hacer inequívoca la denegación del JSON: la autorización no se consulta como conocimiento completo en aceptación; ésta valida que se recibió una referencia de permiso plausible. La disponibilidad/validez efectiva se consulta en access_check al llegar. No se devuelve el cargo de un viaje ya realizado. Una versión con denegación conocida de antemano deberá emitir un rechazo temprano y expectativas distintas.

El archivo automático puede copiar REC_ORIG por su propio grant de archivo de P1. Ese grant es independiente de ORIGINAL_ACCESS de G1; revocarlo a G1 no evita la copia de P1. Los roles report_submitter/assigned_reviewer incluyen los accesos limitados previstos; se materializarán como perfiles versionados.

## NQR-01 — conocimiento, testimonio y relación

Given: W1 observa, W2/I1 no están en L_INC; sólo W1 conocía previamente el alias como apariencia/nombre, sin identidad vampírica.

When: confirmar incidente; consultar antes de t3; después transmitir por teléfono con la transformación configurada.

Then: W1 tiene percepción/memoria directa de sus rasgos autorizados; W2/I1/P1 no reciben esa memoria. Fear/trust de W1 cambian por el evento observado. En t3 W2 obtiene contenido reducido con origen testimonial; contact_details no aparecen por acceso a debug. Su confidence/stance es propia. I1 sólo obtiene contenido al consultar/recibir por su rol.

## NQR-02 — independencia de cámara

Given: desactivar witness_enabled, manteniendo cámara, archivo y reconocimiento previo del alias disponible para I1.

When: capturar y revisar por acceso autorizado.

Then: no hay memoria W1, MSG_TESTIMONY o REC_REPORT; sí grabación. Antes de revisar, I1 no conoce el incidente. Después puede abrir caso con evidencia de vídeo y, sólo con la muestra de apariencia autorizada, relacionar el alias. Repetir sin esa muestra: no enlace automático al alias.

Witness-only: desactivar capture_enabled; mantener W1. Then no original/copy, pero puede haber informe y caso testimonial. No-information-channel: desactivar ambos y usar incidente no crítico sin otros indicios configurados. Then no caso por omnisciencia. La condición de M0 existe sin una vía médica implementada en A.

## NQR-03 — retirada tardía

Given: late_copy; t4 copia y t6 retirada.

When: continuar hasta t12.

Then: original no disponible; copia íntegra/custodiada; informe independiente; task completed; presupuesto G1=1/reserva=0. I1 usa report + copy. V0 recibe el mensaje limitado y no sabe de la copia. El resultado original/copia y cada gasto son descendientes de sus comandos/eventos propios.

## NQR-04 — retirada temprana

Given: early_removal; cambiar sólo duración de ruta del agente, sin órdenes de resultado.

When: llegada t2, retirada t3, copia prevista t4.

Then: original inaccesible para el procedimiento de copia; REC_COPY no se crea. W1/testimonio/informe sobreviven. El caso sigue abierto por informe elegible y la visita puede ocurrir; review_support sólo cita REC_REPORT. El éxito de limpieza es interrupción de una vía, no anulación global del problema.

## NQR-05 — alcance de tarea

Given: denied_access o insufficient_directive.

When: ejecutar la tarea real.

Then: denegación al llegar conserva original/copia, produce bloqueo e informe, presupuesto G1=1. Falta de oficina bloquea antes de viajar/reservar, presupuesto=2. Ninguna ruta obtiene información de debug. La copia sigue protegida por su acceso propio.

Repetir con el mismo CommandId después de guardar: mismo receipt; no segundo gasto, viaje o retiro. Usar mismo ID/payload diferente: COMMAND_ID_COLLISION y estado de dominio idéntico.

## NQR-06 — rastro de limpieza

Given: perfil de bitácora habilitado y retirada autorizada.

When: G1 inspecciona/retira; I1 obtiene la bitácora por acceso de su caso.

Then: ACCESS_LOG cita la acción de G1 y lugar/tick permitidos. I1 puede asociar G1 a la intervención. No aprende L_HAV o identidad vampírica de V0. El testimonio no se borra por esa bitácora. La copia del informe no altera la acción original.

## NQR-07 — procedimiento institucional

Given: W2 escucha pero recipient_reports=false.

When: avanzar comunicación/revisión.

Then: W2 conserva su relato; no existe REC_REPORT. P1 sólo actúa si otra vía autorizada aporta indicios; con cámara desactivada no abre caso. Un actor que pertenece a P1 pero no recibió/leyó el expediente no hereda contenido privado.

Revisar récord inaccessible: resultado bloqueado sin contenido. Acceso lícito crea una adquisición con cause_id. CaseState no reemplaza esa causa. El procedimiento de archivo conoce dónde copiar, sin una creencia “todo miembro sabe lo que pasó”.

## NQR-08 — guardado y descarga

Given: cada case JSON y cada frontera de commit declarada.

When: ejecutar una vez continuamente; otra con Save/Load y descarga de L_INC; reanudar las mismas entradas.

Then: iguales estados/causas/cola/receipts/contadores en cada checkpoint; ninguna copia, retirada o cargo duplicado. Visit scheduled antes del save sigue pendiente y ocurre t12. La comparación excluye sólo metadatos locales de archivo/presentación.

Restaurar no reproduce handlers ya confirmados. Guardar antes de una retirada preserva trabajo pendiente, no su outcome; después preserva su receipt y efectos.

## NQR-09 — causas, alias y descubrimiento

Given: caso abierto y revisión real. V0 no accedió al expediente ni a la copia.

When: programar visita; V0 despierta t10, recibe mensaje y viaja L_INC; I1 hace indagación visible t12.

Then: WhyProcessStarted/WhyBelieves enumera la vía recibida, memory/message o camera/record/access, y evento original. La visita deriva de la revisión/caso. V0 sólo aprende lo que percibe del encuentro; saber de la indagación no le otorga la copia ni hipótesis ocultas. El alias es comprometido respecto de I1, sin resolver clan/identidad real.

La consulta de debug es pura. El ensayo comprueba Fear/trust de W1 con procedencia y evita una reputación global. Desactivar observación de V0 en t12 preserva la visita pero no crea su conocimiento: player discovery separado de world change.

## Fronteras obligatorias

F-01 — mismo tick, copia primero: programar copia antes de retirada con igual due_tick. La copia se confirma y sobrevive al retiro. Guardar no cambia enqueue_seq.

F-02 — mismo tick, retirada primero: invertir exclusivamente el orden de programación. Falla la copia que necesita el original; el testimonio permanece. Prueba que la prioridad no es por “jugador” o “institución”.

F-03 — presentación: programar callback PRESENTATION_LOCAL y trabajo WORLD_PROCESS; descargar escena elimina el primero y conserva el segundo. El callback nunca muta dominio.

F-04 — protección de bucle: un handler de prueba encadena trabajo mismo tick. Al superar 128, detención diagnosticada en último commit; siguiente trabajo queda pendiente. Save/Load no reinicia el contador. El handler de estrés pertenece al harness, no a misiones.

F-05 — carga inválida: copiar snapshot de ensayo y quitar un ID target o introducir versión incompatible. Carga falla antes de publicar; mundo previamente cargado permanece idéntico. No retarget ni reparación silenciosa.

F-06 — input/receipts: entradas idénticas y ordenadas reproducen estado/log; repetir command/payload mantiene resultado; colisión de payload se rechaza. Ninguna lectura/debug/render consume RNG.

F-07 — copia/alcance: retirar original nunca cambia custody/integrity de la copia ni el contenido de recuerdos. Revocar grant G1 no revoca el acceso del archivo o de I1.

## Diferido a B

NQR-10: transacción de sangre y lesión sellada; NQR-11: Bestia y pago de acción lúcida; NQR-12: incidente moral único y prohibición de compra de éxito con voluntad. No se simulan ni se marcan verdes en A. Exigen resolver sus pendientes de fuente/adaptación.

## Criterio de aprobación y reporte

El runner reporta contrato/perfil, seed/inputs, actual/expected, hash de estado, tests y traceback de fallos. El test de continuidad compara snapshots en cada commit; una aserción identifica el desacuerdo y la traza permite recorrer causas. NQR-01–09 y F-01–07 pasaron en el runtime implementado. No hay depurador interactivo de divergencias o rendimiento de producción certificado.

La revisión conserva AT-01–18 a través de la matriz de correspondencia del contrato. No transforma 18 + 9 + 7 en treinta y cuatro features ni interpreta recuentos como profundidad lograda.

