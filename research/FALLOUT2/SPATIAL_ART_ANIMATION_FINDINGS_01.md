# Hallazgos: espacio, arte, animación e interacciones

Estado: SOURCE_OBSERVED / 2026-10-09 Argentina. Lectura dirigida; sin ejecución de Fallout 2 ni equivalencia binaria comprobada. Las conclusiones describen las revisiones enlazadas. Requisitos de VampiroCRPG proceden de dirección; las propuestas de adaptación son inferencias de ingeniería.

## F2-SPA-001 — Dos geometrías relacionadas

Fallout 2 usa una grilla hexagonal para posición/dirección de objetos y otra grilla de tiles para pisos y techos. Las conversiones están implementadas mediante funciones distintas: `tileToScreenXY`, `tileFromScreenXY`, `squareTileToScreenXY` y las variantes de techo. Los mapas distinguen elevaciones. No corresponde adoptar las ocho direcciones y la grilla cuadrada de nuestra muestra como si fueran equivalentes al modelo original.

Evidencia: [CE tile.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/tile.cc), funciones citadas; [MAP](https://github.com/rotators/fallout2-docs/blob/fa5b3a90b342975998f10e270c5cd7f5293af9e9/content/pages/map.md), coordenadas y elevaciones.

**Asimilación:** separar coordenada lógica, proyección y cobertura del recurso. Si elegimos otra grilla, especificar velocidades/distancias y coste por tramo. Un sprite voluminoso no adquiere colisión por ser grande.

**Prueba necesaria:** ida/vuelta de selección en suelo; recorrido por seis orientaciones de referencia; actor delante y detrás de un muro; equivalencia de distancias lógicas sin medir directamente píxeles de una proyección oblicua.

## F2-SPA-002 — Dibujo y navegación consultan instancias de objetos

En CE, `_obj_blocking_at` consulta objetos de la celda/elevación, su tipo y flags; examina además vecinos para objetos `OBJECT_MULTIHEX`. `_make_path` pasa esa consulta al buscador de rutas. El dibujo también recorre las listas de objetos por celda y elevación. Las ramas RE examinadas muestran el mismo vínculo básico entre `make_path_func` y `obj_blocking_at`.

Evidencia: [CE object.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/object.cc), `_obj_blocking_at`; [CE animation.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/animation.cc), `_make_path` y `pathfinderFindPath`; [RE anim.c](https://github.com/alexbatalov/fallout2-re/blob/b135fc46ef40c4aecd156f3cebcf88ec531bb8ac/src/game/anim.c), `make_path`.

Movimiento, disparo y paso de luz tienen condiciones distintas. `OBJECT_NO_BLOCK` no significa simplemente que el objeto sea invisible. `MULTIHEX` representa una extensión concreta a vecinos, no una forma arbitraria derivada de los píxeles.

**Asimilación:** una definición común debe vincular identidad, posición, huella y estado visual. No inferir que todos los objetos dibujados bloquean: el contenido decide flags y huellas coherentes. Nuestra caja decorativa [3,4] existe sólo en el renderizador y es transitable; ese desacople debe eliminarse.

**Prueba necesaria:** caja sólida, decoración atravesable deliberada, contenedor de varias celdas, puerta abierta/cerrada y personaje móvil; comprobar tanto ruta como ejecución, no sólo el plan inicial.

## F2-SPA-003 — Profundidad, techos y luz son subsistemas específicos

`_obj_render_pre_roof` separa objetos planos del resto y usa ordenación por celdas/elevación; existe una pasada posterior a techos. Se combina luz ambiente con intensidad de celda. `_obj_adjust_light` propaga intensidad según posiciones y bloqueos. No es equivalente a ordenar todas las piezas por la suma de dos coordenadas de su centro.

Evidencia: [CE object.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/object.cc), funciones citadas; [CE light.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/light.cc); [CE tile.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/tile.cc), pisos/techos.

**Asimilación:** conservar la distinción entre suelo, volumen y cubierta; hacer explícita la política de oclusión. La iluminación técnica ayuda a coherencia y atmósfera, pero no sustituye composición, materiales y diseño artístico.

**Prueba necesaria:** secuencia fija alrededor de un muro alto y un contenedor ancho; entrada bajo una cubierta; apagar/encender una fuente. Evaluación visible obligatoria.

## F2-SPA-004 — La selección enlaza cursor, objeto y visor

`gameMouseGetObjectUnderCursor` obtiene una lista de intersecciones, recorre candidatos y considera cubiertas/tipos. Al cambiar el objeto señalado se invoca `_obj_look_at`. En `proto_instance.cc`, mirar/examinar utiliza callbacks de script y dirige el texto al monitor mediante `displayMonitorAddMessage`. Esto reproduce la cadena concreta que dirección pidió: señalar algo del mundo y obtener una observación contextual.

Evidencia: [CE game_mouse.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/game_mouse.cc), funciones y cambio de objeto señalado; [CE proto_instance.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/proto_instance.cc), `_obj_look_at` y `_obj_examine`; [CE display_monitor.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/display_monitor.cc).

**Asimilación:** hit visual, identidad y observación deben concordar. Conservar en Vampiro el filtro de conocimiento/percepción por actor; la posibilidad de señalar un sprite no autoriza revelar todo su estado oculto.

**Prueba necesaria:** dos objetos solapados, pared con objeto detrás, personaje inspeccionado frente a suelo seleccionado, cambio de objetivo sin spam y texto sólo de lo percibido. No tratar un click sobre volumen como suelo automáticamente.

## F2-SPA-005 — La ejecución vuelve a comprobar el siguiente paso

`_object_move` aplica offsets del fotograma y, al cruzar una celda, consulta nuevamente `_obj_blocking_at`. Si aparece un obstáculo puede recalcular ruta o terminar; existe tratamiento específico para puertas. El movimiento observado no consiste únicamente en calcular una ruta una vez y reproducirla sin consultar el mundo.

Evidencia: [CE animation.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/animation.cc), `_object_move` y `animationComputeTicksPerFrame`.

**Asimilación:** validar ocupación durante ejecución e interrupción. Preservar continuidad lógica/visual sin suponer que la política original es una solución moderna universal. La respuesta exacta a redirección y guardado sigue pendiente de observación en runtime.

## F2-ART-001 — Los cuadros tienen anclajes y movimiento propios

La documentación FRM describe seis orientaciones, datos de paleta de 8 bits, FPS, un marcador `action_frame`, ajustes por orientación y deltas por cuadro. `art.cc` obtiene esas propiedades y `animation.cc` las aplica durante avance/reversa. Se recuperaron ambos archivos y se revisó el avance de animación.

Evidencia: [FRM](https://github.com/rotators/fallout2-docs/blob/fa5b3a90b342975998f10e270c5cd7f5293af9e9/content/pages/frm.md); [CE art.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/art.cc); [CE animation.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/animation.cc), `_object_animate`.

**Asimilación:** preservar anclaje, duración, desplazamiento y marcadores al importar/exportar. Nuestro PNG atlas y un clip que se reproduce no bastan para probar apoyo de pies, continuidad de posición o contacto. No fijar el formato FRM para producción antes de elegir runtime: la restricción de color puede ser inconveniente para el detalle deseado.

**Prueba necesaria:** un ciclo completo en cada orientación, cuadro a cuadro y en movimiento; comparar pies y desplazamiento; interrupción sin retroceso; recurso editado conserva metadatos.

## F2-ANI-001 — Las acciones forman secuencias

CE dispone de secuencias de movimiento, orientación, animación, sonido, cambio de FID, callbacks y continuación. Se registran entre `reg_anim_begin` y `reg_anim_end`. El planificador es de capacidad fija: 32 secuencias y 55 descripciones por secuencia en el archivo observado. Estos números son detalles heredados, no criterios para nuestro diseño.

Evidencia: [CE animation.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/animation.cc), `AnimationKind`, registros y ejecución; [RE anim.c](https://github.com/alexbatalov/fallout2-re/blob/b135fc46ef40c4aecd156f3cebcf88ec531bb8ac/src/game/anim.c).

**Asimilación:** representar intención, acercamiento, orientación, contacto, efecto y finalización como fases con cancelación definida. El motor original mezcla avance visual y mutaciones de mundo: hay que entender esa coordinación antes de decidir cómo conservarla en una autoridad determinista. No trasplantar punteros/callbacks como arquitectura propia.

## F2-ANI-002 — Recoger vincula proximidad y efecto a la animación

`actionPickUp` solicita acercamiento, comprueba adyacencia/coste, reproduce el gesto y registra `_obj_pickup` con el `actionFrame` del recurso. RE contiene una coordinación equivalente y registra `obj_pickup`; la lectura estática no demuestra un número de cuadro de efecto. Esto es evidencia de coordinación, no prueba de contacto geométrico exacto entre mano y objeto.

Actualización de ejecución 2026-10-10: [paquete CE](CE_PICKUP_CYCLE_2026-10-10.md), ocho arranques/526 observaciones, registra CONTINUE del sonido ausente y callback pickup con delays sucesivos derivados del marcador4. Primera propiedad observada7, sin instrumentación atómica. Guardar durante gesto limpia la acción pendiente y conserva suelo; carga no reanuda esa recogida. Esta medición acota cualquier interpretación literal anterior de «efecto en action_frame». Sigue sin equivalencia al Windows original ni aceptación de Vampiro.

Evidencia: [CE actions.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/actions.cc), `actionPickUp`; [RE actions.c](https://github.com/alexbatalov/fallout2-re/blob/b135fc46ef40c4aecd156f3cebcf88ec531bb8ac/src/game/actions.c), `action_get_an_object`.

**Diferencia actual:** nuestra llave cambia de propietario antes del gesto visual. Cambiar de destino puede cancelar la animación después de que la adquisición ya ocurrió. Eso no satisface por sí solo la interacción física esperada.

**Prueba necesaria:** detenerse antes del contacto, alcanzar el contacto, cancelar después, repetir la petición y guardar/reanudar en cada fase. Definir exactamente cuándo se transfiere la propiedad y conservar ese resultado una sola vez. No permitir que FPS del cliente determine la verdad del juego.

## F2-EQU-001 — Armadura y arma no usan composición libre de prendas

`_adjust_fid` selecciona un identificador de arte corporal según armadura y sexo y toma `animationCode` del arma de la mano activa. `buildFid` y `_art_get_code` combinan tipo de arte, base, animación, categoría de arma y orientación para resolver el recurso. El prototipo conserva también arte de inventario.

Evidencia: [CE inventory.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/inventory.cc), `_adjust_fid` y `_inven_wield`; [CE art.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/art.cc), `buildFid` y `_art_get_code`; [CE proto_types.h](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/proto_types.h).

**Conclusión:** existe correspondencia entre equipo y apariencia, pero el arma visible se selecciona mediante categoría de animación. No demuestra representación idéntica de cada modelo de arma del inventario ni capas combinables de ropa. Para nuestra exigencia de identidad por ítem habría que ampliar el modelo o usar una composición diferente.

**Coste artístico a medir:** por cada combinación de cuerpo/vestuario/categoría, recursos de orientaciones y acciones compatibles. No prometer combinaciones ilimitadas sin medir generación, revisión y almacenamiento.

**Prueba necesaria:** dos siluetas realmente distintas y dos armas de una misma categoría, con icono y mano distinguibles y coherentes desde una fuente propia común. Una recoloración no cierra el requisito.

## F2-EXT-001 — sfall demuestra expansión, con dependencias concretas

El `ddraw.ini` examinado documenta códigos adicionales de animación de armas, soporte Hero Appearance y límites ampliados de animación. Se localizaron un ejemplo de lluvia mediante shader y módulos de animación/arte. No se ejecutaron; lluvia localizada no equivale a clima que afecta navegación o simulación.

Evidencia: [configuración sfall](https://github.com/sfall-team/sfall/blob/6c65e67342bda1488671601e417194199ec72a09/artifacts/ddraw.ini); [Animations.cpp](https://github.com/sfall-team/sfall/blob/6c65e67342bda1488671601e417194199ec72a09/sfall/Modules/Animations.cpp); [ejemplo de lluvia](https://github.com/sfall-team/sfall/blob/6c65e67342bda1488671601e417194199ec72a09/artifacts/example_mods/rain/readme.txt).

**Asimilación:** anotar dependencia y versión de cada extensión. No heredar una función sfall suponiendo que existe en RE, CE o nuestro núcleo. Vehículos, clima y combate vampírico quedan requisitos futuros sin implementación demostrada.

## ALT-001 — FOnline merece comparación por composición de equipo

Se examinó el motor actual, no FOClassic. Su `Map::IsHexMovable` combina bloqueo estático/dinámico y existen comprobaciones por radio. Su documentación y `ModelInstance.cpp` muestran selección por capas, modelos hijos y enlaces a huesos. Las prendas pueden vincularse a huesos compartidos; un arma puede adjuntarse a una mano. El pipeline documenta FBX/OBJ y clips convertidos con metadatos de duración comunes.

Evidencia: [FOnline Map.cpp](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Source/Server/Map.cpp); [ModelInstance.cpp](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Source/Client/ModelInstance.cpp); [composición](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Docs/en/how-to/content/model-format.md); [duración](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/Docs/en/how-to/content/model-animation.md).

**Inferencia:** podría reducir el trabajo de equipo visible y animación reutilizable. Debemos medir el costo de servir un juego individual sobre una estructura de cliente/servidor, integrar turnos y adaptar nuestro núcleo. No se construyó, no se importó nuestro rig y no se comprobó el rendimiento en la notebook del usuario. El ejemplo ContentShowcase revisado omite deliberadamente modelos 3D: no usarlo como demostración visual de esta capacidad.

## Correcciones que siguen vigentes

- [Vida de la cola](QUEUE_LIFETIME_CORRECTION.md): guardar timers no implica conservarlos al salir de un mapa. La tabla `gEventTypeDescriptions` en [CE queue.cc](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/queue.cc) sigue marcando eventos de script para limpieza al salir. Procesos institucionales entre ubicaciones requieren otra política.
- [Economía táctica](TACTICAL_ACTION_ECONOMY.md): AP/Sequence y fórmulas de daño son Fallout, no reglas vampíricas ya adoptadas.
- No se concluye que el motor clásico proporcione física rígida general, conducción de vehículos o interacciones corporales arbitrarias. Su coherencia observada usa grilla, bloqueos y acciones autoradas.

## Gate de esta pasada

Tenemos evidencia suficiente para comenzar un laboratorio acotado de asimilación espacial. No se cierra aceptación artística, equivalencia del original, elección de motor ni producción de ciudad. La siguiente prueba debe demostrar comportamiento visible y estados, no sólo existencia de código o cantidad de tests.

## Runtime spatial comparison — 2026-10-10

Siete arranques/575 poses nativas, 138 ensayos de cursor: 65 superposiciones opacas frontales, 70 supresiones por techo y 103 puntos egg. Perímetro del poste en ambos sentidos; pared con vecinos bloqueados/inaccesibles; armario seleccionado pero sin efecto con acceso cerrado, panel correcto a contacto1 después de abrir/entrar. Revelación de armario oculto por techo repetida dos veces: discrepancia CE con percepción prevista para Vampiro. Omisión de un tramo del log contrastada con recibos nativos y repetición independiente; causa del logger sin verificar. 83 tests/siete guards PASS. A2-01/02/03/05/06/07/08/09/10 parciales, tres casos sin ejecutar; todo Vampiro sin verificar. See [spatial report](CE_SPATIAL_2026-10-10.md). `gameMouseGetObjectUnderCursor` uses roof intersection/egg and ordered nonzero art-pixel hits; `objectDraw` and blocking use different criteria. Native hit flags and compound identity are measured, not full renderer equivalence. Hidden roof disclosure is a reproducible reference deviation; a successful distance1 inventory opening after entering does not establish all contact permissions or barrier revalidation. Fully opaque wall hiding, wide/elevated art, original Windows and Vampiro artistic acceptance remain open.
