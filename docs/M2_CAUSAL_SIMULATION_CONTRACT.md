# M2 Causal Simulation Contract — La Noche que Recuerda

Status: DRAFT FOR ARCHITECTURE REVIEW — revision 0.2 candidate  
Implementation status: no simulation/gameplay code; no M2 acceptance test executed.  
Scope authority: [Reconciliación de alcance 01](https://docs.google.com/document/d/1GbWEeyIQvvoVT-ohiAIQkQ-uSZypaU3deCQPWOXHdow/edit).

## 1. Objetivo y límite

Demostrar la cadena hecho → observación → memoria/creencia → transmisión/registro → procedimiento → consecuencia diferida, con causas auditables, conocimiento individual y continuidad al guardar o descargar una escena.

Esta revisión precisa el núcleo A de la propuesta 01–14. La alimentación ya resuelta entra como dato de prueba; no existe todavía una implementación de alimentación o de una Disciplina. La etapa B agregará sangre, víctima, hambre, Bestia, voluntad y moralidad mediante sus dueños reales. Combate, AP, política Kindred, ghoul completo, Vínculo dinámico y poderes canónicos se difieren a C.

Los términos MUST/DEBE indican obligaciones de la propuesta, no arquitectura aprobada. Ningún archivo de esta revisión es un esquema de guardado en producción. No se elige engine, lenguaje del juego, ECS, base de datos o tecnología de serialización.

## 2. Disposición del corpus Fallout

Se conserva la frontera intención/ejecución, las superficies finitas de eventos, la propiedad del estado, el tiempo de simulación y el guardado coordinado. Se extienden con observaciones y memoria individuales, custodia de registros, procesos persistentes y explicación causal. Se reemplazan globals de misión como autoridad causal, reacción social universal y persistencia de punteros.

La [corrección de cola](../research/FALLOUT2/QUEUE_LIFETIME_CORRECTION.md) prevalece sobre generalizaciones anteriores: el guardado completo de Fallout no implica que todo timer sobreviva al salir del mapa. Testimonio, encargo, copia, revisión y visita de M2 DEBEN sobrevivir a la descarga de presentación.

## 3. Reparto, localizaciones e identidad

Seis actores: actor:V0, actor:M0, actor:W1, actor:W2, actor:G1 y actor:I1. M0 es la víctima; W1 es otra persona. G1 usa perfil mortal en A. P1 es institution:P1, una organización con registros/procedimientos, no un cerebro que comparte memorias.

Tres localizaciones: location:L_INC, location:L_REG y location:L_HAV. device:D_CAM crea record:REC_ORIG; record:REC_COPY es una copia independiente; record:REC_REPORT contiene el testimonio de W2. persona:V0_ALIAS es un alias, no otro Actor.

H1/R1/C1 de documentos anteriores no son IDs reutilizables: se usaron para roles diferentes. Un receptor Kindred futuro será actor:K1; un contacto será actor:CONTACT1; un segundo refugio tendrá otro LocationId.

Todo objeto persistente tiene ID tipado y estable. El asignador determinista, su namespace/contador y su versión se preservan. No se reutilizan IDs en una misma línea de guardado. Las referencias de runtime se reconstruyen; nunca son autoridad persistida. Un ID ausente causa un error validado y no se sustituye por un actor “parecido”.

## 4. Superficie mínima de registros

Esta tabla define responsabilidades y campos conceptuales obligatorios. La forma concreta de clases/archivos queda para implementación después de aprobación.

| Registro | Dueño y campos mínimos | Restricción |
| --- | --- | --- |
| WorldState | tick, versions, allocator, enqueue_seq, counters, RNG, input cursor | No reloj de pared; configura el orden común |
| ActorState | id, location, persona, availability, task_budget de prueba | El presupuesto sintético no es sangre, AP ni voluntad |
| Location/Device | id, location, coverage/access/schedule profile | Existencia separada de presentación |
| WorldEvent | id, type, tick, source, targets, typed payload, causes, command/process | Hecho ocurrido; no conocimiento automático |
| Observation | id, observer, channel, perceived features, source IDs, tick | Proyección autorizada; excluye campos secretos |
| Proposition | id, typed claim, referents, objective status si se conoce | Claim distinto de certeza del titular |
| Belief/Memory | holder, proposition/content, provenance, stance, acquisition event | Directo y testimonio conservan procedencias distintas |
| Record/Evidence | id, origin, contents/features, custody, location, integrity, access, derivation | Copia independiente; borrar original no borra descendientes |
| Message | id, sender, recipient/channel, disclosed content, sent/delivery events | Enviar no equivale a recibir; no acceso al pensamiento |
| Relationship | directed pair, named dimensions, causes | A usa fear/trust por observación; no reputación global |
| Institution | id, roles/access/procedure profiles, record/case IDs | Memoria de un miembro no equivale a expediente |
| Process | id, type, owner/participants, state, references, pending work, causes | Estado de tarea/caso legítimo; no misión global |
| ScheduledEvent | id, due_tick, enqueue_seq, lifetime, owner, payload, causes, status | WORLD/PROCESS no se cancela por descargar una escena |
| CommandReceipt | command_id, canonical payload identity, result/event IDs | Una misma solicitud no aplica dos veces el efecto |

Una memoria individual conserva el acto de percibir o recibir. Un registro institucional conserva contenido sometido a custodia/acceso. Una creencia puede citar cualquiera de ellos sin convertir su procedencia en verdad objetiva. Las escalas de creencia/relación de la prueba son bandas declarativas versionadas; no representan balance social final.

Evidence es el rol de un objeto/registro al usarse como indicio, no una copia obligatoria de todos sus datos. Una grabación puede ser Record y servir como Evidence por referencia al mismo ID. Evitar dos autoridades para su integridad o custodia.

## 5. Commands, hechos y transacciones

Superficie A: SendMessage, AcceptDirective, StartTravel, InspectRecord, RemoveRecord, SubmitRecord, ReviewCase, ScheduleVisit, ChangeAvailability y RequestInteraction. InjectResolvedIncident es exclusivamente una entrada privilegiada del harness, jamás una opción de jugador/contenido. AdvanceTo y Save/Load son operaciones del núcleo/harness.

El dueño valida identidad, agencia, información comunicada, lugar, permisos, recursos y estado actual del objetivo. Rechazo devuelve una razón y no modifica el estado de dominio ni consume RNG. Un nuevo intento deliberado usa otro CommandId.

Un command aceptado o un handler diferido se confirma como transacción indivisible: mutaciones, pagos/reservas, receipt, eventos derivados e inserciones/cancelaciones de cola se hacen visibles juntos. El guardado ocurre entre estas confirmaciones. No se permite guardar una mitad de la retirada y después cobrarla de nuevo.

Reenviar el mismo CommandId con idéntico payload devuelve su receipt anterior, sin nueva retirada, cargo, RNG o enqueue_seq. Reutilizarlo con payload diferente devuelve COMMAND_ID_COLLISION. Los receipts se preservan durante todo A; su compactación es trabajo futuro.

Un evento documenta un resultado ya confirmado. Los handlers de efectos derivados reciben eventos sólo después del commit; se ejecutan por el scheduler común o dentro de una composición transaccional explícita. No hay callbacks reentrantes que modifiquen medio estado.

## 6. Percepción, mensaje y acceso

El incidente contiene rasgos objetivos necesarios para el ensayo, por ejemplo colmillos visibles y contacto con M0. El perfil de W1/D_CAM determina qué rasgos capturan. No se copia a un observer el estado interno de sangre, intención o clan. La hipótesis inicial puede ser “incidente anómalo relacionado con el alias”; certeza vampírica no es requisito.

El alias es reconocible para W1 sólo porque el fixture inicial incluye familiaridad/contacto previo con esa identidad presentada. La cámara por sí sola registra rasgos visibles; asociar una imagen al alias requiere un canal configurado. Desactivar ese canal impide el enlace aunque haya vídeo.

El mensaje de W1 puede perder detalles conforme a una transformación determinista. W2 conserva el origen testimonial y su propia interpretación. MSG_DIRECTIVE transporta objetivo, oficina, permiso y plazo que V0 conoce; no incluye REC_COPY por acceso al debug.

Consultar un registro crea una adquisición de contenido con su causa de acceso. Tener permiso no significa que ya se leyó. Estar en P1 tampoco. G1 puede inspeccionar el original autorizado; no recibe acceso a todo el archivo institucional.

## 7. Encargo acotado de G1

Una tarea exclusiva: retirar REC_ORIG. Estados propuestos: awaiting_delivery, offered, accepted, travelling, access_check, acting, reporting, completed/blocked/cancelled. Los estados son progreso real del proceso y pueden derivarse de sus eventos. No habilitan resultados por sí solos.

Al aceptar, se verifica la información mínima y se reserva una unidad del task_budget sintético. El primer desplazamiento confirma ese gasto. Si el encargo no inicia el viaje, se libera la reserva; haber llegado y no poder entrar no devuelve el coste de viaje. El perfil inicial tiene dos unidades y usa una. Es un contador de prueba para verificar propiedad/idempotencia, no economía final.

Llegada, acceso y retirada validan nuevamente condiciones al ejecutarse. G1 debe conocer ubicación/objetivo; tener la autorización limitada; estar disponible; llegar dentro del plazo; encontrar el original accesible. La copia no desaparece por compartir una derivación.

El informe exitoso declara “retiré el original; no observé otras copias”. No declara ausencia global de copias. Un bloqueo produce un informe de su limitación. Cancelación posterior a la retirada detiene lo pendiente, sin resucitar el original.

## 8. Procedimiento institucional de prueba

P1 tiene roles declarados: W2 puede someter su informe; I1 está asignado y puede acceder a los registros de su caso. Un procedimiento automático de archivo de P1 puede copiar una grabación recibida mediante su acceso explícito. Esto no crea creencias ni otorga contenido a otros miembros.

Política mínima A, versionada y ficticia:

- Un informe elegible con contenido de anomalía y procedencia abre un caso sin exigir certeza sobrenatural.
- Una revisión de grabación obtenida por vía autorizada puede abrir un caso si no hay informe.
- Obtener las dos vías agrega corroboración; una revisión no transforma por defecto el testimonio en observación directa.
- La visita a L_INC requiere caso abierto y la lectura por I1 de al menos un indicio elegible. Identificar el alias requiere atribución conocida por ese canal.
- Revisión/copia no puede leer un original retirado/inaccesible. Una copia previa válida sigue disponible por su propio acceso.
- La visita no revela L_HAV, clan, sangre ni identidad real.

Una ruta sólo testimonial puede justificar la misma visita con otra base informativa. La prueba distingue sus referencias y corroboración, aunque una consecuencia visible coincida. Branch sensitivity no exige que toda variante termine en una misión distinta.

Los umbrales y roles son procedimiento del fixture, no un simulador completo de policía ni una regla VTM universal. CaseState puede ser open/reviewed/visit_planned; sus transiciones exigen hechos/access reales, no un QUEST_STAGE.

## 9. Scheduler candidato: orden y avance exactos

Tiempo A: tick entero lógico; no minutos, turnos VTM u horas solares. La conversión de tiempo de B sigue pendiente.

Orden total de trabajo diferido: (due_tick, enqueue_seq). enqueue_seq es global, único y monótono; se asigna al confirmar la programación y se guarda. No hay prioridad secreta por tipo de actor/evento. Si copia y retirada vencen en el mismo tick, gana la que se programó primero.

Las entradas externas tienen input_seq único y un orden serializado. AdvanceTo(T) procesa todo trabajo con due_tick <= T antes de aceptar la siguiente entrada externa. Si ésta programa trabajo en el tick actual, se procesa antes de la siguiente entrada. Los productores recorren destinos en orden estable; nunca depende de la iteración de un contenedor.

Un handler que programa trabajo para el tick actual recibe un enqueue_seq posterior y no salta por delante de trabajo ya en cola. Programar en el pasado se rechaza. El tick lógico nunca retrocede.

Perfil de protección A: máximo de 128 handlers en un mismo tick. El contador se guarda y sólo se reinicia al avanzar el tick; dividir llamadas o cargar no evita el límite. Si se excede, se detiene en el último commit, queda el siguiente trabajo pendiente y se expone diagnóstico. No se borra silenciosamente trabajo para “resolver” el bucle.

Guardar entre handlers confirmados permite restaurar el siguiente trabajo exactamente. AdvanceTo puede hacer múltiples commits; su parada intermedia no se presenta como operación de dominio indivisible.

## 10. Lifetimes y descarga

WORLD_PROCESS es el único lifetime del scheduler de dominio de A. Incluye testimonio, recepción, viaje, copia, retirada, informe, revisión y visita.

PRESENTATION_LOCAL es un canal separado para callbacks visuales descartables. Descargar L_INC destruye sus callbacks/presentación, pero no un Actor/Record/Process ni sus eventos. La revisión 0.1 permitía hablar ambiguamente de descargar una “simulation slice”; para A esa interpretación queda excluida.

Una cancelación WORLD_PROCESS requiere evento/causa y resultado persistente cancelled/superseded. Ausencia de permisos al vencer una tarea produce un bloqueo comprobable, no pérdida del evento. Cancelar una comunicación por incapacidad real del emisor tampoco cancela una copia independiente.

## 11. Guardado, restauración y RNG

Contrato de contenido del snapshot: versiones de contrato/perfiles/save; tick; ID allocator; enqueue_seq; contador del tick; input cursor; receipts; Actor/Location/Device; personas; eventos/causas; observations/propositions/beliefs/memories; relaciones; records/evidence/custodia/copia; mensajes; institución; procesos; cola WORLD_PROCESS; estado RNG.

El formato de snapshot no se elige aquí. No se implementa migración en A: una versión incompatible se rechaza expresamente. Diseñar migraciones para una versión publicada será trabajo posterior aprobado.

Carga en staging: leer entidades; validar IDs/versiones/referencias/causas; reconstruir índices; restaurar cola exacta, contadores y RNG; publicar estado completo. Un error deja intacto el mundo ya cargado, sin reparar destinos ni eliminar registros en silencio.

Los índices de búsqueda y objetos visuales son reconstruibles y no autoridad. El historial causal se conserva íntegro en A; no se exige event sourcing como única persistencia ni reconstruir todo el mundo desde el log.

A usa procedimientos deterministas y no necesita consumir aleatoriedad para ocultar huecos de reglas. Si un handler futuro usa RNG, tiene algoritmo/versión y estado persistidos, lo consume en ejecución autorizada y no en rendering, previews, guardado o consultas. Elegir el algoritmo para B sigue NEEDS_DECISION antes de esa implementación.

Comparación de ensayo: igualdad semántica de estado ordenado y log de dominio, excluyendo metadatos locales de archivo/UI. Si se usa hash, se declara canonicalización y algoritmo. Cambiar orden serializado de inputs/perfiles es cambiar el ensayo.

## 12. Secuencia A y observación del resultado

Baseline: t0 incidente resuelto; t1 encargo; t2 sueño y descarga de presentación; t3 testimonio/submisión; t4 copia; t5 llegada; t6 retirada; t7 informe; t8 revisión; t9 planificación de visita; t10 despertar/recepción.

Compleción del descubrimiento: V0 puede viajar L_HAV → L_INC con duración de un tick desde t10. La planificación en t9 inicia el desplazamiento de I1 desde L_REG, cuya ruta dura tres ticks; su llegada permite la indagación visible sobre el alias en t12. Si V0 está presente y percibe esa interacción, obtiene una nueva observación/claim. No recibe el contenido de un expediente privado ni todo el historial de I1. Programar una visita no teletransporta al investigador.

El fixture baseline y tres variantes están en [m2_core_a_cases.json](../tests/specs/m2_core_a_cases.json). La llegada temprana t2/retirada t3 impide la copia t4 del original. La tardía permite REC_COPY. La denegación conserva el original y su copia. Cada variante modifica condiciones y tiempos, no fuerza un resultado institucional.

La cámara/archivo se ubican en L_INC/L_REG como objetos distintos: captura en el primero y almacenamiento autorizado en el segundo por el canal fijo del fixture. El transporte/registro de ese contenido es explícito en el evento de captura/ingreso; G1 no retira una cámara desde otra ubicación.

## 13. Queries y conocimiento de jugador

Debug: WhyBelieves(holder, proposition), WhyProcessStarted(process), Descendants(event), WhoAccessed(record), PendingWorldWork, ExplainCommand(receipt). Deben recorrer referencias causales sin conocer nombres de misión.

Player: recursos propios autorizados, acciones legales y sus límites conocidos, mensajes recibidos, registros leídos y consecuencias percibidas. El journal es derivado. Ni UI ni queries de jugador llaman a debug para revelar la copia desconocida.

La consulta de causas no consume RNG, avanza reloj ni crea memoria. Descubrir el caso en t12 crea el conocimiento de V0, no el caso retroactivo.

## 14. Ensayos vigentes y continuidad con 0.1

Los nueve ensayos A son NQR-01–09; los tres de supervivencia NQR-10–12 esperan B. La [especificación de aceptación](M2_CORE_A_ACCEPTANCE.md) define precondiciones, estímulos y postcondiciones, además de ensayos de frontera del scheduler/carga.

Los dieciocho AT-01–18 de 0.1 se conservan como obligaciones. Su correspondencia permite consolidar ensayos sin declarar obligaciones satisfechas por conteo:

| AT 0.1 | Ensayo que mantiene la obligación |
| --- | --- |
| AT-01, AT-02, AT-03 | NQR-01: conocimiento, procedencia y transformación testimonial |
| AT-04 | NQR-03/04: custodia, copia y retirada |
| AT-05, AT-10 | NQR-07: acceso y procedimiento institucional |
| AT-06, AT-07, AT-11, AT-16, AT-18 | NQR-08 + fronteras F-01–07 |
| AT-08, AT-13, AT-14, AT-15 | NQR-09 + NQR-01: causas, UI, alias y fear/trust |
| AT-09 | NQR-02/04/05/07: sensibilidad de canales/requisitos |
| AT-12 | NQR-06: rastro de intervención |
| AT-17 | F-03: descarte exclusivamente visual |

Estado de todos los ensayos de simulación: ESPECIFICADOS, NO EJECUTADOS. Validar sintaxis o referencias de un fixture no prueba sus consecuencias de runtime.

## 15. Puerta de revisión y siguientes decisiones

Se mantienen los ocho compromisos de revisión de 0.1: conocimiento particular y con procedencia; scheduling que sobrevive descarga; IDs persistentes/referencias reconstruibles; futuro causal guardado; ausencia de misión escalar como sustituto; relaciones multidimensionales; separación escena/mundo; ensayos headless antes de la presentación.

La decisión pedida es aprobar o corregir este núcleo A y sus reglas de orden/commit/persistencia como base para el primer prototipo headless. No incluye autorización para elegir silenciosamente toda la tecnología o programar B/C con reglas abiertas.

Después: seleccionar el runtime/lenguaje y runner mínimo conforme al entorno objetivo; registrar aceptación en Drive; escribir núcleo A y ejecutar NQR-01–09/F-01–07. Sin esa aceptación, esta revisión permanece documental y los archivos de prueba siguen siendo especificaciones.

NEEDS_DECISION antes de B: gasto de despertar, perfil de alimentación, cadencia/terminación de Bestia, regla moral mínima, ventana lúcida, voluntad/recuperación, RNG y unidades de tiempo. No bloquean la revisión de A.

## 16. Fuentes y estado

Autoridades: [AGENTS.md](../AGENTS.md); [reconciliación 01](https://docs.google.com/document/d/1GbWEeyIQvvoVT-ohiAIQkQ-uSZypaU3deCQPWOXHdow/edit); [Readiness 02](https://docs.google.com/document/d/1CwQjBfdCBV50V0dULWe-0D_xylWhP-dFOcM7xEzuiqk/edit); [matriz Fallout](../research/FALLOUT2/SYSTEM_MATRIX.md) y [corrección de cola](../research/FALLOUT2/QUEUE_LIFETIME_CORRECTION.md). Reglas exactas de supervivencia siguen en Traducciones 01/02/03/08/11 y sus fuentes.

No nueva dependencia, engine, game code o esquema publicado de save. La revisión especifica comportamiento y prepara datos de ensayo para una implementación posterior.

