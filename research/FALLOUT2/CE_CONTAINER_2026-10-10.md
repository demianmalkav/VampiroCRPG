# Selección, visor y armarios observados en CE — 2026-10-10

DONE: tres arranques independientes registran selección normal, observación y tres resultados distintos: armario bloqueado, apertura de armario vacío e interrupción de su acercamiento. Se incorpora cobertura parcial A2-06 y evidencia adicional A2-02/A2-03. A2-08 permanece NOT_EXECUTED: abrir un inventario vacío no demuestra recoger un objeto ni transferir propiedad.

## Referencia y método

Mismo CE limpio e97087b9582f37075db347a89898887320753f8b, fpattern 8523173ec252c3b796fcdfca0fcc6329642fbbe3 y ELF SHA256 70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c. NCR1 Linux DAT-only; master/critter/patch000 conservan los hashes publicados. La comprobación de esta unidad no detectó deriva: no se repitieron recuperación ni compilación.

Adaptador y controlador nuevos, separados de las sondas anteriores congeladas. Sustituyen únicamente entrada relativa de ratón SDL; teclas XTEST normales. Consultan selección nativa, rectángulo de arte, distancia, pose/animación, estado del armario, ventana/objetivo de inventario, slots/propietarios y dos líneas recientes del visor. No escriben posición, inventario ni estado de juego. Tras cargar actor13915, abren la misma puerta y cruzan al interior15709 como preparación. El clic se realiza sobre un píxel visible cuyo objeto seleccionado coincide con la identidad compuesta prevista; la casilla bajo ese píxel es distinta y no se usa para atribuir la selección.

| Corrida | Objetivo (id/pid/tile/elevación) | Estado inicial | Resultado observado | Poses/estados totales / interacción |
| --- | --- | --- | --- | ---: |
| container-02 | 491/132/14499/0 | Bloqueado, cuatro slots | Vecino14500, gesto11, aviso de bloqueo; frame0 y sin panel | 117 / 13 |
| container-03 | 968/132/14497/0 | Sin bloqueo, vacío | Vecino14498, gesto11; panel dirigido al mismo objeto; Escape sale | 134 / 16 |
| container-04 | 968/132/14497/0 | Sin bloqueo, vacío | Uso desde15709, carrera parcial; redirección a15709 cancela antes de abrir | 77 / 18 |

Son 328 registros totales, incluidos preparación y entrada; se publican sólo 47 registros de la interacción y sus recibos/entradas. No son 328 desplazamientos ni una repetición idéntica de los tres escenarios. Cada escenario se ejecutó una vez con las fuentes finales; container-01 fue exploratorio y no se añade como repetición. Las capturas y registros completos permanecen privados; la evidencia pública contiene metadatos numéricos y hashes/clases de las líneas del visor, sin texto original ni censo completo del mapa.

## Cadena medida

Antes del uso, selección y visor identifican el armario observado. En ambas interacciones adyacentes se registran ANIM11, orientación0 y frames0–11 a distancia1. El bloqueo del armario14499 es data.flags0x02000000; sus cuatro slots y propietarios permanecen iguales, inventario del avatar vacío. El visor agrega la negativa y no aparece panel ni cambia frame0.

En el armario14497 sin bloqueo, el gesto precede a la primera observación del panel. La ventana está inicializada y tiene buffer vivo; su objetivo nativo coincide con 968/132/14497/0. El panel aparece cuando el armario ya está en frame1 y todavía no se han registrado los frames2/3: animación completa y apertura de interfaz son señales distintas. Actor y armario están vacíos antes/después. No se ejecuta Take All ni una transferencia repetida; los campos correspondientes son null. Escape destruye la ventana observada; no se afirma cierre del armario, que permanece en frame3 en el recibo final.

Para interrumpir, se ordena usar14497 desde15709. La sonda confirma ANIM19 y offset[9,-7] antes de cualquier apertura, a distancia12. Cambiar modo y colocar el cursor lleva tiempo: el avatar avanza hasta15104 en el recibo de liberación. Por eso el destino15709 es una **redirección a la casilla inicial**, no una parada instantánea en la casilla actual. Regresa a15709/STAND; durante la ventana registrada no aparece gesto11, panel, búsqueda ni cambio del frame0 del armario. Inventarios vacíos conservados. No se demuestra cancelación durante el gesto, después del efecto ni ante todas las carreras de entrada.

## Soporte en fuente y límites

La rama contenedor de [actions.cc fijado](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/src/actions.cc#L1182-L1249) registra proximidad, gesto, uso del contenedor y petición de saqueo como pasos distintos. Su condición de artLock/artGetActionFrame en la rama contenedor es anómala en esta revisión; no se corrige ni se usa para afirmar el instante exacto de contacto. El registro demuestra orden y estados observados, no un marcador atómico de mano/efecto.

OPEN: A2-06 no cubre selección superpuesta ni oclusión detrás de muro; A2-03 no cubre todos los tiempos/recursos o cancelación durante gesto. A2-05 puerta/llave sigue parcial: un armario bloqueado no sustituye una puerta bloqueada. A2-08 objeto en suelo, propiedad única y antes/después del contacto continúa sin ejecutar. Siete otros casos sin ejecutar, ninguna aceptación de Vampiro. Memoria muestreada sin suspender el motor; intervalos variables, sin reloj lógico exacto ni ausencia de eventos entre muestras. Windows original, persistencia, arte/VTM y motor productivo siguen abiertos; rechazo de muestra02 y tres fallas C preservados.

EVIDENCE: [estado y recibos saneados](CE_CONTAINER_2026-10-10.json), sonda/controlador propios con hashes, diez nuevos tests de rechazo. Comandos reproducibles, sin archivos originales:

```bash
python3 -m unittest discover -s tools/research -p 'test_*.py' -v
python3 tools/research/check_ce_container_evidence.py research/FALLOUT2/CE_CONTAINER_2026-10-10.json --check-source-hashes
```

Reproducción privada: ejecutar probe_ce_container_interaction.py con --binary/--ce-source/--inputs/--output nuevos y --record-frames. Negativa: `--locker-tile 14499 --locker-id 491 --locker-pid 132 --scenario complete`. Apertura: `--locker-tile 14497 --locker-id 968 --locker-pid 132 --scenario complete`; interrupción: mismos identificadores, `--scenario cancel`. Requiere SDL/Xvfb/xdotool/Pillow, compilador y referencia exacta; no publicar DAT/capturas ni reutilizar un output existente. Fuentes de navegación/redirección/puerta anteriores intactas y sus guards siguen aplicando. La CI Walk proof de a8a829b anterior terminó SUCCESS en push38079264998/PR38079269846; no equivale al resultado del commit nuevo.

NEXT: A2-08 acotado: identificar un objeto portátil único y alcanzable mediante consulta de prototipo y selección nativa; medir uso desde suelo, gesto/contacto, propietario e inventario antes/después, cancelación antes del efecto y repetición cuando sea practicable. Cerrar sólo esa cobertura medida; no fabricar transferencia desde un armario vacío ni editar el estado para obtenerla.
