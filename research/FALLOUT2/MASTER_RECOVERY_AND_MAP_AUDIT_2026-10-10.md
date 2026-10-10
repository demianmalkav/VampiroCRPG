# Master recuperado y mapa urbano inspeccionado

Fecha: 2026-10-10 Argentina. Estado: `A2_INPUT_TRANSFER_RESOLVED_STATIC_MAP_AUDIT_COMPLETE_RUNTIME_NOT_EXECUTED`. Parent lógico: `f7f45e416585ebeeeb786564b204684eb3b9ebe5`. Dirección aportó dos volúmenes RAR en la carpeta privada de Fallout 2 y pidió continuar con Game Reconstruction. Se aplicó el método al perfil real VampiroCRPG; no se transportaron datos o decisiones del perfil TrueRecall del plugin.

## Transferencia cerrada

| Entrada | Bytes | SHA256 |
| --- | ---: | --- |
| `master.part1.rar` | 178.257.920 | `526e8c8c040cd8b6a8b6337ddb8151cd2def011fe0a713cf03c1b37b80d0e75f` |
| `master.part2.rar` | 149.208.726 | `0c50d1929d720fe2df985a43439c35612c679ef46e778a0f4a1153849d5f5489` |
| `master.dat` reconstruido | 333.177.805 | `9b096d3035edafd4077deeb8ee7877a803b9db98497aa4596624b5c058a84711` |

Ambas partes fueron descargadas por el conector autenticado de Drive. `libarchive 3.7.2` reconoció RAR5 y leyó una sola entrada `master.dat`, con el tamaño esperado, hasta EOF sin error. MD5 obtenido: `5acf4f9a8bb017af0f7b35c7f920a48b`. El tamaño coincide con la entrada original en Drive; el conector no expuso su checksum, por lo que no se declara una comparación independiente de hashes con ese archivo ni autenticidad de distribución.

La prueba negativa con sólo el primer volumen fue rechazada por la biblioteca, sin publicar archivo final. El wrapper rechaza sobrescribir una referencia existente; el SHA256 del master permanece igual después de las pruebas. El bloqueo 413 de la descarga directa queda **resuelto mediante los volúmenes**; no volver a pedir este archivo o la instalación completa al usuario.

Herramienta de recuperación propia: [recover_master_rar.py](../../tools/research/recover_master_rar.py), usa la biblioteca de sistema ya presente, sin instalar dependencias. Comando desde raíz del repo, con datos privados fuera de él:

```bash
python tools/research/recover_master_rar.py /ruta/privada/master.dat 333177805 /ruta/privada/master.part1.rar /ruta/privada/master.part2.rar
```

## Lectura real del archivo

El lector DAT propio recorrió **23.140 entradas**: índice, límites, unicidad de rutas, lectura de todos los contenidos e inflación zlib. Cero errores dentro de esas comprobaciones. El footer declara 944.706 bytes de árbol y 333.177.805 bytes de archivo, base de datos 0, rutas ordenadas sin distinción de mayúsculas.

Incluye 155 MAP, 7.650 PRO, 8.071 FRM, 1.443 INT, 833 MSG y 23 LST, entre otros recursos. Se leyeron cabeceras de todos los MAP/PRO y **10.774 registros de cuadros** de sus FRM. Inventario y resultados acotados: [evidencia JSON](MASTER_RECOVERY_AND_MAP_AUDIT_2026-10-10.json). No confundir estos conteos con porcentaje de comprensión ni con gameplay verificado.

Los archivos anteriores necesarios para comparar se recuperaron tras limpieza automática del espacio temporal. `critter.dat` y `patch000.dat` conservan los hashes registrados en la inspección previa. GitHub/Drive preservaron el trabajo anterior: no se repitió la implementación ni su commit.

## Dependencias y objetos: NCR1

Se escribió un [lector estático MAP](../../tools/research/inspect_fallout_map.py) independiente, que consume variables, tiles, scripts, objetos y objetos de inventario anidados. PID resuelve por la línea correspondiente de PRO/LST; no se inventa el nombre de archivo desde el número. FID y sus listas conectan instancia y representación; scripts se resuelven por su lista. Esta herramienta no ejecuta scripts ni modifica el mapa.

| Medida en `maps/NCR1.MAP` | Versión de `master.dat` | Versión de `patch000.dat` |
| --- | ---: | ---: |
| Bytes consumidos, EOF exacto | 349.080 | 353.040 |
| Objetos principales | 3.230 | 3.275 |
| Objetos anidados en inventarios | 163 | 163 |
| Muros | 1.644 | 1.649 |
| Escenografía | 1.050 | 1.090 |
| Personajes | 51 | 51 |
| Ítems principales | 37 | 37 |
| Puertas | 32 | 32 |
| Referencias de dependencia existentes | 1.098 | 1.098 |

En ambas versiones hay 448 objetos misc, 27 scripts de ítem y 51 de critter. No quedaron referencias ausentes **dentro de la resolución implementada**: prototipos/listas, gráficos no-critter/tiles, archivos de texto por tipo y programas INT referenciados. Para critters se resuelven diecisiete nombres base; no todos sus clips/armas/direcciones. La existencia de un MSG no verifica cada texto solicitado; la existencia de un INT no demuestra qué hará al entrar al mapa.

Las puertas almacenan una con `open_flags=1` y `NO_BLOCK`, y 31 con `open_flags=0` y sin `NO_BLOCK`. Son estados de archivo: los scripts todavía pueden cambiarlos al cargar. No se midió caminar, abrir, bloquear o alcanzar un objeto en el motor.

**La revisión cambia el mundo.** El parche agrega cuarenta objetos de escenografía y cinco muros frente al mapa base. En una puerta de referencia, tile 15061, el objeto tiene id 127 en el base y 300 en el parche. Una prueba debe identificar el mapa y su hash, no conservar IDs/offsets aislados como si fueran universales. El parche es la referencia estática de trabajo por prioridad de DAT; `data/maps` se comprobó vacío. Se comprobaron también vacías las carpetas sueltas de PRO/items y PRO/critters. Otros overrides no se declaran exhaustivamente auditados.

**Los slots de scripts no se saltan por el tipo de lista.** CE `scriptRead` decide los campos opcionales por el SID de cada slot, incluso los slots sin usar de un bloque de dieciséis. NCR1 contiene trece slots cuyo tipo SID difiere del de la lista. El lector respeta el SID; una prueba sintética con un script espacial y quince slots de sistema confirma el caso de tamaños distintos. Este matiz limita la simplificación de tamaño fijo por lista de algunas recetas del formato.

## Reproducción y evidencia

```bash
python -m unittest discover -s tools/research -p 'test_inspect_fallout_*.py'
python tools/research/inspect_fallout_dat.py /ruta/privada/master.dat --output /ruta/privada/master-audit.json
python tools/research/inspect_fallout_map.py --dat /ruta/privada/master.dat /ruta/privada/critter.dat /ruta/privada/patch000.dat --map maps/NCR1.MAP --output /ruta/privada/ncr-patched-audit.json
python tools/research/inspect_fallout_map.py --dat /ruta/privada/master.dat /ruta/privada/critter.dat --map maps/NCR1.MAP --output /ruta/privada/ncr-base-audit.json
```

Once pruebas sintéticas PASS: seis del DAT/FRM previo y cinco MAP (EOF exacto, SID de slots sin usar, inventario recursivo y cantidad, conteo total inconsistente, truncamiento/bytes sobrantes). Las dos versiones reales de NCR1 llegan al último byte con sus conteos reconciliados. También se consumió `denbus1.map` del parche hasta EOF: 351.640 bytes, listas con 22 scripts de ítem y 70 de critter; comprobación auxiliar sin índice visual ni comparación conductual.

Fuentes primarias fijadas: `rotators/fallout2-docs` `fa5b3a90b342975998f10e270c5cd7f5293af9e9`, MAP/PRO; CE `e97087b9582f37075db347a89898887320753f8b`, `scripts.cc:scriptRead`, `object.cc:objectRead/objectLoadAllInternal`, `proto.cc:objectDataRead/objectCritterCombatDataRead`, `proto_types.h` (exit grids). Código de terceros sólo leído para contrastar; los nuevos lectores son propios. Los binarios y recursos originales se mantienen privados y no se publican.

## DONE / EVIDENCE / OPEN / NEXT

**DONE:** recuperación del estado vivo, partes descargadas, master reconstruido con identidad registrada, 23.140 entradas verificadas, lector de objetos/dependencias y comparación NCR1 base/parche. Bloqueo de datos cerrado.

**EVIDENCE:** JSON, comandos, once tests sintéticos, EOF exacto y conteos de mapas, rechazo de volumen faltante/sobrescritura y hash de referencia inalterado. Evidencia estática, no ejecución del motor.

**OPEN:** no se ejecutó EXE ni se construyó CE; doce casos A2 permanecen NOT_EXECUTED. En el entorno se encontraron compiladores C/C++, pero no Wine, CMake, pkg-config, Xvfb, SDL2 ni sus headers. Preparar la ejecución sigue siendo trabajo técnico; no confundir disponibilidad de datos con arranque. Versión exacta del EXE, extensiones efectivamente activas y overrides restantes se medirán al preparar referencia. Las fallas de C siguen sin corregir; arte/reglas/inventarios de Vampiro no integrados; motor productivo sin elegir.

**NEXT:** preparar un laboratorio ejecutable aislado con CE fijado y estos inputs; cerrar primero arranque reproducible, registro de versiones/overrides activos y evidencia visual de NCR1. Después ejecutar los doce casos A2, separando original, CE y políticas nuevas. No reabrir transferencia ni encuesta general. Para usar la ubicación en pruebas, mantener el hash de mapa y evitar asumir que la lista de 1.098 dependencias constituye un paquete mínimo completo. No publicar recursos originales ni cambiar la instalación del usuario.
