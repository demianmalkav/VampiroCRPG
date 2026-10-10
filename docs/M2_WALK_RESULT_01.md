# M2 C — El pasaje

Estado: IMPLEMENTED / BROWSER_AND_PACKAGE_VERIFIED / PLAYER_ACCEPTANCE_PENDING.

Una escena recorrible con avatar: clic en suelo traza rutas, evita sólidos y esquinas; clic derecho describe personas/objetos en el visor; clic en un objeto solicita aproximación y actúa sólo al alcanzarlo. La llave tiene dueño único y abre la puerta; cruzar físicamente el umbral completa el objetivo. Guardar/cargar conserva ruta, paso parcial, intención pendiente, inventario y observaciones. El cliente interpola; la autoridad espacial permanece en Python.

## Evidencia

Código verificado: 05454dfb85e6c19e51c1976aa4a821c6828c8e90.
[Workflow completo PASS](https://github.com/demianmalkav/VampiroCRPG/actions/runs/37993656561).

80 tests PASS: 59 A/B históricos, nueve del panel de reglas y doce del contrato espacial. Regresión adicional del suite B: 59 pruebas y siete escenarios PASS. A/B, sus esquemas y sus informes originales permanecen sin modificaciones.

Navegador real con mouse: ocho comprobaciones PASS: inspección en visor, ruta con obstáculos, recogida/inventario, guardar a mitad de movimiento y continuar al cargar, puerta/entrada, vestuario regenerado con estado idéntico, reinicio y disposición móvil sin desborde horizontal. Cero errores JavaScript en el recorrido corregido.

72 cuadros por vestuario: idle y ocho cuadros de caminata en cada una de ocho direcciones. El cambio de un material regenera los 72 cuadros; anclajes y dimensiones permanecen iguales. Variante observada dentro de la misma escena con estado autoritativo idéntico.

Paquete descomprimido en carpeta nueva inicia el servidor, carga mapa e imágenes. Python 3.11 estándar más PNG exportados; Blender/Pillow sólo para autoría. Muestra Windows/macOS/Linux entregada como fuentes con lanzador Windows; no es un .exe ni una prueba de ejecución en Windows.

La primera ejecución de navegador completó el recorrido pero detectó errores al dibujar mientras la cámara se reiniciaba. Se añadieron guardas durante carga/reinicio y la ejecución completa siguiente pasó. El entorno local se desconectó; el código y la receta de arte se conservaron y las pruebas se completaron en CI.

## Entrega y continuidad

[El-pasaje-muestra-01.zip en Drive](https://drive.google.com/file/d/1EO6JA-I2w6Z9bWltBX-_RZqawpDRVscQ/view?usp=drivesdk), carpeta 09_BUILDS. Incluye modelos .blend, materiales, receta de exportación, PNG, variante de abrigo y capturas/informes de comprobación. El repositorio versiona la receta; las exportaciones completas están en el paquete y en el artefacto Walk-art-source del workflow.

Arte todavía simple: base de proporciones/cámara/materiales comunes, no acabado urbano gótico final. Percepción discreta, mapa pequeño y un objeto de inventario; sin segunda escena interior, combate, alimentación o frenesí integrados. No se instaló Godot ni se decidió motor de producción.

NEXT: dirección juega la muestra y aporta criterio sobre recorrido/inspección/visor y distancia de la estética buscada. Corregir observaciones concretas antes de ampliar el escenario. No reabrir A/B ni agregar más sistemas por conjetura. El mantenimiento de controles sigue delegado.
