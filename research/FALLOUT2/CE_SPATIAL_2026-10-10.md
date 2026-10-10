# Selección, oclusión y acceso espacial CE — 2026-10-10

Estado: **REFERENCE_PARTIAL**. Siete arranques completos, 575 registros nativos de pose/estado y 138 ensayos de cursor; A2-06/07/10 reciben evidencia parcial. Ninguna aceptación de Vampiro ni equivalencia con el ejecutable Windows. Parent lógico: `2933d2aa121be2fb3cd1071e99b6a75cbd9dac36`.

## Resultado que afecta la adaptación

La referencia distingue selección por píxel, dibujo y bloqueo físico, pero **no garantiza que coincidan**. El mismo armario 968/pid132/tile14497 fue identificado por el visor bajo un techo que lo ocultaba en la imagen. Se repitió en dos arranques, con el avatar fuera, puerta cerrada y distancia nativa14. La segunda corrida lee también `gGameMousePointedObject`: coincide con el seleccionado y el diagnóstico LOOK. La consulta `_square_roof_intersect` devolvió0 y el píxel quedó fuera del egg; la imagen seguía mostrando el techo. Es una discrepancia reproducible entre selección y visibilidad en este CE/DAT/configuración, **no una política deseable para la percepción de Vampiro**. No se ha aislado si el origen es clásico, CE, configuración o recursos suministrados.

Seleccionar no permitió actuar: ambas pulsaciones conservaron avatar15711, armario cerrado e inventario no visible. Una petición de movimiento a14497 tampoco avanzó mientras la puerta estaba cerrada. Tras abrir la puerta26/pid33555281/tile15710 por UI, el avatar entró15709 y llegó14498, distancia1; entonces apareció el panel dirigido al mismo armario y el visor SEARCH. Escape cerró el panel. El armario vacío y el inventario del avatar permanecieron vacíos: no transferencia inventada.

Esto demuestra un caso de acceso cerrado/abierto, **no** todas las acciones a través de muros cercanos. En la fuente `_is_next_to`, el guard comprueba distancia>1; no expresa un test general de barrera o línea de contacto. Cambio/destrucción del objetivo durante acercamiento y revalidación atómica del efecto siguen abiertos.

## Escenarios medidos

| Corrida privada | Objetivo | Registros de pose | Resultado |
|---|---|---:|---|
| spatial-04 | Selección exterior inicial | 42 | 40 ensayos de cursor, todos bajo supresión de techo; armario no seleccionable desde posición inicial; suelo13914 alcanzado. |
| spatial-05 | Poste13912, seis vecinos, ida y vuelta | 80 | 13 solicitudes alcanzan sus destinos. Superposición del cuerpo y poste detectada por píxeles nativos; poste aparece delante en un punto compartido. 13 GIF reales privados. |
| spatial-06 | Barrido equilibrado de superposiciones | 79 | 46 ensayos, 40 seleccionan objeto y seis son suprimidos por techo; se compara el hit-list observado tras mover el cursor, no sólo el candidato previo. |
| spatial-07 | Acceso cerrado/abierto y profundidad interior | 159 | Armario oculto revelado, uso/acercamiento inaccesibles; puerta abierta, entrada, contacto1, panel correcto y salida. 36 poses contienen al menos un punto con flag4 del egg. |
| spatial-08 | Vecinos del muro14310 en ambos sentidos | 92 | Destinos sólidos terminan en vecinos libres; dos de los seis vecinos solicitados son sólidos y otro es libre pero inaccesible desde el exterior. No se presenta como perímetro completo alcanzable. Una omisión del log se conserva y contrasta con recibos. |
| spatial-09 | Clic de muro, suelo y repetición de objeto oculto | 89 | Arrow/inspect no mueve al avatar; move a muro no entra14310; suelo13915 alcanzado. Segunda revelación del armario, con identidad del objetivo LOOK leída directamente; uso sin efecto. |
| spatial-10 | Diagnóstico del primer recorrido junto al muro | 34 | Repite arribo14110 y regreso13915 con secuencia vecina completa en el log. |

Los 138 ensayos incluyen **65 superposiciones opacas** que eligen el último objeto del hit-list nativo observado, **70 supresiones de techo** y tres puntos de otro alcance. Los candidatos pueden cambiar entre consulta y hover; dos ensayos del barrido equilibrado ya tenían un solo hit al observarlos. No se cuenta un candidato como superposición medida si desapareció.

Se observan **103 puntos del cuerpo** con flag4 en la lista de intersección durante la profundidad interior. El bit4 describe el tratamiento de la máscara egg en la selección; no se lo equipara automáticamente a un resultado raster idéntico en cada frame. Capturas y frames de GIF privados muestran exposición del interior y el personaje cerca de las paredes. Poste, muro y decoración plana/no plana se contrastan dentro del alcance original; dumpster ancho y decoración elevada quedan pendientes.

## Integridad y omisión conservada

575 consultas registradas no encuentran bloqueador en la casilla del actor. El log spatial-08 pasa de14112/tick17146/input30 a14110/tick21686/input78 sin incluir14311. Los recibos nativos de las entradas31/33/37 conservan14112→14311→14110, todos vecinos. La repetición independiente spatial-10 registra el recorrido sin ese hueco. El checker exige esa cadena real y rechaza su eliminación o cualquier hueco nuevo sin evidencia. **Causa de la omisión del logger: UNVERIFIED**; no se promueve a teletransporte, ni se afirma muestreo exhaustivo/atómico de todas las colisiones.

La copia local estaba atrasada y master/critter truncados a325947904/43734016 bytes. Se recuperaron 71 blobs del HEAD exacto y se verificaron sus SHA1 Git; se restauró master desde RARs locales con hashes exactos y critter desde Drive por descarga autenticada. Se conservaron las copias truncadas privadas. Causa de deriva local sin verificar. Tres intentos de preparación fallaron por dependencias XTEST/XKB; ninguno aporta casos de mapa aceptados. No se repitió la absorción documental ni se reconstruyó el ejecutable.

## Identidad y reproducción

- CE limpio: `e97087b9582f37075db347a89898887320753f8b`; fpattern: `8523173ec252c3b796fcdfca0fcc6329642fbbe3`.
- ELF SHA256: `70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c`.
- Tres DAT: identidades exactas en [JSON](CE_SPATIAL_2026-10-10.json); originales sin cambios después de cada corrida.
- Mapa NCR1 original, configuración DAT-only silenciosa de la referencia anterior; no overrides/DLL Windows ni MAP propio.
- Versiones nuevas de sonda conservan las anteriores: `ce_spatial_input`/`probe_ce_spatial`, variante visibility con cuotas de barrido, variante click con objetivo de hover leído. Los hashes vinculan cada corrida a su fuente y plan; ninguna fuente medida se reescribió después de su corrida.
- Consultas de rectángulo, hit-list, egg/techo, selección, distancia, inventario y visor; sólo entradas normales SDL/teclado. Las consultas gestionan caché/asignación de listas, sin escribir estado autoritativo. No invocan callbacks de interacción directamente.
- Capturas, GIF, texto, censos y entradas originales privados; sólo datos numéricos, diagnósticos y hashes publicados. Los recibos repetidos se proyectan a campos pertinentes; hashes de las trazas completas se conservan.

Ejemplo privado; cambiar output por una carpeta nueva en cada arranque:

```bash
python3 tools/research/probe_ce_spatial_click.py \
  --binary /ruta/privada/build/fallout2-ce --ce-source /ruta/privada/ce \
  --inputs /ruta/privada/datos --lab-deps /ruta/privada/lab-deps \
  --output /ruta/privada/corrida-nueva \
  --plan research/FALLOUT2/spatial_click_plan_01.json
```

El laboratorio necesita SDL2 de desarrollo, Xvfb, xdotool y xkbcomp con sus bibliotecas. En la recuperación actual se extrajeron paquetes en una carpeta aislada y se enlazó el compilador XKB requerido por Xvfb. Planes versionados reproducen los escenarios; RNG por defecto y NPCs originales pueden moverse.

Validación sin juego ni activos:

```bash
python3 -m unittest discover -s tools/research -p 'test_*.py' -v
python3 tools/research/check_ce_spatial_evidence.py research/FALLOUT2/CE_SPATIAL_2026-10-10.json --check-source-hashes
```

**83 tests** de lectores/rechazo y **siete guards** de evidencia/fuentes PASS. Los seis guards previos preservan sus fuentes. CI del parent2933d2aa: Research y Walk SUCCESS, push/PR; CI del commit nuevo se registra al publicar, sin inferir su conclusión desde el parent.

## DONE / EVIDENCE / OPEN / NEXT

- **DONE:** matriz de selección/superposición, profundidad/perímetros y acceso cerrado/abierto; discrepancia de visibilidad preservada; scripts, planes y checker reproducibles. No cambios en juego Vampiro, arte, reglas, saves o motor elegido.
- **EVIDENCE:** siete arranques, 575 poses, 138 ensayos; 65 frontales opacos, 70 bloqueados por techo; 103 puntos egg; capturas y 40 GIF reales privados; 83 tests/siete guards. A2-01/02/03/05/06/07/08/09/10 parciales; A2-04/11/12 sin ejecutar; todo Vampiro sin verificar.
- **OPEN:** origen de revelación bajo techo y omisión del log; muro completamente ocultante/objetivo próximo, disponibilidad cambiante y contacto atómico; huellas grandes/elevación, comparación Windows y demás aceptación completa. Muestra02 rechazada y tres defectos C abiertos.
- **NEXT:** paquete de persistencia durante movimiento: guardar/cargar por UI original al caminar/correr y con una redirección pendiente; comparar posición, intención/cola, pose y continuación con controles sin carga. Registrar cancelación o reanudación efectiva, sin imponer persistencia de fases a CE ni cambiar originales. Cerrar alcance A2-09 con evidencias y límites concretos; motor/VTM/arte siguen abiertos.
