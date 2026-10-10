# Animación e interacciones — base ampliable 01

Estado: adopción parcial en la muestra recorrible 02. IMPLEMENTED: fuentes editables separadas del exportador, catálogo idle/walk/pickup, ocho direcciones y gesto de recoger. NOT_IMPLEMENTED: sincronización general entre actores, marcadores, combate, ropa intercambiable, armas, vehículos y clima. Muestra 02 RECHAZADA por dirección por un desfasaje artístico muy grande y problemas de coherencia espacial. Las capacidades implementadas enumeradas aquí no acreditan aceptación. Ver [estado vigente](TECHNICAL_STATE.md).

## Dirección vigente

Primer juego en Nueva York, tomando New York by Night como referencia local. Dirección aprobó las referencias conceptuales por su acabado y precisó una noche seductora y hostil: peligro, clandestinidad, sordidez y variedad de aseo, vestuario, cansancio e intoxicación.

El juego deberá tener combate por turnos y diversas animaciones e interacciones entre personas y objetos, y entre personas. Vehículos y eventos climáticos forman parte del horizonte de expansión. Contemplarlos no significa implementarlos todos en el pasaje inicial.

## Punto de partida comprobado

C separa autoridad Python y presentación canvas. Actualmente ofrece desplazamiento, inspección, llave, puerta, umbral e inventario. A/B contiene reglas vampíricas todavía no integradas al recorrido.

El avatar tiene idle (1), walk (8) y pickup (10) en ocho direcciones. El renderer elige columnas y duración desde los metadatos del clip. El contacto usa una pose estática. Recoger es un gesto visual disparado por la adquisición confirmada; no implementa fases lógicas cronometradas ni una acción conjunta.

La fuente anatómica incorpora prendas separadas y esqueleto compartido. build_ny_source.py crea las fuentes; export_ny.py reexporta los materiales, geometría y poses guardados sin reconstruirlos. La variante de abrigo se obtiene editando su material en la fuente. Reejecutar el constructor sí reemplaza fuentes: usar sólo el exportador para conservar cambios manuales.

## Recursos por acciones

Proponer un catálogo de clips con identificadores estables: reposo, caminar, recoger, manipular puerta y reacción conversacional para el primer conjunto. Ataque, recibir impacto, esquiva, caída y alimentación se producirán al integrar sus reglas.

Cada clip declara duración, repetición, orientaciones disponibles, cuadros o región del atlas, anclaje al suelo y marcadores visuales. Evitar que la cantidad de cuadros o la acción activa se deduzca de posiciones fijas dentro de una hoja. Resolver dirección y clip por metadatos.

La fuente debe conservar proporciones, esqueleto/articulaciones, materiales, vestuario y poses. Exportar todas las acciones desde esa misma fuente, con cámara y escala comunes. Añadir vestuario o suciedad puede requerir recursos específicos; no afirmar que cualquier ropa se deforma correctamente con un único rig.

Primera adopción implementada: fuente Blender editable + clips nombrados + exportador independiente. Ver assets/walk/source/NY_README.md y proof/walk/README.md. Tecnología de producción permanece sin decidir; esta base no prueba todavía el acabado artístico de la referencia.

## Autoridad y reproducción

Una acción lógica identifica actor, objetivo, acción, posición/orientación pertinente y resultado. La presentación elige y reproduce el clip correspondiente. Los marcadores sincronizan sonido, contacto o efectos visuales; no deciden por sí solos daño, adquisición de objetos, sangre ni éxito.

Las reglas deberán validar coste, alcance, permisos y condiciones, y resolver consecuencias una sola vez. Una animación interrumpida, repetida o saltada no debe duplicar efectos. El ritmo de render y la velocidad del equipo no deben cambiar el resultado.

El combate por turnos necesitará estado de turno, acciones permitidas, costes y orden explícitos. El reloj de exploración existente no es ya un sistema de turnos. Política del tiempo del mundo durante combate, economía de acciones y transición exploración/combate: NEEDS_DECISION en su especificación posterior.

Guardar/cargar durante una acción conjunta o turno deberá conservar el estado lógico y la fase necesaria para reanudar. Cualquier cambio a los esquemas actuales requiere su contrato de versión y migración antes de implementarlo.

## Interacciones entre personas y con objetos

Una interacción conjunta requiere roles de actor y objetivo, puntos de contacto, alcance y fases compatibles: aproximación, preparación, acción, reacción y cierre/cancelación según el caso. Conversar, dar un objeto, sujetar o alimentarse pueden compartir estructura sin compartir permisos o reglas.

La sincronización usa una acción identificada y tiempos definidos, no dos animaciones iniciadas independientemente. Conservar ubicación física, selección y orden de dibujo por profundidad. Objetos como una puerta pueden tener estados y animaciones propias.

Aseo, desgaste e intoxicación visuales son dimensiones distintas de la conducta y la mecánica. Definir sus efectos sistémicos sólo cuando el diseño los requiera; no derivarlos automáticamente de una textura.

## Equipo visible e identidad de los ítems

Requisito de dirección: intercambiar ropa y armaduras debe cambiar la apariencia del personaje. Un arma utilizada o sostenida debe coincidir lo más fielmente posible con su representación en inventario. REQUISITO REGISTRADO; equipamiento visual general y armas todavía NOT_IMPLEMENTED.

Proponer una definición estable de ítem que relacione su diseño visual de referencia, fuente editable, materiales y variantes con icono, representación en el suelo y representación equipada. Conservar forma, proporciones características, color, componentes y estado relevante entre vistas, aunque su escala e iluminación sean distintas. El icono puede exportarse de la misma fuente con cámara de inventario; no diseñar por separado dos armas que sólo compartan nombre.

Separar posesión, equipo asignado y modo de uso. Un arma transportada puede estar guardada; al empuñarla y actuar, el recurso mostrado debe corresponder a ese ítem. Estos estados deberán persistirse en su futura especificación; el inventario de una sola llave en C no tiene ya slots ni empuñado.

Ropa y armaduras requieren piezas o conjuntos compatibles con el cuerpo, con cambios de silueta cuando corresponda, además de color y textura. Definir zonas ocupadas, capas, piezas cubiertas y combinaciones admitidas; verificar intersecciones y deformación al moverse. Un abrigo, una chaqueta y una armadura no se resuelven todos recoloreando el torso.

Las armas necesitan puntos de agarre, posición/orientación y restricciones de una o dos manos, más familias de poses o clips adecuados. La misma pistola, cuchillo u objeto puede compartir fuente entre vistas; sostenerlos puede requerir movimientos diferentes. Los detalles exactos se fijarán al especificar cada familia y sus reglas. Mostrar un arma no implementa aún su ataque o daño.

Estrategia de exportación: evaluar conjuntos equipados prerenderizados desde la fuente común y/o capas compatibles con profundidad controlada. No prometer combinaciones arbitrarias gratuitas ni multiplicar todos los clips por todas las prendas sin medir coste. NEEDS_DECISION técnico cuando exista un personaje fuente y un conjunto reducido real para comparar memoria, generación, calidad y oclusión.

Prueba posterior acotada: dos vestuarios con diferencia de silueta, un equipo de protección y un arma representada tanto en inventario como en mano, en orientaciones y acciones pertinentes. Comprobar identidad visual, agarre, ausencia de intersecciones, cambio de equipo y continuidad al guardar/cargar cuando existan esas reglas. Es una ampliación de validación posterior a la base del pasaje; no declara nuevas capacidades del paquete actual.

## Vehículos y clima

Vehículos: reservar soporte conceptual para entidades de varias celdas, orientación, ocupantes, interacción de entrada/salida y condiciones propias de movimiento. Esto demandará rutas y colisiones para su tamaño. No representar un vehículo funcional sólo ampliando el sprite humano. Conducción directa o transporte entre lugares: NEEDS_DECISION futuro.

Clima: separar estado del tiempo y efectos de presentación. Lluvia, viento o niebla pueden cambiar partículas, sonido, materiales y visibilidad visual; modificar percepción, desplazamiento u otras reglas requiere condiciones explícitas de simulación. Evitar que ruido gráfico o FPS determinen consecuencias. Clima y variantes ambientales todavía no implementados.

## Muestra 02 y criterios de cierre

La muestra 02 mantiene mapa y autoridad, integra caminata y recoger, personaje/NPC con vestuario y postura diferenciados, fachadas y entorno independientes. La puerta conserva dos estados gráficos. El acabado fue rechazado por dirección como muy inferior a la ilustración conceptual aprobada. La base de producción artística sigue sin demostrarse; superar pruebas automáticas no resuelve ese rechazo.

Verificar: fuente editada se reexporta conservando cambios; identidad, escala y anclajes coherentes entre clips/direcciones; reproducción, pausa/carga e interrupción no duplican consecuencias; navegación, selección y profundidad siguen funcionando; el usuario valora el acabado real en movimiento. Ejecutar regresiones pertinentes cuando cambie runtime.

Vehículos, clima y catálogo completo de combate no son criterios de cierre de esta primera muestra. Se amplían después de validar la base. No introducir dependencias mayores, nuevo motor o cambios de saves mediante esta nota.
