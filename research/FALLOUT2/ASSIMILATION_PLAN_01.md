# Plan de asimilación de Fallout 2

Estado: A1_CONTRACT_DEFINED / A2_REFERENCE_PARTIALLY_OBSERVED, 2026-10-10. Dirección autorizó asimilación para campaña individual de Nueva York y online posterior. CE compilado/ejecutado; geometría, bloqueo, redirección, puerta/acceso, selección/armario y recogida/propiedad con cobertura parcial medida. Ningún caso completo A2 aceptado para Vampiro; gates A3–A5 pendientes. Motor productivo todavía no seleccionado.

## Objetivo

Comprender y comprobar cómo Fallout 2 hace funcionar un espacio recorrible con acciones, objetos, visor y animaciones, y decidir qué base conviene para VampiroCRPG. Mantener Nueva York y la dirección artística de Vampiro como destino. La muestra 02 está rechazada y sus fallas quedan abiertas. No sumar más contenido mientras evaluamos la base.

La unidad de trabajo es un comportamiento completo, con entrada visible y consecuencia verificable. Recuperar más archivos sin cambiar nuestra comprensión no cierra una fase.

## Modalidad de trabajo por paquetes — dirección 2026-10-10

Agrupar ensayos relacionados y avanzar de forma autónoma durante la sesión hasta un resultado de subsistema revisable, sin devolver un NEXT por cada sonda. Mantener checkpoints y commits pequeños comprobados dentro del paquete; resumir a dirección el resultado conjunto, sus límites y la próxima unidad. Avisos breves de progreso no requieren intervención. Solicitar criterio sólo por una decisión concreta de diseño o un bloqueo que dirección deba resolver. No implica ejecución en segundo plano al terminar el turno.

**Plan del paquete de recogida, histórico y ejecutado en alcance CE:** La primera tarea sigue siendo el NEXT vigente: reconciliar action_frame4 y primera propiedad observada7 mediante lectura de la cola/delays/callbacks en DENBUS1. Si queda suficientemente identificado el límite de efecto, continuar con cancelación durante el gesto y después del efecto, repetición física por UI y guardado/carga en límites que el runtime permita alcanzar normalmente. Si una precondición no se cumple, probar una hipótesis discriminante antes de repetir; no forzar estado, marcadores, tiempos ni partida para conseguir el resultado esperado.

**Cierre del paquete:** entregar una matriz de esos escenarios con entradas, estado de suelo/propietario/cantidad antes y después, identidad exacta de fuentes/datos y evidencia reproducible; cada escenario debe tener resultado medido o bloqueo concreto documentado. Explicar el orden entre gesto y transferencia o dejar la causa precisa UNVERIFIED. Guardado/carga debe compararse con ejecución sin interrupción donde sea practicable. Un clic físico no prueba replay de recibos/identidad de acción; ese contrato de adaptación sigue separado. Un bloqueo no equivale a completar el escenario ni A2-08 entero.

**Control de errores:** observadores de sólo lectura, originales privados conservados, outputs nuevos, gates de precondición y checks afectados antes de encadenar experimentos. Conservar fallos y desacuerdos; validar regresiones pertinentes, hashes y publicación antes de sincronizar. No acumular modificaciones del motor sin revisar ni introducir nuevas reglas/arte para compensar una diferencia de referencia. Este paquete investiga CE; no implementa A3–A5 ni cambia el motor o la aceptación de Vampiro.

## A1 — Contrato espacial a partir de las fuentes — CERRADO A NIVEL DE CONTRATO

Entrega: [contrato espacial reconciliado](../../docs/FALLOUT_ASSIMILATION_A1_SPATIAL_CONTRACT.md), [adaptación de motor/reglas y online futuro](../../docs/VAMPIRO_ENGINE_ADAPTATION_SINGLEPLAYER_01.md), [auditor ejecutado](A1_BASELINE_AUDIT_2026-10-09.json) y [12 casos previstos para A2](A2_ACCEPTANCE_CASES_01.json). Las tres fallas siguen reproducidas; cierre A1 no significa corrección ni aceptación del runtime.

**Trabajo:** extraer de RE/CE las relaciones mínimas entre identidad de objeto, celda/elevación, flags/huella, proyección, selección, ruta y acercamiento. Construir un documento de contrato para nuestro mismo pasaje. Cruzar las tres fallas ya comprobadas: caja decorativa transitable, diagonales con duración uniforme y reinicio de progreso al cambiar destino.

**Entrega:** tabla de autoridad/representación, estados de puerta y reglas de interrupción; trazas esperadas para los recorridos de A2. Marcar comportamiento observado en fuente frente a política nueva. No copiar implementaciones externas.

**Cierre:** ninguna pieza volumétrica visible del pasaje queda sin decisión explícita de bloqueo; distancia/velocidad se definen en coordenadas del mundo; redirección tiene posición continua e intención inequívoca; se especifica el efecto sobre partidas antiguas antes de cambiar mapa o esquema.

**Límite:** una extracción y una revisión por contradicciones concretas. Si faltan datos del original, registrarlos para A2 en lugar de improvisar.

## A2 — Laboratorio ejecutable de referencia — NEXT

**Paquete espacial vigente cerrado en alcance medido 2026-10-10:** [informe](CE_SPATIAL_2026-10-10.md), [evidencia](CE_SPATIAL_2026-10-10.json). Siete arranques/575 poses nativas, 138 ensayos de cursor: 65 superposiciones opacas frontales, 70 supresiones por techo y 103 puntos egg. Perímetro del poste en ambos sentidos; pared con vecinos bloqueados/inaccesibles; armario seleccionado pero sin efecto con acceso cerrado, panel correcto a contacto1 después de abrir/entrar. Revelación de armario oculto por techo repetida dos veces: discrepancia CE con percepción prevista para Vampiro. Omisión de un tramo del log contrastada con recibos nativos y repetición independiente; causa del logger sin verificar. 83 tests/siete guards PASS. A2-01/02/03/05/06/07/08/09/10 parciales, tres casos sin ejecutar; todo Vampiro sin verificar. NEXT: Paquete de persistencia durante movimiento: guardar/cargar por UI original al caminar/correr y con una redirección pendiente; comparar posición, intención/cola, pose y continuación con controles sin carga. Registrar cancelación o reanudación efectiva, sin imponer persistencia de fases a CE ni cambiar originales. Cerrar alcance A2-09 con evidencias y límites concretos; motor/VTM/arte siguen abiertos.

**Checkpoint histórico cerrado en alcance medido 2026-10-10 — ciclo de recogida:** [informe](CE_PICKUP_CYCLE_2026-10-10.md), [evidencia](CE_PICKUP_CYCLE_2026-10-10.json). Ocho arranques/526 registros: dos delays sucesivos en cola reconcilian marcador4/primera propiedad7; cancelación temprana press1/release2 deja suelo, ensayo tardío release7 ya adquirido, petición postefecto y repetición física conservan cantidad1. Guardar/cargar antes/después/durante gesto conserva posición/propiedad medidas; durante gesto, save elimina la acción pendiente y carga no la reanuda. 66 tests/seis guards PASS; baselines exactos conservados. A2-01/02/03/05/06/08/09 parciales, cinco otros sin ejecutar; nada aceptado para Vampiro. NEXT: Paquete espacial de referencia: identificar en un mapa original objetos superpuestos u ocultos y un contacto separado por muro; medir selección/visor, oclusión al recorrer perímetros y acercamiento/negativa de interacción, con capturas y estado nativo. Cerrar una matriz de escenarios A2-06/07/10 con evidencia reproducible o bloqueos concretos. Conservar baselines, no modificar MAP/activos ni elegir motor o integrar reglas para compensar diferencias.

**Checkpoint histórico 2026-10-10 — primera recogida/propiedad:** [pickup CE medido](CE_PICKUP_2026-10-10.md), [evidencia](CE_PICKUP_2026-10-10.json). Fixture original DENBUS1 sin edición: objeto200/pid4 en suelo, entrada real13292 frente a header23895. Dos arranques/132 registros; selección, acercamiento/gesto, un slot propiedadavatar; cancelar acercamiento conserva suelo y reintento con pulsación adicional recoge. Fallo previo conservado, causa UI sin verificar. Marcador FRM4 frente a primera propiedad observada7: contacto/cola sin reconciliar. 54 tests/cinco guards PASS. A2-01/02/03/05/06/08 parciales; seis otros sin ejecutar, todo Vampiro sin verificar. NEXT: Reconciliar el marcador de recogida: observar de sólo lectura la secuencia de animación y sus delays/callbacks durante el mismo pickup de DENBUS1; ubicar sonido/CONTINUE y callback de propiedad respecto de frames4–8. Cerrar con una traza que explique el orden observado o deje la causa concreta sin verificar. No cambiar upstream, activos, reloj, saves ni contrato de adaptación para hacer coincidir el resultado.

**Checkpoint histórico de contenedor/selección 2026-10-10:** [interacción CE medida](CE_CONTAINER_2026-10-10.md), [evidencia](CE_CONTAINER_2026-10-10.json). Tres arranques: bloqueo14499, apertura vacía14497 y redirección durante acercamiento que evita abrir. Selección/visor/gesto y objetivo nativo de inventario registrados; sin transferencia. 328 registros totales/47 interacción, fuentes/DAT conservados, 44 tests y cuatro guards PASS. A2-01/02/03/05/06 parciales; siete casos sin ejecutar, todo Vampiro sin verificar. NEXT: A2-08: identificar un objeto portátil único y alcanzable por prototipo/selección nativa; medir uso desde suelo, gesto/contacto, propietario e inventario antes/después, cancelación antes del efecto y repetición cuando sea practicable. Cerrar sólo cobertura medida; no fabricar transferencia desde un armario vacío ni escribir estado autoritativo. A2-05 completo y persistencia permanecen pendientes.

**Checkpoint histórico de puerta/acceso 2026-10-10:** [puerta/acceso CE medidos](CE_DOOR_2026-10-10.md), [evidencia](CE_DOOR_2026-10-10.json). Tres arranques, 216 cambios de pose/estado, puerta seleccionada por UI, acercamiento/gesto, ocho frames y cruce al interior después de desaparecer el bloqueo. openFlags y frame final no bastan por sí solos para declarar pasabilidad. Un acercamiento interior al armario 14499 alcanza vecino 14500; uso/inventario pendiente. DAT/ELF locales truncados restaurados con hashes exactos antes de las corridas. 34 tests y guardas PASS. A2-01/02/03/05 parciales, ocho otros casos sin ejecutar, todo Vampiro sin verificar. NEXT: Medir interacción con el armario 14499 desde el interior alcanzable: seleccionar su arte por UI normal, observar visor, orientación/gesto, apertura/inventario y efecto; registrar antes/después e interrupción antes del efecto si es practicable. A2-05 permanece parcial: llave/bloqueo, contacto causal, cierre/repetición e interrupción siguen pendientes; persistencia después.

**Checkpoint de redirección 2026-10-10:** [redirección CE medida](CE_REDIRECTION_2026-10-10.md), [evidencia](CE_REDIRECTION_2026-10-10.json). Cinco escenarios con input durante offset parcial: redirección simple/doble, carrera al repetir destino, Escape/opciones/retorno y parada por casilla actual. 429 poses nativas; las redirecciones cambian frame/offset dentro de la misma casilla, sin demostrar nuestra política de continuidad C. Fuentes/ELF/DAT conservados, 25 pruebas de lectores/guardas PASS. A2-01/A2-02/A2-03 parciales; nueve casos sin ejecutar y todo Vampiro sin verificar. NEXT acotado: puerta/acceso alcanzable en NCR1, estado/bloqueador, UI normal, frames/flags/pasabilidad/cruce; contenedor accesible si ese acceso permite una prueba. No repetir waypoints fallidos ni cerrar A2-05 con sólo abrir una puerta.

**Checkpoint de cobertura de navegación 2026-10-10:** [geometría/bloqueo CE medidos](CE_NAVIGATION_2026-10-10.md), [evidencia](CE_NAVIGATION_2026-10-10.json). 21 solicitudes con selección nativa comprobada: seis vecinos/regresos; destinos libres y ocupados, acercamiento vecino y rodeo de poste. 53 observaciones nativas (inicial + 52 cambios), rutas coherentes y sin bloqueador en las casillas del actor observadas. El bloqueo del armario lo aporta scenery auxiliar; IDs aislados no son únicos. Tres DAT conservados; siete controles/rechazos y once tests de lectores PASS. A2-01/A2-02 parciales: no cerrar tiempos, contenedor accesible/perímetros o huella amplia. Otros diez casos sin ejecutar y todo Vampiro sin verificar. NEXT acotado A2-03: redirección durante movimiento, repetición/cancelación y continuidad medida; después puerta/acceso para contenedor, visor, contacto y persistencia.

**Checkpoint histórico de arranque 2026-10-10:** [CE ejecutado](CE_EXECUTABLE_LAB_2026-10-10.md), [evidencia](CE_EXECUTABLE_LAB_2026-10-10.json). CE e97087b9/fpattern 8523173 limpios compilados, datos privados inalterados. Tres carpetas nuevas alcanzan NCR1 (versión 20/índice 42/elevación 0); capturas y sonda nativa confirman movimiento 13915 → 14517. Arranque y configuración/overrides activos cerrados; doce casos completos A2 siguen pendientes. Laboratorio silencioso DAT-only no reproduce las DLLs/overrides Windows. NEXT acotado: A2-01/A2-02, seis direcciones y bloqueo de suelo/muro/contenedor/actor, con IDs, flags, ruta, estado antes/después y evidencia visual. No repetir transferencia ni preparar el entorno de nuevo.

**Checkpoint histórico de entrada, antes del arranque:** [recuperación y mapa](MASTER_RECOVERY_AND_MAP_AUDIT_2026-10-10.md), [evidencia](MASTER_RECOVERY_AND_MAP_AUDIT_2026-10-10.json). Dos RAR descargados, master.dat reconstruido de 333177805 bytes, SHA256 9b096d3035edafd4077deeb8ee7877a803b9db98497aa4596624b5c058a84711. Las 23140 entradas leídas/validadas; NCR1 base/parche consumidos hasta EOF, 32 puertas y 1098 referencias existentes por versión. Once tests sintéticos PASS; no ejecución de EXE/CE ni caso A2 conductual. Transferencia cerrada entonces; arranque CE ya verificado arriba. No pedir más partes ni otra instalación.

**Avance inicial, histórico:** [inspección](INSTALLATION_INSPECTION_2026-10-10.md) y [evidencia](INSTALLATION_INSPECTION_2026-10-10.json): quince descargas con SHA256; sfall 2.19a/Hi-Res 4.1.8.0 identificados; tres DAT, 7.786 entradas y 224.382 registros de cuadros comprobados; cabeceras de quince mapas/tres prototipos. La descarga directa del master devolvió 413; este bloqueo fue resuelto por los volúmenes recibidos después. Los doce casos permanecen NOT_EXECUTED.

Antecedente de transferencia: `Fallout2_clean_Windows11.rar`, ID `1G8uAAZ_QIiF9XYQ1dAJrp40s-N4LA8BS`, 741208238 bytes, devuelve 413 y no se descargó. Su bloqueo queda superado para inspección por la carpeta descomprimida. La ficha declaraba ISO/Windows 11, 1.02d + 1.02.31: la lectura nueva identifica sfall/Hi-Res pero mantiene sin resolver el segundo número y la versión exacta del EXE. No pedir al usuario localizar otra copia ni tratarlo como material ausente.

**Trabajo:** fijar una revisión CE y una instalación legítima disponible; registrar versión y hashes de recursos de entrada. Comparar con RE sólo cuando una diferencia CE pueda afectar el contrato. Escena mínima: avatar, muro, caja/contenedor, puerta, objeto y un contacto. Primero medir el comportamiento del juego, luego considerar un mapa propio editable.

**Herramientas mínimas:** runtime CE; extracción DAT y visor de cuadros cuando hagan falta. Evaluar Gecko o Mapper para el único mapa. SSLC sólo si el caso necesita un script. No instalar todo el ecosistema ni modificar la instalación original del usuario.

**Cierre:** arranque reproducible; capturas o video de movimiento, bloqueo, selección/visor, puerta y acción; traza de estado antes/después. Comprobar acercamiento imposible, objeto que cambia mientras el actor se acerca y redirección durante movimiento. Aclarar qué es comportamiento clásico y qué es CE.

**Bloqueo real:** si no hay datos legítimos disponibles, informar los archivos concretos necesarios. No obtener DAT/arte de mirrors ni declarar funcionamiento con sólo compilar el ejecutable.

**Límite:** un intento de configuración y hasta dos correcciones sustentadas en errores nuevos. Si la cadena de herramientas se vuelve el problema, registrar costo y evaluar la segunda base, sin repetir el mismo intento.

## A3 — Interacción y persistencia de fases

**Trabajo:** observar recoger/usar y el marcador de acción, interrupción, repetición y guardado. Formular para nuestra autoridad: intención → acercamiento → orientación → contacto → efecto único → finalización. Separar momento causal del FPS de presentación y decidir qué fases se persisten.

**Cierre:** cancelar antes del efecto no adquiere el objeto; después del efecto no lo devuelve ni lo duplica; petición repetida conserva resultado único; guardar/cargar no teletransporta ni repite efecto; puerta y contacto no producen acciones a través de un muro.

**Reconciliación:** preservar el núcleo A/B ya medido; no asumir que callbacks originales son un esquema de persistencia suficiente para hambre, Bestia o procesos fuera de mapa.

## A4 — Comparación técnica acotada

Comparar CE adaptado y FOnline actual en la misma microescena y con recursos propios sencillos. La implementación actual sólo sirve como referencia de lo que falla; no es una candidata aceptada por inercia. Introducir otra alternativa moderna únicamente si ambas presentan un impedimento material.

| Criterio | Evidencia necesaria |
| --- | --- |
| Arranque y mantenimiento | Construcción reproducible, herramientas necesarias, pasos manuales y fallos pendientes. |
| Espacio e interacción | Los mismos recorridos y contactos de A2/A3 sin inconsistencias visibles. |
| Editor y producción | Editar posición/huella de una pieza y verla funcionar en el runtime. |
| Ropa y arma visibles | Dos siluetas distintas; dos armas de la misma clase, diferenciadas en icono y mano desde fuente propia. |
| Animación ampliable | Un rig o catálogo editado produce caminar e interactuar sin rehacer el resto del escenario. |
| Simulación vampírica | Frontera concreta para comandos/eventos y persistencia del núcleo; no una afirmación de compatibilidad abstracta. |
| Juego individual | Inicio offline, pausa/guardado y cierre local; en FOnline, medir transporte interthread existente y el costo de autoridad/cliente locales. No exigir administración de servidor al jugador. |
| Distribución | Licencias exactas y dependencias conocidas; motor, herramientas y contenido separados. |
| Equipo del usuario | Medición en su Windows y hardware confirmado cuando exista paquete; no inferir GPU ni FPS. |

**Cierre:** recomendación con evidencias y costos observados; no porcentajes de ahorro ni cronogramas inventados. El motor no se elige porque tenga la lista de funciones más larga.

## A5 — Prueba artística integrada

Sólo después de la base coherente: un tramo corto de Nueva York y un personaje con el acabado aprobado, dentro del runtime, con movimiento e interacción. Mantener piezas editables, dirección de cámara/luz, escala y anclajes. Evaluar alrededor de obstáculos y a velocidad normal, además de fotogramas aislados.

**Cierre:** dirección juzga esa muestra concreta. Una ilustración estática o un atlas técnicamente válido no sirven como aprobación artística. Si el método vuelve a producir un resultado muy inferior, revisar creación de arte y necesidad de un artista; no multiplicar escenarios para ocultar el problema.

## Lo que puede aprovecharse y lo que se conserva pendiente

**Aprovechar como mecanismos:** geometría explícita, identidad compartida entre navegación y dibujo, prototipos/instancias, acercamiento, secuencias/marcadores, equipo ligado a apariencia, scripts/eventos y disciplina de persistencia.

**Reconciliar con Vampiro:** atributos y resolución d10, alimentación/Bestia, coste de poderes, iniciativa, acción social, consecuencias diurnas, conocimiento por actor/institución y procesos que sobreviven a descarga de ubicaciones.

**Online futuro:** requisito autorizado de orden posterior; conservar fronteras de autoridad, comandos, IDs, vistas por actor y persistencia. Modalidad concreta no definida; no iniciar hosting ni cuentas.

**Pendiente de expansión:** combate completo, catálogo de ropa/armas, varias ciudades, vehículos, clima y animaciones conjuntas complejas. Se mantienen como requisitos de diseño, sin afirmar que Fallout o FOnline los resuelven todos.

## Registro y continuidad

Cada gate cierra con DONE/EVIDENCE/OPEN/NEXT. El master conserva la fase activa; estos documentos guardan los detalles. Dirección no necesita leer controles: se le pide criterio cuando exista una experiencia o alternativa concreta que deba evaluar. Los gates posteriores sólo se abren con nueva evidencia.

Referencias: [inventario](RESEARCH_SURVEY_2026-10-09.md), [hallazgos](SPATIAL_ART_ANIMATION_FINDINGS_01.md), [manifiesto](SOURCE_INVENTORY_2026-10-09.json), [matriz](SYSTEM_MATRIX.md), [corrección de timers](QUEUE_LIFETIME_CORRECTION.md).
