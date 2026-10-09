# M2 — propuesta mínima de B, revisión 01

Estado: APPROVED_FOR_PROOF / IMPLEMENTED / EXECUTED. [Resultado medido](M2_CORE_B_RESULT_01.md).

La segunda prueba sustituye el incidente de alimentación ya resuelto de A por un proceso real: sangre del vampiro, pérdida de sangre de la víctima, control de la Bestia, una acción lúcida y una evaluación moral. Mantiene los dueños, permisos, procedencias, cola y commits indivisibles de A. No selecciona motor, lenguaje de producción, combate, inventario o presentación gráfica.

## Decisión registrada

Dirección indicó que asume la lógica propuesta y pidió continuar trabajando, delegando decisiones técnicas rutinarias y mantenimiento de registros. Se acepta este perfil para B sin gráficos en Python/biblioteca estándar; los ocho puntos del [contrato](M2_CAUSAL_SIMULATION_CONTRACT.md) quedan resueltos para este ensayo. La aceptación procede de esa instrucción, no de crear un PR. A conserva sus fixtures y su informe histórico; sus 29 tests pasaron como regresión de B.

| Punto | Propuesta concreta | Autoridad |
| --- | --- | --- |
| Sangre nocturna | Un punto por noche, también si el vampiro sigue dormido; recibo por actor y night_id | Manual p. 138; precisión respecto de Traducción 01 |
| Alimentación | Adulto de referencia 10 puntos; objetivo conservador 2; extracción máxima 3 cada 3 segundos; capacidad del vampiro 10 | Manual pp. 138–140; perfil estrecho de acceso |
| Resistencia | Autocontrol limitado por sangre; dificultades olor 3, visión 4, sabor 6; cinco éxitos acumulados | Manual pp. 138 y 228 |
| Bestia activa | Continúa alimentándose hasta estar lleno, quedarse sin fuente o ser interrumpido; cierre tras 3 ventanas tranquilas, 6 si hubo botch | Política y duración propuestas para reemplazar discreción del Narrador |
| Lucidez | Un punto de voluntad compra una sola acción de 3 segundos; no termina el frenesí | Manual p. 229; coste fijo del perfil |
| Voluntad | Reserva inicial 5/5; recuperación opcional de 1 al levantarse, una vez por noche; ninguna otra recuperación en B | Opción del manual p. 138, propuesta para este ensayo |
| Moralidad | Un incidente por proceso de alimentación; Conciencia a dificultad 8; voluntad prohibida; muerte en frenesí nivel 4 | Manual pp. 221–222; agrupación digital explícita |
| Tiempo y azar | Tick de un segundo, acciones de 3 segundos; streams SHA-256 con contador y versión persistidos | Decisión técnica propuesta para el ensayo |

Perfil de datos aprobado: [m2_core_b_profile.json](../tests/specs/m2_core_b_profile.json). El [candidato original](../tests/specs/m2_core_b_profile_candidate.json) se conserva como antecedente. Es un perfil interno de ensayo, no esquema de guardado publicado. Los valores iniciales y tiempos de la noche son datos de ensayo; no fijan el balance del juego.

## Fuentes y precisiones

Se usaron las traducciones existentes, sin reabrir su extracción completa:

- [01 — sangre y alimentación](https://docs.google.com/document/d/1_7UwotWDq8Pmr-T-M-9u2buVBa7wIKTdNvwMf5wb_W0/edit).
- [02 — Bestia](https://docs.google.com/document/d/1vGKCdvIZm756Qu8Jn0gPh01a30isqGpt3ve6VUrcBqw/edit).
- [03 — Humanidad](https://docs.google.com/document/d/1i-8IAT-HOG9nBtcliU_MvB19d7GcOtutjgRIT5WTvl4/edit).
- [08 — resolución](https://docs.google.com/document/d/1MHJ-QPf4_EA8XcOKZ-8Y9JUbtiNNx1w0VTlqH3UJ9Sg/edit).
- [11 — voluntad](https://docs.google.com/document/d/1veSv6180GiUNjuHpstRnLLkQJooSRmZ1b2juu0vr-PI/edit).

Cotejo visual dirigido del PDF español de Vampiro: La Mascarada, edición revisada: pp. 138–140, 191–192, 221–222, 228–229. Las páginas impresas coinciden con esos números del PDF utilizado. No se incorporan reglas de V5.

Precisiones que prevalecen en B sobre formulaciones ambiguas de las traducciones:

1. El gasto nocturno se aplica aunque no se levante el vampiro. Levantarse puede recuperar voluntad bajo la opción elegida; no es el único disparador del gasto de sangre.
2. En Revised, si hubo algún éxito bruto que los unos cancelaron, hay fallo ordinario. Botch requiere cero éxitos brutos y al menos un uno (p. 192). No basta con obtener cero éxitos netos.
3. Muerte del recipiente durante frenesí pertenece al nivel 4; muerte accidental por hambre fuera del frenesí al nivel 6 (p. 221). El ejemplo de pérdida de control no habilita a confundir ambos contextos.
4. El aviso moral también alcanza al personaje en frenesí, antes del acto grave (pp. 221–222). No exige devolver control gratis ni revelar el estado oculto de la víctima.

Las traducciones originales mantienen identidad y estado de working design. Esta revisión registra las precisiones usadas por B; no afirma haber corregido todos los documentos originales ni implementado todo su alcance.

## Estado inicial y propietarios

V0: generación 13, capacidad 10, gasto máximo 1 por turno para usos de sangre, Autocontrol 3, Humanidad 7, Conciencia 3, voluntad permanente/temporal 5/5. Reserva antes del primer coste nocturno: 3; después: 2. Gasto y extracción son límites distintos: poder gastar 1 no impide ingerir hasta 3.

Hambre = sangre actual < max(0, 7 − Autocontrol). En este perfil el umbral es 4. Dados de resistencia = min(Autocontrol, sangre actual), calculados de nuevo al ejecutar cada check. No existe una segunda moneda de hambre.

M0: adulto con capacidad 10. Baseline: reserva 10, pérdida previa 0. Variante letal: reserva 8, pérdida previa 2, con historia inicial explícita en el fixture; no es el mismo estado saludable. Así puede morir por ocho puntos extraídos sin permitir desbordar la capacidad de V0 ni inventar sangre descartada.

| Dueño | Autoridad que tendrá en B |
| --- | --- |
| Metabolismo | Reserva/capacidad, límite de gasto, recibos nocturnos; hambre derivada |
| Fuente y consecuencias físicas | Sangre disponible, pérdida acumulada, condición y puncturas |
| Alimentación | Contacto, política de parada, extracciones, ganancia y fin del proceso |
| Bestia | Presión, acumulación, gobierno, objetivo, ventanas y cierre del episodio |
| Voluntad | Débitos, recuperación, recibos y reserva de acción lúcida |
| Moralidad | Contexto del acto, incidente, adjudicación única y consecuencia |

No hay setters de misión que produzcan frenesí, transfieran sangre o resten Humanidad. Cada cambio emite un evento con perfil y padres causales. Se retienen los seis actores, tres lugares y procedimientos acotados de A; G1 sigue siendo mortal, sin conversión a ghoul.

## Alimentación y condición de la víctima

Se ensaya acceso ya viable a un adulto no resistente. El fixture debe declarar contacto posible, presencia común y acceso; iniciar no sortea permisos, localización o disponibilidad. Caza, forcejeo, resistencia excepcional al Beso, alimentación vampírica/animal y sustancias se difieren.

AttemptFeed registra actor, fuente, política conservadora (objetivo 2), intención y contexto inicial. El contacto crea puncturas y un estímulo percibido de sabor. Esa muestra no transfiere un punto entero: el perfil sólo contabiliza puntos completos en las extracciones siguientes. El check de hambre precede a la primera extracción de 3 segundos. No hay sabor detectado desde una fuente inaccesible u oculta.

Cada extracción compromete en una transacción:

cantidad = min(límite de 3, sangre disponible, capacidad libre, resto del objetivo si gobierna el personaje).

La fuente pierde exactamente lo que V0 gana. Un episodio activo no respeta el objetivo conservador, pero respeta acceso, capacidad, disponibilidad y velocidad. Llegar al límite de capacidad detiene la extracción y libera el contacto; por sí solo no devuelve el gobierno del personaje.

Pérdida acumulada = capacidad de la fuente − sangre restante, incluyendo la pérdida previa declarada. Bandas del perfil: hasta 2, sin emergencia; 3–4, debilidad; desde 5 con sangre positiva, emergencia médica; 0 restante, muerte. Los anclajes 2/5/10 vienen del manual; la banda de debilidad y su síntoma perceptible son adaptación de ensayo. No se convierten automáticamente los puntos de sangre en niveles de Salud ni se simula tratamiento médico.

SealBite requiere contacto/acceso físico legal y 3 segundos. Sólo cierra puncturas; conserva pérdida de sangre, condición, muerte, recuerdos, vídeo, copias y expediente. No borra una grabación previa de la mordida. Repetir una extracción o sellado con el mismo command_id devuelve el recibo sin repetir sus efectos.

## Resistencia, frenesí y acción lúcida

Se soporta sólo HUNGER_FRENZY con Autocontrol/Humanidad. Olor, visión y sabor usan observaciones válidas y sus dificultades 3/4/6. Un mismo estímulo persistente pertenece a la misma presión; no crea episodios paralelos por cada frame.

Durante RESISTING, acumular cinco éxitos netos evita el estallido para esa presión. Una tirada parcial positiva concede tantos turnos de resistencia como éxitos netos de esa tirada: 3 segundos por éxito. Al expirar se vuelve a tirar únicamente si persiste la presión de hambre. Si ésta desapareció, se cancela el check pendiente con causa registrada. Fallo o botch transfieren gobierno a BEAST. Una vez activo no se añaden rerolls gratuitos de Autocontrol para finalizarlo.

AttemptFeed encola su primera extracción antes de resolver/enlistar el vencimiento de resistencia. Si ambos vencen en el mismo segundo, la extracción tiene menor enqueue_seq y actualiza sangre antes de comprobar la presión. No se agrega una prioridad secreta al scheduler. El episodio adopta el proceso de alimentación existente; no encola una segunda extracción para el mismo actor/ventana. Una presión por actor/fuente agrupa sus estímulos válidos; el siguiente retry usa la mayor dificultad vigente de esos estímulos, sin crear tiradas paralelas.

Política acotada de Bestia: continuar la extracción legal sobre la fuente actual; si no existe contacto, seleccionar una fuente viable del mismo lugar por acceso, cercanía declarada y stable_id. Puede iniciar contacto, alimentar o esperar. No viaja entre lugares, pelea ni crea acceso que no tenga. Llena su reserva o agota la fuente; si no hay acción alimentaria legal, espera. No hace limpieza de pruebas.

Cierre propuesto: sangre al menos en el umbral de hambre, contacto de alimentación cerrado y ninguna nueva provocación de hambre válida durante 3 ventanas completas consecutivas de gobierno BEAST (9 segundos). Una ventana LUCID_ACTION no cuenta como ventana tranquila. Botch duplica a 6 ventanas (18 segundos). Una provocación válida reinicia el contador. Estar lleno no cierra de inmediato el episodio. Si no logra sangre suficiente y queda sin fuente, permanece activo esperando; no termina por un timeout arbitrario. Este cierre y la prolongación son decisiones digitales, no números canónicos de Revised.

Una acción lúcida exige episodio activo, voluntad disponible y una acción legal de 3 segundos. Opciones mínimas: ReleaseVictim, SealBite si sigue siendo accesible, MoveTo a un lugar conectado con recorrido de 3 segundos o Wait. Una ruta más larga no cabe en este derecho. MoveTo libera el contacto al iniciar el viaje; no extrae mientras viaja. Pagos y concesión se comprometen juntos antes de comenzar; gobierno LUCID_ACTION conserva reserva, acción y vencimiento al guardar. Una entrada ilegal no debita. La acción consume la ventana ordinaria de V0, sustituye la acción de Bestia de esa ventana y no añade un turno.

Al completar o expirar, el gobierno vuelve a BEAST si no se cumplieron las condiciones de fin. Durante el intervalo no pueden resolverse extracciones de V0 en paralelo. Un token no sirve para dos acciones: ninguna carga, duplicación de command_id o consulta renueva su derecho. Coste extraordinario por acción muy contraria, autolesión, combate y poderes quedan fuera de las opciones de B.

## Voluntad y límites nocturnos

NightStarted usa night_id y cobra una vez por actor incluso dormido. Wake puede recuperar min(1, capacidad − reserva) una vez por actor/night_id. Repetir Sleep/Wake, guardar o descargar presentación no repite recuperación ni sangre. El recibo se registra incluso si la reserva ya estaba llena. No hay recuperación por sesión, guardado, objetivos o Naturaleza.

Se excluye agotamiento a cero de la reserva vampírica, torpor y despertar sin sangre. Los fixtures deben tener al menos 2 puntos antes de cada coste nocturno; un comando/caso fuera de ese dominio devuelve UNSUPPORTED_EXHAUSTION antes de mutar o consumir RNG. La exclusión se informa; no se transforma en frenesí automático, éxito, relleno de sangre ni PASS de B.

## Incidente moral

Un proceso continuo sobre una víctima tiene un semantic_incident_id. Contacto, extracciones y fin lo alimentan. Se cierra al parar, cambiar de objetivo o acabar la fuente. Se elige una sola regla aplicable, la más grave (nivel numérico menor); se evalúa si nivel ≤ Humanidad actual. Reanudar un proceso distinto crea otro incidente; duplicar un evento o cargar el mismo proceso no crea otro.

Reglas mínimas del perfil:

| Contexto verificado | Nivel | Resultado antes de tirar |
| --- | --- | --- |
| Daño físico a otro, sin muerte | 8 | Con Humanidad 7 no requiere degeneración |
| Muerte accidental por hambre fuera de frenesí | 6 | Requiere check con Humanidad 7 |
| Muerte de la víctima durante gobierno de frenesí | 4 | Prevalece sobre la regla accidental; requiere check |

La regla accidental se verifica aisladamente con hechos de prueba, sin afirmar que ese camino de alimentación completo esté implementado. No se implementa toda la jerarquía: premeditación, robo, alimentación voluntaria estando saciado y otros contextos salen como UNSUPPORTED_MORAL_CONTEXT. El contexto inicial de hambre, intención y autoridad se conserva; pasar el umbral de hambre durante la misma extracción no convierte automáticamente cada tick en un acto voluntario de alimentación estando saciado.

Check: Conciencia actual, dificultad 8. Éxito conserva Humanidad; fallo resta 1; botch resta 1 de Humanidad y 1 de Conciencia y crea TRAUMA_PENDING_SELECTION con incidente y procedencia persistentes. El marcador hace visible una consecuencia todavía no desarrollada: B no simula un trastorno ni afirma cerrar su comportamiento de largo plazo. Los fixtures no alcanzan Humanidad/Conciencia 0; pérdida del personaje y Virtud agotada se difieren con rechazo explícito fuera del perfil.

Comprar un éxito con voluntad está prohibido aun con reserva disponible. La petición se rechaza antes del check y no cambia voluntad ni RNG. La evaluación legítima sigue pendiente; no se puede usar la petición inválida para suprimirla. Evaluaciones ya terminadas tienen recibo y se devuelven sin volver a tirar.

La salida textual advierte antes de una posible acción grave, también en frenesí: describe riesgo, opción lúcida y coste sin prometer la supervivencia ni exponer la reserva oculta de la víctima. Una advertencia no congela el reloj: la CLI de pasos avanza sólo con entradas explícitas y la misma regla rige sin presentación. El gobierno de la Bestia sigue siendo real.

La evaluación interna no necesita testigo, cámara o expediente. El vídeo registra hechos perceptibles del proceso, no sangre interna, intención privada, RNG o Humanidad. Sellar/eliminar el original modifica evidencias concretas; no modifica el incidente moral.

## Tiempo, azar y persistencia

B usa segundos enteros. Acción mínima 3 segundos; due_tick/enqueue_seq sigue ordenando empates. La escala no reinterpreta ni migra snapshots/fixtures de A. El reloj 12 h de noche + 12 h de día es calendario sintético de prueba, no astronomía o reglas definitivas de descanso.

Baseline de integración propuesto: NightStarted y comienzo del contacto en segundo 0, extracción conservadora y fin en 3, sellado 3→6; encargo en 12 y viaje de V0 al refugio 12→15; SleepUntil desde 15 hasta 86400; comienzo del día en 43200; testimonio 43260; copia 43320; llegada del encargado 43380; retirada 43440; informe 43500; revisión 43560; plan 43620; segunda noche y Wake 86400; visita 86460. El encargo declara not_before=43260 y duración de viaje 120 segundos. Aceptar el encargo requiere entrega real, accesos y recursos; los tiempos no fuerzan esos resultados. Variante early_copy adelanta la retirada autorizada, no borra la copia por script. SleepUntil es una entrada elegida, no una regla de torpor ni una consecuencia automática de viajar.

Ningún caso de frenesí puede enviar el encargo o SleepUntil como si V0 conservara control. Debe recuperar gobierno, o registrar esas entradas como rechazadas y cambiar la variante; el baseline de integración usa alimentación conservadora resistida. Los casos de sangre/Bestia/moralidad se ensayan además localmente sin imponerles la salida de A.

RNG propuesto sha256_counter_d10_v1: seed de 32 bytes representado por 64 hex minúsculos; stream_id ASCII restringido a letras, dígitos, dos puntos, barra, punto, guion y guion bajo (1–128 caracteres); contador unsigned de 64 bits empezando en cero. Mensaje ASCII exacto: M2B-D10-v1, LF, seed_hex, LF, stream_id, LF, contador decimal de 20 dígitos con ceros a la izquierda, sin LF final. SHA-256; leer los primeros 4 bytes como uint32 big-endian. Si valor ≥ 4294967290, descartarlo y consumir otro contador; si no, dado = 1 + valor mod 10. Se incrementa el contador por candidato, incluso descartado. Overflow falla explícitamente.

Streams separados actor:V0/beast y actor:V0/moral, con contador siguiente a usar persistido. El algoritmo, versión de perfil, seed, valores/dificultad, tirada bruta, unos, éxitos netos y posiciones antes/después figuran en la traza. No consume RNG inspección, preview, guardado, carga, permiso denegado o comando duplicado. Test vectors pueden sustituir dados exclusivamente en el harness; su traza dice TEST_VECTOR y no pretende ser una tirada generada por ese seed.

Referencias calculadas del formato RNG (no ejecución de B): con el seed candidato terminado en 01 y contador 0, los primeros cuatro bytes de SHA-256 son 8f7de5ad para actor:V0/beast (dado 6) y 7458d63c para actor:V0/moral (dado 9). Los cinco primeros dados son [6,2,4,2,4] y [9,1,4,9,5], respectivamente. El baseline obtiene una ventana inicial de resistencia de 3 segundos con [6,2]; extraer 2 antes del retry quita el hambre y cancela ese retry.

Los snapshots internos de B serán versionados aparte. Persisten sangre/fuente, condiciones, proceso de alimentación, presión/episodio, objetivo y gobierno, acción reservada, voluntad, recibos nocturnos, incidente/evaluación/trauma, streams y cola. Renderizar o descargar un lugar no los elimina. A no adquiere compatibilidad de saves de B por esta propuesta.

## Aceptación que deberá ejecutarse

Casos siguientes ejecutados con PASS en el [informe B](../tests/results/m2_core_b_run.json). La regla accidental fuera de frenesí se comprueba aisladamente con hechos de prueba, no como recorrido alimentario completo.

| ID | Evidencia exigida |
| --- | --- |
| NQR-10 | Objetivo 2: V0 2→4 y M0 10→8; extracción conserva total, coste nocturno previo una vez; sellado cierra sólo puncturas; memoria, vídeo y copia siguen; continuidad idéntica guardando antes/después de cada commit |
| NQR-11 | Dados válidos de fallo inician frenesí; superar hambre no lo termina; acción lúcida debita 1 una vez, ocupa 3 segundos y devuelve gobierno a Bestia; cargar en mitad de la ventana no duplica pago, acción o extracción; cierre respeta 9/18 segundos |
| NQR-12 | Variante M0 8: extracciones 3+3+2 dejan V0=10/M0=0; un incidente nivel 4; tres vectores verifican conservar/perder Humanidad/botch; voluntad prohibida; cámara ausente no elimina degeneración y cámara presente no conoce Humanidad |
| B-F01 | NightStarted dormido cobra; varios Wake no recuperan dos veces; repetir límites o cargar no repite costes; agotamiento excluido es informado |
| B-F02 | Sin percepción/acceso no hay check ni extracción; stream/recursos intactos tras rechazo; fuentes inaccesibles no son objetivos de Bestia |
| B-F03 | Cinco éxitos acumulados y sus ventanas; quitar presión cancela el retry; no hay tirada gratuita de cierre en un episodio ya activo |
| B-F04 | Uno cancela éxitos sin convertir un fallo en botch; botch real queda distinguido; pool se vuelve a limitar por sangre actual |
| B-F05 | Objetivo/fuente/capacidad/rate y muerte bloquean extracción extra; dos procesos no extraen simultáneamente a V0 ni dan dos acciones en una ventana |
| B-F06 | Comandos duplicados, rollback, guardado a mitad de alimentación/acción lúcida y after-load producen el mismo estado, causas y siguiente dado |
| B-F07 | Regla nivel 4 prevalece sobre accidental 6; daño 8 con Humanidad 7 no tira; incidente ya evaluado no repite; contexto no cubierto se informa |
| B-F08 | Lecturas/presentación descargada no consumen RNG ni recursos; quitar cámara cambia información pública y conserva la evaluación moral |
| B-I01 | Incidente real de alimentación inicia la cadena causal de A sin inyectar un desenlace; pipeline diurno y visita persisten al dormir/guardar; permisos, copia y conocimiento privado mantienen sus fronteras |
| A-regresión | Los 29 tests de A y sus cuatro fixtures conservan resultado tras la integración, con unidades de tiempo de A intactas |

Vectores de referencia, no resultados observados: dificultad 6, [6,1] → fallo ordinario; [1,2] → botch; [6,8] → dos éxitos. A dificultad 8 con Conciencia 3: [8,6,4] conserva 7/3; [4,6,2] deja 6/3; [1,6,4] deja 6/2 y trauma pendiente; [8,1,1] deja 6/3, sin botch. Presión de olor persistente a dificultad 3 y sangre 2: [3,7], [4,8], [3,2] acumulan 2+2+1; retries en 6 y 12 segundos si no cambia la presión.

Variante lúcida verificable: fallo inicial, M0 empieza con 8; la primera extracción deja V0=5 y M0=5 en segundo 3. MoveTo legal al refugio 3→6 paga voluntad 5→4 y libera el contacto; M0 conserva vida y emergencia médica, no se declara recuperado. Bestia continúa activa y, sin fuente allí ni nueva provocación, termina tras 9 segundos tranquilos. El caso sin intervención sigue extrayendo 3+3+2 y produce la muerte en segundo 9.

La ejecución y sus 59 tests/siete escenarios se registran en el resultado medido. El regreso del protagonista al incidente antes de la visita se hizo mediante viaje explícito, como precisa el resultado. El siguiente paso es presentación mínima sobre el núcleo verificado. Godot y gráficos permanecen fuera de esta ejecución.
