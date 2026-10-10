# Plan de asimilación de Fallout 2

Estado: A1_CONTRACT_DEFINED / A2_PENDING, 2026-10-09 Argentina. Dirección autorizó comenzar la asimilación orientada a motor productivo, campaña individual primero y online en un orden posterior. A1 documental y auditoría baseline ejecutados; gates A2–A5 pendientes. Motor productivo todavía no seleccionado.

## Objetivo

Comprender y comprobar cómo Fallout 2 hace funcionar un espacio recorrible con acciones, objetos, visor y animaciones, y decidir qué base conviene para VampiroCRPG. Mantener Nueva York y la dirección artística de Vampiro como destino. La muestra 02 está rechazada y sus fallas quedan abiertas. No sumar más contenido mientras evaluamos la base.

La unidad de trabajo es un comportamiento completo, con entrada visible y consecuencia verificable. Recuperar más archivos sin cambiar nuestra comprensión no cierra una fase.

## A1 — Contrato espacial a partir de las fuentes — CERRADO A NIVEL DE CONTRATO

Entrega: [contrato espacial reconciliado](../../docs/FALLOUT_ASSIMILATION_A1_SPATIAL_CONTRACT.md), [adaptación de motor/reglas y online futuro](../../docs/VAMPIRO_ENGINE_ADAPTATION_SINGLEPLAYER_01.md), [auditor ejecutado](A1_BASELINE_AUDIT_2026-10-09.json) y [12 casos previstos para A2](A2_ACCEPTANCE_CASES_01.json). Las tres fallas siguen reproducidas; cierre A1 no significa corrección ni aceptación del runtime.

**Trabajo:** extraer de RE/CE las relaciones mínimas entre identidad de objeto, celda/elevación, flags/huella, proyección, selección, ruta y acercamiento. Construir un documento de contrato para nuestro mismo pasaje. Cruzar las tres fallas ya comprobadas: caja decorativa transitable, diagonales con duración uniforme y reinicio de progreso al cambiar destino.

**Entrega:** tabla de autoridad/representación, estados de puerta y reglas de interrupción; trazas esperadas para los recorridos de A2. Marcar comportamiento observado en fuente frente a política nueva. No copiar implementaciones externas.

**Cierre:** ninguna pieza volumétrica visible del pasaje queda sin decisión explícita de bloqueo; distancia/velocidad se definen en coordenadas del mundo; redirección tiene posición continua e intención inequívoca; se especifica el efecto sobre partidas antiguas antes de cambiar mapa o esquema.

**Límite:** una extracción y una revisión por contradicciones concretas. Si faltan datos del original, registrarlos para A2 en lugar de improvisar.

## A2 — Laboratorio ejecutable de referencia — NEXT

Referencia privada ya identificada en Drive: `Fallout2_clean_Windows11.rar`, ID `1G8uAAZ_QIiF9XYQ1dAJrp40s-N4LA8BS`, 741208238 bytes. Ficha: ISO/Windows 11, versión declarada 1.02d + 1.02.31 todavía no inspeccionada. Fetch autenticado devuelve 413; resolver transferencia soportada antes de afirmar ejecución. No pedir al usuario localizar otra copia ni tratarlo como material ausente.

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
