# Inspección de la instalación privada — primer avance de A2

Estado: `A2_RESOURCE_INSPECTION_COMPLETE_RUNTIME_NOT_EXECUTED`. Fecha: 2026-10-10 UTC / 2026-10-09 Argentina. El usuario subió la instalación descomprimida, archivo por archivo. **El acceso y la lectura funcionan:** se descargaron 15 archivos, 172.607.199 bytes, y se inspeccionaron recursos reales. El bloqueo general del RAR ya no impide comenzar. Motor productivo todavía sin elección; A2 conductual sigue abierto.

Referencia privada: [carpeta Fallout 2](https://drive.google.com/drive/folders/1yStYnSN1fpqGkUFyEVSBPY1Ug5VY4XTp). [Evidencia de inspección](INSTALLATION_INSPECTION_2026-10-10.json) registra tamaños, SHA256, alcance y resultados. Los originales siguen como referencia privada: no se incorporan ejecutables, imágenes, mapas, scripts ni textos del juego al proyecto.

## Identidad y configuración comprobadas

| Componente | Evidencia del archivo recibido | Alcance |
| --- | --- | --- |
| Juego base | `readme.txt` declara parche final US 1.02d; `FALLOUT2.EXE` descargado y hasheado | Versión exacta del ejecutable todavía `UNVERIFIED`: no tiene el recurso fijo de versión encontrado en las DLL y no se ejecutó. |
| sfall | Texto de DLL `SFALL 2.19a`, readme 2.19a y versión fija PE 2.19.1.0 | El comentario inicial del INI dice v2.18; no usarlo como versión de la DLL. No es el sfall actual inventariado en la investigación. |
| Alta resolución | DLL: Fallout 2 High Resolution Patch, versión 4.1.8.0 | Archivo y configuración comprobados; activación efectiva en runtime pendiente. |
| Ficha previa | Declaraba 1.02d + 1.02.31 | El segundo número no queda identificado por esta inspección. No atribuirlo automáticamente a sfall. |

`fallout2.cfg`: recursos principales `master.dat` y `critter.dat`; ambas raíces de parches apuntan a `data`; inglés; `interrupt_walk=1`. Esto es configuración, no una prueba de interrupción continua.

`ddraw.ini`: modo gráfico 0, ajuste de velocidad habilitado e inicial 100 %. `f2_res.ini`: modo gráfico 2, 1024×768, color 32 bits, pantalla completa, sin escala 2×. No extrapolar tiempos o comportamiento de CE a esta combinación sin medirlos.

La instalación recién creada incluye extensiones y archivos sueltos. Eso es compatible con una instalación limpia **del paquete recibido**; no equivale a un ejecutable clásico sin extensiones. No se modificó ningún archivo de referencia.

## Recursos que realmente se abrieron

| Archivo | Bytes | Entradas leídas y verificadas | Contenido relevante |
| --- | ---: | ---: | --- |
| `critter.dat` | 166.951.131 | 7.120 | 4.149 FRM, 2.970 archivos direccionales FR0–FR5 y una lista. |
| `patch000.dat` | 2.896.671 | 489 | 445 scripts INT, quince mapas, tres prototipos, una lista y otros recursos. |
| `f2_res.dat` | 651.823 | 177 | Recursos de interfaz/alta resolución; dieciséis FRM y otros archivos. |

Se verificaron límites del índice, nombres únicos, tamaños, lectura de datos e inflación zlib de todas las entradas: **7.786**, sin errores en las comprobaciones implementadas. Además se recorrieron **224.382 registros de fotogramas**: cabeceras, dimensiones y límites de píxeles, con lectura de FPS, offsets y marcadores. Esto no certifica autenticidad de distribución, apariencia correcta ni comportamiento del motor.

Herramienta propia: [inspect_fallout_dat.py](../../tools/research/inspect_fallout_dat.py), Python estándar, sólo lectura. Referencia del formato: `rotators/fallout2-docs` fijado en `fa5b3a90b342975998f10e270c5cd7f5293af9e9`, páginas DAT/FRM/MAP/PRO; contraste del cargador en CE `e97087b9582f37075db347a89898887320753f8b`, `src/art.cc`.

## Hallazgos aplicables a Vampiro

**Animación y contacto tienen datos concretos.** En `HMJMPSAB.FRM`: ocho cuadros por dirección, seis bloques direccionales y 10 FPS. En `HMJMPSAL.FRM`: once cuadros por dirección, seis bloques, 8 FPS y marcador 8. La asociación AB a caminar y AL al gesto de interacción se conoce por la fuente de resolución de animaciones; la lectura binaria confirma sus metadatos. No se observó todavía el contacto en ejecución. Los offsets por fotograma varían: reproducir únicamente imágenes centradas omitiría parte del movimiento registrado.

**Un lector demasiado estricto puede romper recursos válidos.** Los 2.970 archivos FR0–FR5 tienen tamaño declarado de área distinto del físico. En la familia `HAPOWRBA.FR0`–`.FR5`, los seis repiten 214.923 bytes de área y la suma de las áreas físicas es exactamente 214.923. El primer auditor asumía igualdad por archivo y los rechazaba; se corrigió esa suposición, conservando validación de todos los cuadros contra los bytes físicos. No se concluye que el juego o los archivos estén rotos.

**La apariencia clásica usa animaciones ya rasterizadas.** El archivo contiene personajes y variantes finalizados como píxeles; no encontramos aquí un rig editable o prendas superpuestas. La inspección confirma el formato, no garantiza que cambiar ropa o distinguir dos armas de la misma categoría sea barato. Para nuestras exigencias de equipo visible, adoptar el motor y diseñar la producción de arte son trabajos distintos.

**Ya hay material de ubicación para preparar el laboratorio.** Los quince MAP del parche tienen versión 20 y cabeceras que distinguen variables locales/globales, script de mapa, entrada y elevaciones. Se inspeccionaron sólo las cabeceras; no se reconstruyeron objetos, puertas, colisiones ni dependencias completas. `Maps\\NCR1.MAP` es un candidato urbano disponible, no una microescena ya validada. Los PRO inspeccionados incluyen dos critters de 416 bytes y un objeto de 81 bytes; se registraron PID, FID y referencia de texto, sin afirmar interpretación completa de sus subtipos.

**Los archivos sueltos cuentan.** Se listaron diecinueve INT bajo `data/scripts`. `ncPerson.int` y `ncJunkie.int` se descargaron: sus bytes coinciden con las entradas homónimas de `patch000.dat`. Esto sólo verifica esos dos archivos; no acredita equivalencia de todo el árbol ni de sus comportamientos.

## Validación reproducible

```bash
python -m unittest discover -s tools/research -p test_inspect_fallout_dat.py
python tools/research/inspect_fallout_dat.py /ruta/privada/critter.dat /ruta/privada/patch000.dat /ruta/privada/f2_res.dat --output /ruta/privada/resource-audit.json
```

Seis tests con recursos sintéticos propios pasan: datos comprimidos/sin comprimir y prefijo, límites del índice, tamaño inflado/límite de salida, basura al final del stream zlib, área compartida entre direcciones y píxeles truncados. No requieren archivos de Fallout ni cambian el juego.

## DONE / EVIDENCE / OPEN / NEXT

**DONE:** acceso archivo por archivo; 15 descargas con hashes; identificación de extensiones; tres DAT abiertos y contenidos validados; inspección estructural de animaciones, cabeceras MAP/PRO y dos scripts sueltos comparados; herramienta propia y seis pruebas.

**EVIDENCE:** informe JSON y comando reproducible. Evidencia privada leída directamente; fuentes de formato ya fijadas. No build o CI de un motor externo, ni nueva prueba artística.

**OPEN:** `master.dat` tiene 333.177.805 bytes: el fetch autenticado devuelve 413 porque supera 268.435.456 bytes. La lectura de la instalación es por tanto **parcial**, no inaccesible. La lista de `data/ART/INTRFACE` llega a cien entradas: no se declara exhaustiva. En este entorno no se encontraron Wine, CMake, pkg-config ni Xvfb; no se ejecutó el EXE ni se construyó CE. Los doce casos A2 permanecen `NOT_EXECUTED`. Las tres fallas de C siguen abiertas; reglas vampíricas todavía no integradas al motor gráfico.

**NEXT:** completar la ruta soportada para `master.dat` y el entorno ejecutable, preservar hashes, fijar qué extensiones estarán activas y registrar arranque ORIGINAL/CE. Usar un mapa urbano acotado para contrastar bloqueo, cambio de destino, acercamiento y punto de acción contra los doce casos de A2. Obtener dependencias reales por PID/FID/listas antes de reconstruir objetos o afirmar colisiones. No reabrir la encuesta amplia ni pedir otra instalación completa; si el cierre requiere una intervención del usuario, precisar el único archivo o paso que falta. Después: A3 fases/persistencia y A4 comparación de base productiva con arte propio.
