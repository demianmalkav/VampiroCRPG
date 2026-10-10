# A2 — Geometría y bloqueo medidos en CE

Fecha: 2026-10-10. Estado: **REFERENCE_PARTIALLY_OBSERVED**, A2-01/A2-02. [Evidencia estructurada](CE_NAVIGATION_2026-10-10.json), [casos y cobertura](A2_ACCEPTANCE_CASES_01.json). La unidad cierra la cobertura descrita; ninguno de los doce casos completos A2 está aceptado para Vampiro.

## Resultado y alcance

En una corrida final se enviaron **21 solicitudes de movimiento**: seis direcciones nativas y seis regresos; nueve solicitudes de destino libre/ocupado. Diecinueve producen desplazamiento y dos no obtienen desplazamiento desde la posición exterior. Las 21 seleccionan la casilla solicitada según el cursor nativo. Se registran **53 observaciones nativas de casilla: una inicial y 52 cambios**. Las rutas muestreadas coinciden con ese registro; cada transición es a un hex vecino. En esas observaciones, `_obj_blocking_at`, excluyendo al protagonista, devuelve `null` sobre su casilla. Esto no prueba todos los bordes, volúmenes gráficos o fases entre observaciones.

Al señalar poste, muro, guardia o hidrante, el personaje se acerca a una casilla libre vecina. También llega a suelo libre rodeando el poste. Señalar un escritorio o armario interior desde 13909 no obtiene desplazamiento; no se verificó acercamiento a un contenedor accesible ni todo su perímetro.

**Referencia fijada:** CE `alexbatalov/fallout2-ce` @ `e97087b9582f37075db347a89898887320753f8b`, upstream limpio; fpattern @ `8523173ec252c3b796fcdfca0fcc6329642fbbe3`. ELF Linux x86-64 SHA256 `70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c`. Configuración silenciosa DAT-only del [laboratorio ya ejecutado](CE_EXECUTABLE_LAB_2026-10-10.md). NCR1.MAP del parche: versión 20, índice 42, elevación 0, SHA256 `11464ce6dd1f5d374523b470ddb7590419d1a88cef72c34c8199fe71bfd01e00`. Identidades completas de los tres DAT y comprobaciones de conservación en el JSON. Sin ejecución del EXE original de Windows.

## Entrada y medición

Herramientas propias: [adaptador SDL](../../tools/research/ce_navigation_input.cc), [controlador](../../tools/research/probe_ce_navigation.py), [comprobador](../../tools/research/check_ce_navigation_evidence.py). `LD_PRELOAD` sustituye sólo deltas/botones de ratón relativo. Invoca consultas nativas de proyección, selección, vecinos y bloqueo; lee el actor, sin teletransporte, llamada al pathfinder ni escritura del estado autoritativo. El ELF/upstream no se parchean. `Home` recentra la cámara mediante la entrada normal de CE después de cada observación.

Cada solicitud comprueba `tileToScreenXY` + centro `[16,8]` → `tileFromScreenXY` y luego la casilla bajo el cursor real antes de mantener el botón 200 ms. Un cursor recortado al borde de pantalla detiene la prueba antes del clic. El estado externo se muestrea aproximadamente cada 40 ms; además, el adaptador registra cambios de casilla en el hilo del juego al consultar SDL, con bloqueador e identificación del actor. El asentamiento observado exige diez poses iguales después de 800 ms, con límite de doce segundos. No equivale a confirmar toda cola de animación o el fin de un script.

Esto corrige una limitación del smoke anterior: aquel demostraba desplazamiento, pero el warp físico de XTEST no comprobaba que CE hubiera recibido el destino pensado. Aquí se verifica el cursor interno. Los hashes de las herramientas medidas, offsets ELF y hash del registro privado completo están en el JSON; el resumen publicado conserva solicitudes, rutas, estados, consultas y todas las observaciones nativas de casilla.

## Geometría — A2-01 parcial

Desde tile 13915, direcciones nativas 0–5: **13714, 13914, 14115, 13916, 13716, 13715**. Cada solicitud llega al vecino y cada regreso a 13915. Los seis centros proyectados y la selección efectiva concuerdan. La grilla de objetos tiene ancho 200 y desplazamientos según paridad: par `[-1,199,200,201,1,-200]`; impar `[-201,-1,200,1,-199,-200]`, orden NE/E/SE/SW/W/NW de `src/tile.cc` fijado. No traducir literalmente coordenadas de la grilla cuadrada C.

No se cierra equivalencia de velocidades/duraciones: los muestreos externos, captura de imágenes y actividad de NPC no controlada no constituyen un reloj lógico comparable. La política C de 300/425 ms sigue siendo propuesta propia; no es un resultado CE.

## Destinos y rutas — A2-02 parcial

| Solicitud | Bloqueador nativo: ID / PID / flags | Inicio → final | Ruta observada |
| --- | --- | --- | --- |
| Poste 13912 | 60 / `0x02000124` / `0x80008000` | 13915 → 14113 | 13915,13914,14113 |
| Suelo libre 13911 | ninguno | 14113 → 13911 | 14113,14112,14111,13911 |
| Suelo libre 13915, rodeo | ninguno | 13911 → 13915 | 13911,13712,13713,13714,13915 |
| Muro 14310 | 47 / `0x0300026d` / `0x00000008` | 13915 → 14311 | 13915,13914,14113,14112,14311 |
| Guardia NCR 12519 | 47 / `0x01000089` / `0x20002000` | 14311 → 12319 | 14311,14112,14113,13914,13915,13716,13717,13518,13318,13118,12918,12718,12518,12318,12319 |
| Hidrante 13710 | 1032 / `0x020000f3` / `0x80008000` | 12319 → 13510 | 12319,12318,12517,12516,12715,12714,12913,12912,13111,13110,13310,13510 |
| Suelo libre 13909 | ninguno | 13510 → 13909 | 13510,13709,13909 |
| Escritorio 14902 | 974 / `0x0200066c` / `0xa0008000` | 13909 → 13909 | sin desplazamiento |
| Armario 14499 | auxiliar 531 / `0x02000043` / `0xa0000008` | 13909 → 13909 | sin desplazamiento |

El guardia puede moverse durante la corrida; el JSON conserva su pose al solicitar el destino. Un muro y un guardia comparten ID 47: **el entero ID no basta como clave única** en este mapa. Fijar mapa/hash y emplear identidad compuesta tile/PID/instancia en el laboratorio; los IDs estables futuros son otro contrato.

En 14499 coexisten el ítem Locker ID 491/PID `0x00000084`/flags `0x20001000`, el auxiliar Secret Blocking Hex ID 531/PID `0x02000043` y otra pieza gráfica. La consulta de bloqueo devuelve el auxiliar. En `src/object.cc::_obj_blocking_at` fijado, el bloqueo atiende a CRITTER/SCENERY/WALL sin HIDDEN ni NO_BLOCK; no al tipo ITEM. MULTIHEX amplía a vecinos, pero esa extensión no se ejercitó aquí. `FLAT` o `SHOOT_THRU` no significan por sí solos suelo transitable.

**Consecuencia para asimilación:** debe relacionarse la representación del contenedor con toda su huella, incluidos auxiliares. No basta buscar un flag en el ítem dibujado. La traza propuesta `DESTINATION_BLOCKED / posición unchanged` de C es política de adaptación y difiere del acercamiento observado en CE. Se conserva separada en los casos previstos; este trabajo no cambia el runtime Vampiro.

## Evidencia visual, reproducibilidad y límites

La corrida final `navigation-08` grabó fotogramas reales de CE y sus tiempos, además de capturas de cada resultado. El GIF privado `Fallout2_CE_rodeo_observado.gif` corresponde a `target-2-13915.gif`: avatar rodeando el poste, sin interpolación ni arte generado. SHA256 `d3f402ed3f45f7be84c759de33bccf3f2ad2d23bb5f6a03a3f064d5c17ef2897`, 274967 bytes. El GIF se mantiene fuera de GitHub por incluir arte original; no es una muestra de nuestro arte.

Experimentos previos delimitan lo que falta: un escritorio proyectado en x=800 fue recortado a x=799 y rechazado antes del clic; dos intentos de llegar a barriles exteriores no produjeron una aproximación válida y se detuvieron por selección fuera de pantalla. No cuentan como PASS de contenedor. Las solicitudes interiores válidas posteriores quedan documentadas como ausencia de desplazamiento desde 13909, con entrada comprobada; no prueban contacto o uso. No insistir con los mismos waypoints sin evidencia nueva.

Repetición privada, con el ELF y los datos fijados:

```sh
python tools/research/probe_ce_navigation.py --binary /private/build/fallout2-ce --ce-source /private/ce --inputs /private/data --output /private/navigation-new --six-directions --center-after-move --record-frames --targets 13912 13911 13915 14310 12519 13710 13909 14902 14499
python tools/research/check_ce_navigation_evidence.py research/FALLOUT2/CE_NAVIGATION_2026-10-10.json --check-source-hashes
python -m unittest discover -s tools/research -p 'test_ce_navigation_evidence.py'
```

Requiere el laboratorio Linux existente: SDL2 dev, g++, Xvfb, xdotool y Pillow; mismos procesos padre/hijos para X TCP. Las rutas de NPC no son replay determinista. No introducir estas dependencias en el juego distribuible.

**DONE:** selección exacta, seis vecinos/regresos, destinos libres/ocupados, rodeo y huella auxiliar medidos en CE.

**EVIDENCE:** 21 solicitudes, 53 observaciones nativas, coincidencia de rutas y centros, tres DAT conservados; comprobador PASS; siete pruebas de rechazo/alcance y once tests de lectores PASS. Captura animada privada real. Ningún upstream, save o runtime Vampiro modificado.

**OPEN:** A2-01/A2-02 parciales: tiempos/reloj, contenedor accesible/perímetros/huella amplia, bloqueo dinámico y volumen/oclusión; otros diez casos sin ejecutar. Original Windows sin comparar, motor productivo sin elegir, arte/reglas VTM sin integrar y tres fallas C sin corregir.

**NEXT:** A2-03: redirigir durante un segmento visible de caminar, registrar casilla/offset/frame antes y después, nueva intención y destino final; repetir una orden y cancelar. Medir la continuidad nativa separada de la política C. Después puerta/acceso para resolver contenedor alcanzable, selección/visor, contacto y persistencia. Conservar cobertura A2-02 abierta hasta medirla; no repetir transferencia, arranque ni encuesta de motores.
