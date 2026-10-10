# El pasaje — Nueva York, muestra recorrible 02

Python 3.11+ estándar y navegador con canvas. El paquete incluye los PNG para jugar y las fuentes editables de arte. Desde la raíz:

    python -m proof.walk --open

En Windows: descomprimir y abrir `iniciar-pasaje.cmd`. No abrir index.html como archivo. Puerto 8766; mantener la consola abierta mientras se juega.

Clic en suelo para caminar; clic en objeto/persona para acercarse y actuar; clic derecho para mirar y leer el visor. I abre inventario; Esc detiene el recorrido. Una mujer orienta; la llave se recoge desde su posición real, abre la puerta y permite cruzar el umbral.

Guardar/Cargar conserva rutas, pasos parciales e intención pendiente. La autoridad está en Python. El cliente interpola y solicita avance automáticamente al caminar. Contrato C separado; A/B y los saves existentes no se migran ni modifican.

## Arte y animación

Pasaje de servicio ficticio de Manhattan. Se revisó el capítulo urbano de New York by Night (2001); todavía no se fija dirección ni año de la campaña. El acabado y la atmósfera están en evaluación, con referencias de gótico urbano nocturno; no se incluyen imágenes de los libros.

Personaje anatómico con prendas separadas, 8 direcciones y clips idle (1 cuadro), walk (8) y pickup (10). Suelo, fachadas y utilería tienen fuentes y exportaciones independientes. Ver `assets/walk/source/NY_README.md` para reconstruir o reexportar una fuente editada. Blender, bpy y Pillow son herramientas de autoría, no dependencias del juego.

El catálogo PNG declara cuadros, duración y anclaje por acción. El gesto de recoger empieza cuando Python confirma la adquisición. Es una representación visual: no retrasa la entrega del objeto ni añade una segunda consecuencia. Cargar/reiniciar cancela el gesto; no se guarda su fase visual. Un nuevo movimiento puede interrumpirlo. Estas decisiones evitan convertir una animación en autoridad de reglas; una futura acción cronometrada necesitará su propio contrato.

La variante `/?look=variant` demuestra una edición del material del abrigo sobre la misma partida. No es todavía una función de cambiar ropa en el inventario. Armas visibles, armaduras, combate por turnos, interacciones entre personas, vehículos y clima siguen pendientes de implementación.

## Verificación

    python -m unittest discover -s tests -v
    python qa/walk/check_art.py
    PYTHONPATH=. python qa/walk/check_browser.py
    python qa/walk/package.py

QA de arte necesita Pillow; el recorrido con mouse real necesita Playwright y Chromium. Opcionalmente `CHROMIUM_PATH` especifica un ejecutable instalado. El workflow reconstruye las fuentes con entradas fijadas, exporta los clips, prueba la variante, ejecuta la regresión y empaqueta/inicia desde una carpeta limpia.

Limitaciones: escena pequeña, iluminación preexportada, NPC estático, puerta con dos estados gráficos, entrada al refugio sin segundo escenario. No integra sangre/hambre/frenesí del prototipo A/B. Motor de producción sin decidir; aceptación artística pendiente de dirección.
