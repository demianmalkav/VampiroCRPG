# M2 C — pasaje de Nueva York, resultado 02

Estado: IMPLEMENTED / VERIFIED_LOCAL; CI de la integración c77782b PASS. Aceptación artística y prueba del paquete por dirección pendientes. La ilustración aprobada sigue siendo la referencia de acabado; esta muestra aún no alcanza ese nivel.

## Cambio entregado

Pasaje de servicio ficticio de Manhattan. Revisión dirigida del capítulo urbano de New York by Night, 2001: ciudad y barrios diferenciados; no se fija una dirección canónica ni año exacto de campaña. No se empaquetan páginas del libro.

Se conserva el mapa lógico y la autoridad C. Pavimento, fachadas, ventanas, escalera de incendios, tuberías, luminaria, contenedor y objetos se exportan como recursos separados. Se ajustó el encuadre y las fachadas del fondo; los muros cercanos conservan transparencia de oclusión.

Jugador anatómico con prendas separadas, esqueleto común y clips idle (1), walk (8) y pickup (10), en ocho direcciones: 152 cuadros por vestuario. Contacto con chaqueta y postura diferente; permanece estático. La anatomía parte exclusivamente del recurso CC0 de MakeHuman, fijado por revisión y hash; no se incorpora código de su aplicación. Texturas originales generadas para el proyecto.

Constructor y exportador separados. El exportador abre la fuente guardada, lee sus poses/materiales y no reconstruye geometría. Variante material del abrigo editada en la fuente y exportada sobre la misma sesión. Fuentes .blend empaquetadas con sus imágenes; entradas, licencia y receta preservadas.

Recoger reproduce un gesto al confirmar Python la adquisición. La llave aparece en inventario y sale del mundo una sola vez. El gesto no es autoridad, no añade coste ni persistencia de su fase; cargar/reiniciar lo cancela y mover puede interrumpirlo. Se mantiene `m2-walk-save-1` y no se modifica el mapa ni la autoridad A/B.

## Evidencia medida

- 80 tests de regresión PASS: 59 A/B, 9 del panel y 12 espaciales.
- 152 cuadros en cada abrigo PASS: alpha válido, sin recortes, anclajes/dimensiones comunes, cambio material en todos los cuadros. Las dimensiones de cada recurso y los hashes de sus fuentes coinciden con las exportaciones.
- Ocho comprobaciones con mouse real, Chromium 141.0.7390.0 PASS: visor, recorrido, gesto/propiedad única de llave, guardar andando y reanudar sin repetir el gesto, puerta/umbral, abrigo editado sobre estado lógico idéntico, reinicio y móvil sin desborde. Cero errores JavaScript.
- Carpeta de entrega limpia PASS: servidor local, índice de recursos y descarga PNG completa. Ejecución comprobada en Linux; no se afirma una prueba en Windows.

[CI de c77782b PASS](https://github.com/demianmalkav/VampiroCRPG/actions/runs/38009988143): reconstrucción desde las entradas del repositorio, exportaciones, regresión, navegador y empaquetado. No confundir ese head con los cambios posteriores de cierre medidos localmente.

Informes en `qa/walk/art-result.json`, `browser-result.json`, `package-result.json`, `unit-results.txt`. El snapshot `implementation-manifest.json` identifica por SHA256 los archivos medidos; el atlas/base y su variante también tienen hashes en el informe. Código base de la integración: `c77782be52e3a9b2916e6468bf283b248549e8a0`, con cierre de QA y corrección del tooltip en la revisión de resultados.

La primera comprobación de carga del navegador pudo evaluar la partida anterior mientras File.text() seguía pendiente; el arnés espera ahora el cambio de revisión real antes de comprobar la reanudación. Los errores visuales de rig iniciales y metadatos obsoletos se corrigieron antes de este resultado. Los clips de recoger empiezan/terminan en reposo: no se exige que esos extremos difieran del idle.

## Entrega

[El-pasaje-Nueva-York-muestra-02.zip](https://drive.google.com/file/d/1jSJMEnoBcrmA6WkFvQoEMKg60JocJ159/view?usp=drivesdk), en 09_BUILDS. Incluye runtime, PNG, fuentes editables, exportadores, variante y evidencias. 31,721,264 bytes; SHA256 `f8295e35b072891badd499c863332b5714f6d48d07f94c26716be0610a41be5c`.

Descarga final desde Drive cotejada byte a byte mediante SHA256 y CRC de las 73 entradas ZIP. La carga inicial incompleta fue reemplazada antes de entregar; el ID y enlace conservan la versión íntegra.

Python 3.11+ y navegador local; no requiere Blender ni Godot para jugar. Abrir `iniciar-pasaje.cmd` desde la carpeta descomprimida o `python -m proof.walk --open`. Mantener la consola abierta.

## Límites y siguiente paso

El arte sigue siendo una base de producción, con repetición de módulos y detalle/iluminación por debajo de la referencia conceptual. Las pruebas automáticas verifican integridad y comportamiento; no demuestran excelencia artística. Valorar en movimiento la silueta, legibilidad, ropa, atmósfera y profundidad antes de escalar producción.

No hay cambio de ropa en inventario, armas equipadas, combate por turnos, alimentación espacial, interacción conjunta, vehículo o clima. La puerta sólo tiene dos estados gráficos. Estas capacidades permanecen en la propuesta de expansión; no se deducen de tener un rig.

Próxima iteración acotada: mejorar dirección artística de este mismo pasaje y la silueta/deformación del personaje a tamaño de juego; añadir una interacción animada con reacción del contacto. La prueba de equipamiento será dos vestuarios con silueta distinta y un único arma con icono/agarre coherentes, cuando se especifiquen sus estados. Motor de producción sigue sin decidir. No ampliar ciudad ni catálogo completo antes de validar esta base.
