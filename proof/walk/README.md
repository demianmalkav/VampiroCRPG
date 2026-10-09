# El pasaje — muestra recorrible 01

Python 3.11+ estándar, navegador con canvas. El paquete de entrega incluye todos los PNG. Ejecutar desde la raíz:

    python -m proof.walk --open

En Windows: descomprimir y abrir iniciar-pasaje.cmd. No abrir index.html como archivo. Puerto 8766; consola abierta mientras se juega.

Una escena: clic para caminar, clic en objeto/persona para acercarse y actuar, clic derecho para describir en el visor, I para inventario, Esc para detenerse. La mujer orienta, la llave se recoge desde su posición real, abre la puerta y se cruza el umbral para completar.

Guardar/Cargar conserva rutas, pasos parciales e intención pendiente. La autoridad está en Python, el cliente dibuja/interpola y solicita avance automáticamente al caminar. No hay botones que revelen opciones de escena ni adelanten tiempo. Contrato separado C; A/B no migran ni se alteran.

## Arte editable

El archivo assets/walk/source/style.json fija materiales, altura, cámara, escala y luces. tools/art/build_walk.py crea modelos .blend editables y atlas PNG: idle más ocho cuadros de caminata en ocho direcciones. No se generan imágenes independientes para cada cuadro.

Autoría en Python 3.11: instalar bpy==4.5.14 y Pillow==11.3.0; ejecutar python tools/art/build_walk.py. La entrega incluye exportaciones para jugar sin esas dependencias.

Variación de abrigo regenerada desde style_variant.json:

    WALK_STYLE=assets/walk/source/style_variant.json WALK_OUT=assets/walk/generated/variant WALK_SOURCE=assets/walk/source/variant python tools/art/build_walk.py -- player

Visitar /?look=variant muestra esa exportación sobre la misma sesión. No modifica mecánicas, mapa ni contrato de partida. Perspectiva 88×44; anclajes y escala compartidos. La primera geometría es simple y necesita evolución artística.

## Verificación

    python -m unittest discover -s tests -v
    python qa/walk/check_art.py
    PYTHONPATH=. python qa/walk/check_browser.py

Las dos últimas comprobaciones necesitan dependencias de autoría/QA. El navegador de QA usa Playwright; no es una dependencia de la muestra. El workflow genera arte, ejecuta regresión y mouse real, empaqueta e inicia el paquete descomprimido desde cero. Informes y capturas en qa/walk y tests/results. A/B y sus mediciones históricas se preservan.

Limitaciones: mapa pequeño, percepción por rayo discreto, sin animación del NPC ni sistema general de luces/stealth. Entrada simbólica al refugio, sin segunda pantalla. Motor de producción sin decidir; aceptación estética y de experiencia pendiente de dirección.
