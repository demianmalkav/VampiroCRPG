# A2 — CE ejecutado: arranque y desplazamiento comprobados

Estado: **STARTUP_VERIFIED / A2_ACCEPTANCE_PENDING**, 2026-10-10. Padre lógico: `7f6fa2e58ca0f715ee05da0d3acef256af103a68`. [Evidencia medida](CE_EXECUTABLE_LAB_2026-10-10.json) · [herramienta propia](../../tools/research/run_fallout_ce_lab.py).

## Qué quedó comprobado

Fallout 2 CE compiló y se ejecutó con los DAT privados aportados por dirección. Tres arranques independientes con carpetas nuevas llegaron a menú, selección de Narg y NCR1. Se capturaron las pantallas y se leyó, sin escribir memoria, la autoridad nativa del proceso: `gMapHeader.name=NCR1.MAP`, versión 20, índice 42, elevación 0. En los tres recorridos un clic cambió al mismo actor, ID 18000, de tile **13915 a 14517**; las capturas muestran su desplazamiento. El proceso siguió vivo al terminar cada observación. Los tres archivos DAT conservaron sus SHA256.

Esto cierra el requisito previo de arranque y evidencia visual; **no aprueba ninguno de los doce casos completos A2**. Un desplazamiento aislado no demuestra bloqueo, redirección, contacto, selección, fases, reloj o persistencia. La muestra 02 y sus tres fallas permanecen abiertas.

## Referencia activa

| Componente | Identidad y condición |
| --- | --- |
| CE | `alexbatalov/fallout2-ce` @ `e97087b9582f37075db347a89898887320753f8b`; checkout limpio, fuente sin cambios. |
| fpattern | `alexbatalov/fpattern` @ `8523173ec252c3b796fcdfca0fcc6329642fbbe3`; checkout limpio. |
| Ejecutable Linux x86-64 | SHA256 `70516cf855af0b8a5c826b0f090f646b29e5672c48e9b981322448edc6dc636c`. C++17, RelWithDebInfo, bibliotecas del sistema, vendorización desactivada. |
| Compilación | GCC 13.3.0, CMake 3.28.3, SDL2 2.30.0, zlib 1.3. Paquetes exactos en JSON. |
| DAT activos | master, critter y patch000 con los hashes ya registrados; sin f2_res.dat ni DLLs originales. |
| Mapa inicial | NCR1 del parche, SHA256 `11464ce6dd1f5d374523b470ddb7590419d1a88cef72c34c8199fe71bfd01e00`. No archivos MAP/SAV previos en la carpeta nueva. |
| Configuración de laboratorio | 800×600, ventana, sin escala 2×; `StartingMap=NCR1.MAP`, `SkipOpeningMovies=1`; sonido desactivado, caminar, velocidad de combate 0. |
| Automatización | Xvfb 21.1.12 y xdotool; SDL usa modo relativo por warp para las entradas XTEST. El clic mantiene botón 200 ms para que CE lo muestree. |

`language=english` selecciona el árbol de recursos; el menú y varias etiquetas suministrados aparecen en castellano. No se infiere una instalación US limpia a partir del readme. CE interpreta opciones de ddraw.ini, pero no ejecuta el sfall 2.19a ni Hi-Res 4.1.8.0 del Windows original. No se copiaron las carpetas de overrides sueltos de aquella instalación: este es un laboratorio DAT-only explícito, no una reproducción íntegra de ese entorno modificado.

## Reproducción

Requisitos: git, C/C++, CMake, pkg-config, SDL2 y zlib de desarrollo, Xvfb, xdotool y Python con Pillow. DAT privados con identidad comprobada, sin publicarlos. Preparar dos checkouts privados y fijarlos:

```bash
git clone https://github.com/alexbatalov/fallout2-ce.git fallout-reference/ce
git -C fallout-reference/ce checkout --detach e97087b9582f37075db347a89898887320753f8b
git clone https://github.com/alexbatalov/fpattern.git fallout-reference/fpattern
git -C fallout-reference/fpattern checkout --detach 8523173ec252c3b796fcdfca0fcc6329642fbbe3
cmake -S fallout-reference/ce -B fallout-reference/build -DFALLOUT_VENDORED=OFF -DCMAKE_BUILD_TYPE=RelWithDebInfo -DFETCHCONTENT_SOURCE_DIR_FPATTERN="$(realpath fallout-reference/fpattern)"
cmake --build fallout-reference/build -j 2
python tools/research/run_fallout_ce_lab.py --binary fallout-reference/build/fallout2-ce --ce-source fallout-reference/ce --inputs fallout-reference/private --output fallout-reference/private/new-run --move-smoke
```

`--output` debe ser nuevo: la herramienta rechaza sobrescribirlo. Crea configuración y data propios y enlaza los DAT; registra hashes antes y después. Servidor X y clientes deben compartir una ejecución/namespaces; aquí los sockets UNIX están bloqueados y se utilizó TCP local autorizado, puerto 33875 (`--display 27875`). La sonda sólo resuelve al hijo directo con ese ejecutable y lee los campos de MAP/Object de la revisión fijada. Las capturas y los archivos generados por CE quedan privados; se publican únicamente herramienta, metadatos y análisis.

## Incidencias y alcance de la evidencia

La preparación APT necesitó usuario root sin cambio de privilegios y caché temporal escribible. El primer link encontró un objeto settings.cc.o con cabecera nula: se eliminó sólo ese objeto y se recompiló en serie; link final PASS. Causa de la corrupción UNVERIFIED. La compilación inicial produjo 44 advertencias; no se corrigió código upstream.

La sonda inicial falló por diferencias entre PID del contenedor y montaje proc, y por ausencia de children; se resolvió con PPid/NSpid/identidad de ejecutable. Un primer clic instantáneo no movió al actor: se conserva esa observación negativa, y se corrigió el adaptador de entrada según dinput.cc. Tres ejecuciones posteriores comprobaron desplazamiento. Once tests sintéticos de los lectores DAT/MAP siguen PASS; no se presentan como pruebas conductuales.

Los tiempos del JSON son tiempos de pared y esperas de automatización, no duración lógica de una acción. Las lecturas de memoria no detienen el proceso: no sirven como transacción atómica. Sonido/música no medidos. Se detuvo con SIGTERM después de observar; cierre normal y guardado no verificados. EXE original/Windows no ejecutado. Motor productivo, arte propio y reglas vampíricas siguen pendientes.

## NEXT

Medir una unidad acotada **A2-01/A2-02: geometría y bloqueo nativos de NCR1**. Identificar tiles/objetos concretos de suelo libre, muro, contenedor y actor; registrar destinos de entrada, huella/flags, estado previo y posterior, ruta/animación y capturas. Comprobar seis direcciones y destino sólido frente a rodeo. Cerrar sólo los casos cubiertos; después continuar redirección y demás casos previstos. No reabrir transferencia, instalación general ni encuesta de motores.
