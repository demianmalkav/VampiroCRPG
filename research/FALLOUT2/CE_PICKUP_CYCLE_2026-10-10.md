# Paquete de recogida, interrupción y persistencia CE — 2026-10-10

DONE: ocho arranques completan un paquete de referencia: cola/gesto/propiedad, cancelación temprana y petición tardía, petición después del efecto, repetición física durante gesto y guardado/carga antes, después y durante el gesto. Son526 observaciones nativas. El desacuerdo del marcador queda reconciliado con la cola observada en este laboratorio silencioso. El guardado durante gesto conserva el objeto en suelo y elimina la acción pendiente; cargar no reanuda automáticamente esa recogida. No hay implementación ni aceptación de Vampiro.

## Identidad, método y alcance

Se conserva CE e97087b9582f37075db347a89898887320753f8b, fpattern8523173ec252c3b796fcdfca0fcc6329642fbbe3, fuentes limpias y ELF SHA25670516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c. Los tres DAT mantienen los hashes de la [recogida anterior](CE_PICKUP_2026-10-10.json). DENBUS1 original del parche, SHA256c293b1652f71f518f5e92915a1676ecb5ad75cf33f93a0d9db30de6fb53236db; objeto200/pid4/tile12477/elevación0, avatar inicial13292. Header23895 sigue siendo distinto del arranque observado, causa exacta sin verificar. No se repite recuperación, descarga o compilación del motor.

La sonda nueva lee la cola del actor y registra cursor/completados, kinds, delays y reconocimiento de los callbacks por símbolos del ELF exacto. Nunca ejecuta ni modifica callbacks, colas, objetos o reloj. `ce_animation_layout.cc` consulta sizeof/offsetof contra el fuente limpio: secuencia4416bytes, descripción80, inicio16, delay36, callback40. El compilador descarta implementación incluida mediante garbage collection de secciones; ese auxiliar no es otro motor. Dependencias del laboratorio usadas desde la copia local, sin cambiar upstream.

Tres controladores propios conservan identidades medidas distintas: ciclo básico, interrupción con cursor preparado y persistencia. Ratón SDL y teclas nativas, outputs nuevos; hashes de fuentes, configuración y saves privados registrados. Antes de F7 se borra sólo el puntero observado por el laboratorio y después se lo vuelve a localizar en mapa/inventario; evita consultar un puntero de un objeto destruido por carga. No se modifica estado autoritativo ni se reemplaza la operación de guardar/cargar.

Publicación: [JSON numérico saneado](CE_PICKUP_CYCLE_2026-10-10.json), todas las526 observaciones de pose/cola, recibos que contienen acciones y estados de los casos. Se omiten muestreos duplicados, texto/visor original, censo completo y capturas; saves/DAT/arte permanecen privados. Sólo hashes de SAVE.DAT y DENBUS1.SAV, no sus bytes. Los offsets de funciones privados no se necesitan para leer este informe.

## Matriz del paquete ejecutado

| Corrida | Caso | Observaciones | Resultado medido |
| --- | --- | ---: | --- |
| cycle-03 | Recogida y cola |46| Suelo hasta frame6; primera propiedad observada7, cantidad1, fuera del mapa |
| cycle-04 | Primer intento de cancelar durante gesto |68| Cursor verificado enframe6 sin dueño; al soltar en7 ya es propiedad. Termina en12479 con el ítem. No demuestra cancelación anterior al efecto |
| cycle-05 | Petición de movimiento tras efecto, gesto aún activo |57| Triggerframe7 con propiedad, releaseframe8; termina con una unidad. No revierte transferencia |
| cycle-06 | Segunda petición al mismo arte durante gesto |46| Target nativo200/pid4, releaseframe3 todavía suelo; termina con una unidad |
| cycle-07 | Cancelación temprana preparada y reintento |74| Triggerframe0, press1/release2 aún suelo; llega12479, sin adquisición. Reintento con pulsación adicional recoge una unidad |
| cycle-08 | Guardar antes y cargar tras recoger |105| Save original en13292/suelo; estado intermedio adquirido12478; carga vuelve13292/suelo/inventario vacío. Nueva recogida exitosa |
| cycle-09 | Guardar después y cargar tras mover |60| Save adquirido12478; movimiento intermedio12479; carga devuelve12478 con una unidad y fuera del mapa |
| cycle-10 | Guardar durante gesto y cargar tras recoger |70| Triggerframe0 sin dueño; save cancela gesto y deja suelo. Estado intermedio adquirido; carga devuelve12478/STAND/suelo/sin cola. Nueva petición recoge |

526 son cambios de pose/cola/estado, no526 desplazamientos. La petición postefecto conserva propiedad hasta los estados finales; no prueba todas las posibles interrupciones ni recursos distintos.

## Reconciliación del marcador

FRM hmwarrak declara9frames/8FPS/action_frame4 (hash anterior427d436fbd1dfa17691e52cda178730b5a26712f622484143ab51e60a270da06). La secuencia registrada tiene siete descripciones: aproximación, orientación, callbacks de proximidad/coste, animación10, CONTINUE28 del sonido ausente y callback11 pickup. Los dos últimos registros tienen delays iniciales4. No son un único marcador compartido.

En cycle-03, al inicio visible del gesto el cursor está en5: delay de CONTINUE2 enframe0,1 enframe1 y0 enframe2; pickup mantiene4. Enframe3 el cursor pasa a6 y pickup baja3; frames4/5/6 muestran2/1/0 con el objeto aún en suelo. Primera propiedad observada enframe7: cursor7, callback identificado consumido; frame8 conserva propiedad. Fuente fijada de `animationRunSequence` consume delays sucesivos y `_anim_set_continue` puede volver a entrar en la secuencia. El marcador estático4 no equivale a cuatro cuadros hasta el efecto ni permite sumar dos delays como ocho cuadros exactos.

La cola y propiedad observadas explican el desacuerdo anterior dentro de esta referencia silenciosa. No se instrumenta entrada/salida del callback, así que sigue sin probarse el instante atómico de contacto, ni que se ejecutó exactamente en el primer frame observado. Con sonido cargado, otra revisión, otro ítem/script o EXE Windows hace falta nueva evidencia. No se corrige upstream para hacer coincidir la animación con una expectativa.

## Cancelación y persistencia

El primer intento de interrupción queda como ensayo tardío, no prueba de que CE ignore una petición anterior al efecto. La corrida discriminante prepara el cursor mientras el personaje se acerca: press/release observados enframes1/2, objeto aún en suelo. La acción se anula antes de la transferencia y la nueva orden termina en12479. Reintentar obtiene exactamente una unidad. La segunda petición al ítem durante otro gesto también termina con una unidad; se trata de UI física, no replay transaccional de recibos/IDs.

F6/Return generan archivos nativos privados; F7 vuelve a cargar. Cada carga se compara con un estado intermedio distinto, no con una pantalla que nunca cambió. Se verifica posición y suelo/propietario/cantidad, no equivalencia de todo el mundo, RNG, reloj, NPCs o pose exacta. Después de guardar, la pose observada puede diferir de la pose anterior al pedido: el caso postefecto incluye un frame de idle distinto, pero la carga vuelveSTAND/frame0 con propiedad.

Durante gesto, el save interrumpe la secuencia: suelo,STAND y cola vacía antes de cargar. `map.cc::_map_save_in_game` llama `animationStop`; la fuente coincide con el resultado observado. No se persiste automáticamente la fase/petición pendiente. Vampiro exige definir y comprobar esa persistencia con su autoridad propia; este resultado no satisface por sí mismo ese contrato.

## Verificación, cierre y continuidad

EVIDENCE:66 tests de lectores/rechazos (doce nuevos) y seis guards con identidad de fuentes PASS. Las fuentes medidas de navegación, redirección, puerta, contenedor y primera recogida permanecen congeladas. Parent0dcf279 Research evidence SUCCESS push38085102982/PR38085106275 y Walk proof SUCCESS push38085102956/PR38085106141. No se presume resultado CI del commit nuevo.

```bash
python3 -m unittest discover -s tools/research -p 'test_*.py' -v
python3 tools/research/check_ce_pickup_cycle_evidence.py research/FALLOUT2/CE_PICKUP_CYCLE_2026-10-10.json --check-source-hashes
```

Reproducción privada: `probe_ce_pickup_cycle.py` scenarios complete/cancel-gesture/cancel-after/repeat-gesture; `probe_ce_pickup_interrupt.py --scenario cancel-gesture` para el disparo temprano; `probe_ce_pickup_persistence.py` save-before/save-after/save-gesture. Todos requieren --binary, --ce-source, --inputs, --lab-deps y --output nuevo, más --record-frames. SDL/Xvfb/xdotool/Pillow/g++ y acceso de lectura al hijo. No invocar la variante básica como prueba de cancelación temprana. cycle-01 fue fallo de lanzamiento del auxiliar por PATH antes del runtime; cycle-02 fue la sonda inicial de cola y queda privada, fuera de la identidad del controlador final publicado.

OPEN: A2-01/02/03/05/06/08/09 REFERENCE_PARTIAL; otros cinco casos sin ejecutar y todo Vampiro sin verificar. Instante atómico, replay por recibo, otras fases de save/movimiento y equivalencia del mundo completo siguen pendientes. EXE Windows original, motor productivo, arte/VTM, muestra02 rechazada/tres fallas C preservados. Paquete cerrado sólo para los escenarios medidos; no se cierran A2/A3–A5 completos.

NEXT: paquete espacial de referencia: identificar en un mapa original objetos superpuestos u ocultos y un contacto separado por muro; medir selección/visor, oclusión al recorrer perímetros y acercamiento/negativa de interacción, con capturas y estado nativo. Cerrar una matriz de escenarios A2-06/07/10 con evidencia reproducible o bloqueos concretos. Conservar baselines, no modificar MAP/activos ni elegir motor o integrar reglas para compensar diferencias.
