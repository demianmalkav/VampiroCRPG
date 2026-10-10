# Animación e interacciones — base ampliable 01

Estado: requisitos de dirección registrados; diseño técnico propuesto para la siguiente muestra. NOT_IMPLEMENTED. El runtime C verificado no cambia con este documento.

## Dirección vigente

Primer juego en Nueva York, tomando New York by Night como referencia local. Dirección aprobó las referencias conceptuales por su acabado y precisó una noche seductora y hostil: peligro, clandestinidad, sordidez y variedad de aseo, vestuario, cansancio e intoxicación.

El juego deberá tener combate por turnos y diversas animaciones e interacciones entre personas y objetos, y entre personas. Vehículos y eventos climáticos forman parte del horizonte de expansión. Contemplarlos no significa implementarlos todos en el pasaje inicial.

## Punto de partida comprobado

C separa autoridad Python y presentación canvas. Actualmente ofrece desplazamiento, inspección, llave, puerta, umbral e inventario. A/B contiene reglas vampíricas todavía no integradas al recorrido.

El avatar sólo tiene idle y caminata en ocho direcciones. El renderer calcula una columna de reposo o una de ocho cuadros de marcha; no existe un reproductor general de acciones. El contacto usa una pose estática.

La receta Blender reconstruye geometría elemental y guarda .blend de salida. Los archivos se pueden editar, pero volver a ejecutar esa receta no reexporta esas ediciones: los reconstruye. Para arte detallado debemos separar creación del modelo y exportación de una fuente editada.

## Recursos por acciones

Proponer un catálogo de clips con identificadores estables: reposo, caminar, recoger, manipular puerta y reacción conversacional para el primer conjunto. Ataque, recibir impacto, esquiva, caída y alimentación se producirán al integrar sus reglas.

Cada clip declara duración, repetición, orientaciones disponibles, cuadros o región del atlas, anclaje al suelo y marcadores visuales. Evitar que la cantidad de cuadros o la acción activa se deduzca de posiciones fijas dentro de una hoja. Resolver dirección y clip por metadatos.

La fuente debe conservar proporciones, esqueleto/articulaciones, materiales, vestuario y poses. Exportar todas las acciones desde esa misma fuente, con cámara y escala comunes. Añadir vestuario o suciedad puede requerir recursos específicos; no afirmar que cualquier ropa se deforma correctamente con un único rig.

Primera adopción propuesta: fuente Blender editada + clips nombrados + exportador independiente. El rig detallado, los nuevos clips y el exportador aún no existen. Tecnología de producción permanece sin decidir.

## Autoridad y reproducción

Una acción lógica identifica actor, objetivo, acción, posición/orientación pertinente y resultado. La presentación elige y reproduce el clip correspondiente. Los marcadores sincronizan sonido, contacto o efectos visuales; no deciden por sí solos daño, adquisición de objetos, sangre ni éxito.

Las reglas deberán validar coste, alcance, permisos y condiciones, y resolver consecuencias una sola vez. Una animación interrumpida, repetida o saltada no debe duplicar efectos. El ritmo de render y la velocidad del equipo no deben cambiar el resultado.

El combate por turnos necesitará estado de turno, acciones permitidas, costes y orden explícitos. El reloj de exploración existente no es ya un sistema de turnos. Política del tiempo del mundo durante combate, economía de acciones y transición exploración/combate: NEEDS_DECISION en su especificación posterior.

Guardar/cargar durante una acción conjunta o turno deberá conservar el estado lógico y la fase necesaria para reanudar. Cualquier cambio a los esquemas actuales requiere su contrato de versión y migración antes de implementarlo.

## Interacciones entre personas y con objetos

Una interacción conjunta requiere roles de actor y objetivo, puntos de contacto, alcance y fases compatibles: aproximación, preparación, acción, reacción y cierre/cancelación según el caso. Conversar, dar un objeto, sujetar o alimentarse pueden compartir estructura sin compartir permisos o reglas.

La sincronización usa una acción identificada y tiempos definidos, no dos animaciones iniciadas independientemente. Conservar ubicación física, selección y orden de dibujo por profundidad. Objetos como una puerta pueden tener estados y animaciones propias.

Aseo, desgaste e intoxicación visuales son dimensiones distintas de la conducta y la mecánica. Definir sus efectos sistémicos sólo cuando el diseño los requiera; no derivarlos automáticamente de una textura.

## Vehículos y clima

Vehículos: reservar soporte conceptual para entidades de varias celdas, orientación, ocupantes, interacción de entrada/salida y condiciones propias de movimiento. Esto demandará rutas y colisiones para su tamaño. No representar un vehículo funcional sólo ampliando el sprite humano. Conducción directa o transporte entre lugares: NEEDS_DECISION futuro.

Clima: separar estado del tiempo y efectos de presentación. Lluvia, viento o niebla pueden cambiar partículas, sonido, materiales y visibilidad visual; modificar percepción, desplazamiento u otras reglas requiere condiciones explícitas de simulación. Evitar que ruido gráfico o FPS determinen consecuencias. Clima y variantes ambientales todavía no implementados.

## Próxima muestra y criterios de cierre

Mantener el pasaje y sus interacciones conocidas. Construir una fuente de personaje con el acabado buscado, caminata en ocho direcciones y al menos una acción adicional integrada —recoger o manipular la puerta— que demuestre el catálogo y su sincronización. Contacto con apariencia/postura diferenciada, arquitectura neoyorquina y recursos de entorno separados.

Verificar: fuente editada se reexporta conservando cambios; identidad, escala y anclajes coherentes entre clips/direcciones; reproducción, pausa/carga e interrupción no duplican consecuencias; navegación, selección y profundidad siguen funcionando; el usuario valora el acabado real en movimiento. Ejecutar regresiones pertinentes cuando cambie runtime.

Vehículos, clima y catálogo completo de combate no son criterios de cierre de esta primera muestra. Se amplían después de validar la base. No introducir dependencias mayores, nuevo motor o cambios de saves mediante esta nota.
