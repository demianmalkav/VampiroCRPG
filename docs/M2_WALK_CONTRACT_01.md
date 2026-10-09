# M2 C — contrato espacial del pasaje

Dirección autorizó una primera muestra recorrible con avatar, inspección y visor de texto. Escenario acotado: encontrar una llave y entrar al refugio. Alimentación, combate y frenesí quedan fuera de este recorrido; A/B y sus informes históricos permanecen sin cambios.

Autoridad separada C, partida `m2-walk-save-1`: mapa 17×13, ocho vecinos, sin cortar esquinas diagonales, costos 10/14 y desempate determinista. Pasos de 300 ms. La presentación solicita avance mientras se camina; no hay botón para adelantar tiempo.

La percepción usa alcance de siete celdas y un rayo discreto con obstáculos opacos. Sólo los objetos actualmente visibles entran en la vista. El visor conserva observaciones adquiridas. El terreno estático y la ubicación conocida del refugio pueden dibujarse desde el inicio.

Inspeccionar describe sin trasladar ni adquirir. Usar solicita una ruta hasta el contacto: la acción sólo ocurre al llegar. Otro destino cancela esa intención pendiente. La llave tiene un único dueño; abre la puerta y entrar físicamente al umbral completa el recorrido.

Guardado: incluye ruta, progreso parcial, intención pendiente, inventario, percepción e historial de órdenes. Cargar reproduce y compara el estado completo; rechaza alteraciones, constantes no finitas, claves duplicadas y mapas/versiones incompatibles. Sesión: revisión y recibos impiden órdenes obsoletas o duplicadas.

Arte: modelos comunes editables, cámara ortográfica a 30°, escala y luces compartidas. Ocho direcciones con idle y ocho cuadros de caminata. Cambiar vestuario/materiales no cambia el mapa ni la partida. Blender/Pillow son herramientas de autoría; la muestra usa PNG ya exportados y Python estándar.

Aceptación: recorrido completo con mouse real, inventario y visor, guardado/carga durante movimiento, regresión A/B, geometría/rutas sin atravesar obstáculos y comparación de vestuario sin cambiar el estado. La calidad estética y la experiencia de dirección se validan al jugar; una primera base gráfica no equivale a arte final.
