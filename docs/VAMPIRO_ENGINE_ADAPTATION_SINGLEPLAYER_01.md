# Motor para Vampiro — adaptación y campaña individual primero

Estado: AUTHORIZED_ASSIMILATION / CANDIDATE_EVALUATION. Dirección pidió comenzar la asimilación de Fallout 2 con vistas a una base productiva, implementar las reglas White Wolf ya estudiadas y reservar una posibilidad online en tercer/cuarto/quinto orden. La primera entrega sigue siendo una campaña individual de Nueva York. Esta autorización no demuestra que CE sea ya el motor elegido o suficiente.

## Qué se asimila y qué se sustituye

| Frente | Mecanismo de Fallout aprovechable | Adaptación requerida para Vampiro |
| --- | --- | --- |
| Mundo y objetos | Prototipos/instancias, grilla/elevación, bloqueo, selección, visor | Registro coherente de volumen y representación; observaciones particulares por actor |
| Acciones | Aproximación, orientación y secuencias con marcador de efecto | Validación/pago/efecto determinista, fases guardables y cancelación explícita |
| Inventario y equipo | Propiedad, inventario, equipo que cambia arte corporal | Identidad por ítem entre icono/suelo/mano, prendas/siluetas; FID por categoría no cierra el requisito |
| Resolución | Infraestructura de pedir y resolver acciones | Sustituir SPECIAL, porcentajes y fórmulas Fallout por perfiles Revised/d10 y costes propios |
| Combate | Orden de actores, UI de turnos, rutas y objetivos | Iniciativa/economía/reacciones de Vampiro, daño/absorción/curación; no renombrar AP como sangre |
| Supervivencia | Reloj, entidades y eventos | Reserva/gasto sanguíneo, hambre derivada, voluntad, gobierno de Bestia, moralidad, Disciplinas y límites por generación |
| Mundo persistente | Estado/mapas, scripts, cola y save/load | Procesos WORLD/PROCESS sobreviven a descarga; memoria/testimonio/registro institucional no son una reputación escalar |
| Contenido | Interacción espacial y herramientas de datos | Campaña/arte/textos propios; bibliografía White Wolf como especificación y referencia de ambientación |

Referencia normativa del primer núcleo: [contrato causal A](M2_CAUSAL_SIMULATION_CONTRACT.md) y [perfil mínimo B](M2_CORE_B_PROPOSAL_01.md). A/B son pruebas Python separadas y medidas, todavía no módulos enlazados a CE/FOnline ni reglas completas de todo Vampiro. Su perfil y las decisiones digitales se conservan diferenciados de la regla publicada. No incorporar reglas V5 por semejanza de nombres.

## Frontera de adaptación concreta

Un adaptador traduce una intención espacial a `Command(actor_id, action_id, target_id, parameters, rules_profile)` y devuelve aceptación/rechazo, acciones programadas y eventos confirmados. La simulación de juego posee recursos, RNG, agencia, conocimiento, cola de mundo y resultados. La capa espacial posee instancias/ocupación y expone contacto/percepción. Una confirmación compuesta debe ser indivisible: validar contacto, reservar/pagar, transferir sangre/ítem, producir hechos y recibo; no mantener dos propietarios del mismo dato.

Prueba inicial de enlace posterior a A2/A3: acercarse físicamente al contacto → comprobar acceso → iniciar alimentación aprobada por perfil → aplicar extracciones al reloj común → cortar contacto al alejarse → producir observaciones sólo para testigos que perciban → guardar y reanudar sin repetir pagos/extracción. La mujer actual no se convierte automáticamente en víctima ni se implementa alimentación mediante un botón remoto.

Los ticks de un segundo de B y los milisegundos de C no son relojes intercambiables sin un puente: preservar ventanas B de 3000 ms y orden `(due_time, enqueue_seq)`. La traducción de iniciativa/acciones del combate completo se especificará usando la [economía táctica estudiada](../research/FALLOUT2/TACTICAL_ACTION_ECONOMY.md) y la traducción VTM correspondiente antes de programarla. No se adelanta por elegir un runtime.

## CE como referencia y como candidato

CE permite estudiar/ejecutar mecanismos clásicos; adaptación productiva requiere medir equipo, formatos de arte, editores, mantenimiento y sustitución de reglas. Su [LICENSE.md fijado](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/LICENSE.md) contiene limitaciones de uso y distribución: la disponibilidad del código no constituye permiso general de distribución comercial. Si se plantea vender el producto, la adopción directa necesita resolver ese punto; aprender mecanismos y escribir código propio no equivale a heredar permiso sobre contenido Fallout o White Wolf. No se afirma una conclusión jurídica de derechos ajenos ni se ha decidido comercialización.

No se usará el ejecutable clásico parcheado como dependencia silenciosa. sfall es otra línea tecnológica y sus funciones no se suponen disponibles en CE. Los datos originales del usuario quedan como entradas privadas de laboratorio, fuera del repositorio público y del paquete de nuestra campaña.

## FOnline: alternativa que se evalúa con la misma campaña mínima

El motor actual fijado en `8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb` tiene [licencia MIT](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/LICENSE), composición de ropa/modelos y armas vinculadas a huesos ya documentada. Una consulta dirigida adicional comprobó [transporte interthread en el cliente](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Source/Client/NetworkClient-Interthread.cpp), blob `e10001f0013e97f94050e9cf8dc196098ea1b52c`, y [documentación de autoridad/red](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Docs/en/explanation/authority-and-networking/index.md), blob `717ebf56c56f39ece7b4b9e8d67b4e2bcbba6fc4`. Existe comunicación cliente/servidor dentro del proceso; es un mecanismo concreto que merece medir para individual offline, no una demostración de campaña empaquetada.

Su [guía de integración](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Docs/en/how-to/build/embedding-project.md) aclara que diálogos, formatos, reglas y GUI pertenecen al juego; no asumir un editor de diálogo completo incluido. Las entidades, persistencia, pausa/reanudación y el reloj del motor deben reconciliarse con A/B. No hay build nuestro ni medición de memoria/FPS. Candidato con ventajas relevantes; todavía no ganador por lista de funciones.

## Online reservado, campaña individual prioritaria

La primera campaña funciona sin conexión, cuenta remota ni servicio público. Si la base usa arquitectura cliente/servidor, medir inicio y cierre locales automáticos o transporte dentro del proceso; el usuario no debe administrar un servidor para jugar la campaña. La posibilidad online no autoriza hoy hosting, cuentas, matchmaking, mundo persistente compartido, PvP ni MMO.

Se conservan desde ahora IDs estables, comandos/recibos idempotentes, orden de simulación explícito, snapshots versionados, dominio separado de pantalla y vistas de información por actor. En individual, la autoridad vive localmente. En una futura modalidad conectada, la autoridad elegida recibe intenciones de participantes y entrega sólo información autorizada. No se promete convertir cualquier save local en mundo compartido ni que replay determinista sea por sí solo sincronización de red.

Una futura fase propia deberá definir si online significa cooperativo de campaña, partidas limitadas u otro formato, quién guarda, qué sucede al desconectar, permisos sobre personajes, turnos/pausa, latencia y evolución de saves. Se solicitará criterio sobre esas alternativas cuando tenga sentido. Por ahora, la prueba de arquitectura es poder cambiar el transporte sin poner reglas en la UI; no construir una abstracción de red ilimitada ni posponer campaña por infraestructura remota.

## Instalación de referencia y continuidad

Archivo identificado: [Fallout2_clean_Windows11.rar](https://drive.google.com/file/d/1G8uAAZ_QIiF9XYQ1dAJrp40s-N4LA8BS/view?usp=drivesdk), ID `1G8uAAZ_QIiF9XYQ1dAJrp40s-N4LA8BS`, tamaño 741208238 bytes. [Ficha original](https://docs.google.com/document/d/1ZiYsI4iWl9E-ksE71BQoTC_dA9CD5sk2jTyKeWrotxU): ISO, Windows 11, instalación declarada limpia, versión «1.02d + 1.02.31», significado del segundo componente pendiente. Metadatos confirmados; intento de fetch autenticado devuelve 413. No se descargó, extrajo, hasheó ni ejecutó el archivo; no se inventa manifest de su contenido.

NEXT: A2 con datos privados y revisiones fijadas. Resolver transferencia soportada del archivo grande; si el conector sigue sin permitirla, pedir exclusivamente los archivos necesarios o una transferencia dividida, con explicación concreta. En paralelo se pueden preparar herramientas de inspección/compilación, sin afirmar un arranque con datos ausentes. Después A3 fases, A4 comparación acotada CE/FOnline y A5 arte integrado. El actual C sólo es baseline rechazado, no motor seleccionado por inercia.
