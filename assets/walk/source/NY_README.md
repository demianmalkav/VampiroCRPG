# Nueva York — fuentes artísticas 02

`ny-player.blend` y `ny-contact.blend` contienen un modelo anatómico, prendas separadas y un esqueleto compartido. `ny-environment.blend` agrupa recursos independientes: fachadas, puerta, contenedor, escalera de incendios, tuberías y pavimento. Las fuentes editables están incluidas en la entrega de Drive; GitHub conserva la receta y sus entradas verificables.

Autoría: Python 3.11, bpy 4.5.14 y Pillow 11.3.0. Para reconstruir desde el repositorio:

    python tools/art/prepare_ny.py
    python tools/art/build_ny_source.py
    python tools/art/export_ny.py assets/walk/source/ny-player.blend
    python tools/art/export_ny.py assets/walk/source/ny-contact.blend
    python tools/art/export_ny.py assets/walk/source/ny-environment.blend

**Para exportar una fuente que editaste, usá sólo `export_ny.py`.** `build_ny_source.py` crea fuentes nuevas y reemplaza las existentes; no es el exportador. El exportador lee las poses y los materiales guardados, conserva el archivo original y aplica la cámara fija del contrato isométrico. Podés editar geometría, materiales y curvas; mantener nombres de colecciones, rig y metadatos `export_manifest`.

Clips del jugador: idle (1 cuadro), walk (8) y pickup (10); ocho direcciones. Marcos de registro compartidos; catálogo de clips en el índice PNG. Cada prenda es una malla separada vinculada al mismo esqueleto. Todavía no hay equipamiento intercambiable en el juego ni montajes de armas.

Prueba de edición: `python tools/art/variant_ny.py` modifica el material del abrigo en la fuente guardada, sin regenerar geometría. Exportar `ny-player-variant.blend` con `--out assets/walk/generated/variant` y visitar `/?look=variant`.

La anatomía utiliza sólo el recurso CC0 de MakeHuman, no código de su aplicación. Procedencia, revisión y hashes en `ny-provenance.json`; licencia original en `MAKEHUMAN_LICENSE.md`. La textura de materiales es un recurso original generado para este proyecto. No se distribuyen imágenes ni páginas de los libros de referencia.
