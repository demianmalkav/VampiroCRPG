# A2-03 — Redirección, repetición y parada medidas en CE

Fecha: 2026-10-10. Estado: **REFERENCE_PARTIAL**. [Registro y fronteras medidas](CE_REDIRECTION_2026-10-10.json). Cinco escenarios completados sobre NCR1 con entrada comprobada, instantáneas nativas de tile/offset/frame/rotación/FID y capturas reales. No aceptación de Vampiro ni del caso completo A2-03: no se fijó exactamente 150 ms ni se ensayó cancelar una interacción pendiente.

## Resultado

La última orden de las probadas determina el destino final. Repetir el destino selecciona carrera; Escape abre opciones y pausa, conservando el recorrido al cerrarlas. Solicitar la casilla actual interrumpe y deja al actor detenido en ella. Cambiar de dirección a mitad de un segmento restablece el frame y el offset dentro de la misma casilla: **CE no demuestra la continuidad de progreso que exige nuestra política C**. Adoptar el mecanismo sin adaptar ese comportamiento no resolvería por sí solo el salto visual del prototipo.

Referencia inalterada: CE `e97087b9582f37075db347a89898887320753f8b`, fpattern `8523173ec252c3b796fcdfca0fcc6329642fbbe3`, upstream limpio, ELF SHA256 `70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c`. NCR1.MAP parche, versión 20/índice 42/elevación 0, SHA256 `11464ce6dd1f5d374523b470ddb7590419d1a88cef72c34c8199fe71bfd01e00`. Tres DAT idénticos antes/después, hashes y configuración en el JSON. Laboratorio DAT-only silencioso, `interrupt_walk=1`, `running=0`; no overrides/DLLs de la instalación Windows, cuyo EXE no se ejecutó.

## Escenarios y observaciones

Cada ensayo parte de 13915, solicita caminar a 13911, detecta FID WALK y offset no nulo antes de intervenir. Entre ensayos se vuelve a 13915 mediante entrada normal, sin teletransporte.

| Escenario | Entrada durante caminar | Resultado medido |
| --- | --- | --- |
| Redirección simple | Nuevo destino 14115 | Termina de pie en 14115; primer cambio posterior conserva tile 13915, reinicia frame a 0 y cambia rotación 0 → 2 |
| Destino repetido | Otra solicitud a 13911 | FID pasa de animación WALK=1 a RUNNING=19; termina en 13911 |
| Dos redirecciones | 14115 y luego 13716, ambas con offset parcial | Termina en 13716; se observan dos reinicios dentro de tile 13915, rotaciones 0 → 2 → 4 |
| Escape | Abrir opciones durante caminar, observar y cerrarlas | La pose permanece igual entre 24687 y 25604 ms del reloj SDL; el menú se ve en captura. Al cerrar sigue caminando y llega a 13911 |
| Parada por casilla actual | Solicitar tile 13915 mientras el actor tiene offset parcial | Primer cambio: STAND=0, frame 0 y offset `[0,0]`, todavía en 13915; no sigue hasta 13911 |

En las redirecciones simple y primera rápida, la liberación del botón se observa con tile 13915/offset `[7,-5]`/frame 1/rotación 0. El primer cambio de pose registrado 16 y 18 ms después, respectivamente, tiene offset `[2,1]`/frame 0/rotación 2 en el mismo tile. La segunda rápida pasa de `[6,7]` a `[-8,0]` en 17 ms; la parada pasa de `[7,-5]` a `[0,0]` en 16 ms. Estos intervalos son entre instantáneas de la frontera de entrada y primer cambio, no el tiempo exacto de consumo ni un presupuesto de respuesta.

Ancla calculada: proyección nativa del tile + centro `[16,8]` + `Object.x/y`, con cámara fija durante los casos. Cambios de ancla: `[-5,+6]` (simple/primera rápida), `[-14,-7]` (segunda rápida), `[-7,+5]` (parada). Sirve para medir reinicio de offsets; no demuestra la posición anatómica del pie ni todos los volúmenes del sprite. La repetición muestra carrera con primer offset `[9,-7]`; no se convierte esa sola frontera en una prueba de velocidad o continuidad general.

## Instrumentación y respaldo en fuente

Herramientas propias: [adaptador de poses](../../tools/research/ce_redirect_input.cc), [controlador](../../tools/research/probe_ce_redirect.py), [comprobador](../../tools/research/check_ce_redirect_evidence.py), [pruebas de rechazo](../../tools/research/test_ce_redirect_evidence.py). Mantienen intactas las herramientas y hashes del [experimento de navegación anterior](CE_NAVIGATION_2026-10-10.md).

El adaptador sólo sustituye deltas/botones de ratón SDL y realiza consultas nativas de lectura. Registra pose al cambiar un campo o la secuencia de entrada; **429 instantáneas**, no 429 desplazamientos. Todas las casillas del actor consultadas carecen de bloqueador nativo, y las transiciones de tile son vecinas. Registra antes de procesar el input, no todos los puntos internos de una transacción. El controlador comprueba proyección/unproyección y cursor interno antes del clic, mantiene el botón 80 ms y exige offset parcial en la instantánea de liberación de cada interrupción. Las teclas se entregan por XTEST. No invoca directamente el movimiento, clear ni el pathfinder, y no escribe estado autoritativo.

Fuente fijada que explica las observaciones, inspeccionada separadamente:

- `src/game_mouse.cc:gameMouseHandleEvent` solicita movimiento al liberar el botón izquierdo en modo MOVE.
- `src/animation.cc:_check_move` usa `reg_anim_clear(gDude)` fuera de combate con `interrupt_walk` habilitado.
- `reg_anim_clear` → `_anim_set_end` → `_dude_stand`; ésta recoloca en el tile actual y pone frame 0. La nueva `_object_move` comienza otra secuencia, no continúa automáticamente el segmento previo.
- `_dude_move` recuerda el destino anterior y llama a `_dude_run` si se repite. `animation.h` identifica WALK=1 y RUNNING=19.
- `src/game.cc`, `KEY_ESCAPE`, abre `showOptions`; no es una orden genérica de cancelar recorrido.

Son resultados de **CE Linux con esta configuración**, no confirmación automática del binario clásico ni reglas nuevas aprobadas para nuestro juego. La política C de conservar posición/progreso y elegir la intención siguiente sigue separada; Escape como cancelación también requiere una decisión de adaptación explícita.

## Reproducción y evidencia visual

```sh
python tools/research/probe_ce_redirect.py --binary /private/build/fallout2-ce --ce-source /private/ce --inputs /private/data --output /private/redirect-new --scenarios single repeated rapid escape stop
python tools/research/check_ce_redirect_evidence.py research/FALLOUT2/CE_REDIRECTION_2026-10-10.json --check-source-hashes
python -m unittest discover -s tools/research -p 'test_ce_*evidence.py'
```

Requiere el laboratorio existente: Linux x86-64, SDL2 dev, g++, Xvfb, xdotool y Pillow, servidor y clientes como hijos del mismo proceso para X TCP. `redirect-01` sirvió de exploración simple; `redirect-02` ejecutó los cinco casos con las herramientas cuyos hashes constan en el JSON. El resumen conserva todos los registros de pose como filas con columnas explícitas, entradas/fronteras relevantes y hash del registro privado completo. El control comprueba fuente, referencia, selección, parcialidad, fronteras y resultados; PASS no significa aceptación de los doce casos A2.

GIF privado real `Fallout2_CE_cambio_de_destino.gif`, fuente `rapid.gif`, 17 frames, 800×600, 250915 bytes, SHA256 `84e7cb45dc86643a65feee86cd7540e547d43b64e4c8f473b2c2016ea6eb6060`. Captura `escape-options.png` inspeccionada: menú Options sobre la escena. Arte original fuera de GitHub; no es arte de Vampiro ni aprobación de calidad artística. Captura y actividad de NPC no controlada impiden exigir una ejecución temporal idéntica.

**DONE:** cinco estímulos de referencia medidos: redirección simple/doble, carrera al repetir, Escape/retorno y parada por casilla actual; diferencia de continuidad registrada.

**EVIDENCE:** 429 instantáneas nativas y entradas seleccionadas; comprobador PASS, siete nuevas pruebas de guardas PASS, siete pruebas de navegación previa y once lectores PASS (25 en total). Fuentes upstream/ELF/DAT conservados; sin modificación del runtime o saves de Vampiro.

**OPEN:** A2-01/A2-02/A2-03 parciales; tiempos lógicos/exactos, contenedor accesible/perímetros, cancelación de interacción, save/load durante fases y oclusión. Otros nueve casos todavía sin ejecutar. Original Windows sin medir, motor productivo no elegido, arte/VTM sin integrar; muestra 02 y tres fallas C permanecen abiertas.

**NEXT:** puerta y acceso alcanzable en NCR1: identificar puerta/estado/bloqueador, seleccionar mediante UI normal, medir acercamiento/apertura y cambios de frame/flags/pasabilidad, cruzar sólo si está abierta y registrar estado final. Usar ese acceso para una única prueba de contenedor alcanzable si permite hacerlo; si exige una llave/trama no disponible, marcar el límite y elegir una puerta accesible con evidencia nueva. No volver a tantear los barriles con waypoints ya fallidos. Mantener fases de efectos, selección/visor y persistencia como cobertura posterior; no cerrar A2-05 con sólo abrir una puerta.
