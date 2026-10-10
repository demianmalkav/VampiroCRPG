# M2 — presentación mínima 01

Estado: IMPLEMENTED / INTEGRATION_VERIFIED / BROWSER_LAYOUT_UNVERIFIED / SPATIAL_GAME_EXPERIENCE_NOT_ACCEPTED.

Dirección probó la inicialización y aclaró que el panel no corresponde al formato buscado: quiere recorrer un mundo con avatar e inspeccionar su entorno, con descripciones en un visor de texto. El navegador como ejecutor es aceptable; el diseño centrado en botones no constituye la experiencia objetivo. Las mediciones siguientes prueban integración de reglas, no cumplimiento del juego espacial.

La escena isométrica provisional usa el núcleo A/B existente a través de un servidor Python de biblioteca estándar, limitado a loopback. HTML/CSS/canvas presentan información y envían decisiones; no calculan sangre, Bestia, voluntad, moralidad o investigación. No se instaló Godot ni se eligió motor de producción.

## Resultado medido

[Informe](../tests/results/m2_scene_run.json): **68 tests PASS**, 0 fallos y 0 errores: 59 regresiones A/B y nueve pruebas de escena; siete escenarios B siguen PASS. Los informes históricos A/B no se reemplazaron. `python3 qa/scene/check.py` reproduce esa medición.

[Interfaz](../tests/results/m2_scene_ui_run.json): **PASS en ocho comprobaciones** del JavaScript real con arnés DOM/canvas y servidor real: cambiar situación, alimentación, retirada pagada, descarga de save, carga por archivo, completar acción lúcida, muerte/pérdida de Humanidad y emisión del dibujo. No es una prueba de layout ni un navegador. Node se usa sólo para este ensayo; jugar requiere únicamente Python y navegador.

| Decisión real | Consecuencia verificada |
| --- | --- |
| Objetivo conservador de 2, avanzar y sellar | Reserva 4 antes de la segunda noche; adulto con 8; marcas cerradas; registro/recuerdos conservados. |
| Frenesí, primera extracción y retirada lúcida | Voluntad 4; adulto vivo en emergencia médica; reserva 5; llegada al refugio y control NORMAL a s15. |
| Frenesí sin intervención | Adulto muerto; reserva 10; Humanidad 6; control NORMAL a s18. |
| Guardar durante la retirada y cargar en una sesión de otro modo | Perfil correcto reconstruido; mundo/cola/RNG/recursos idénticos; mismo resultado y un único pago. |
| Reenviar la petición pagada | Mismo recibo; ningún pago o efecto adicional. Una revisión vieja nueva se rechaza. |
| Alterar voluntad en un save o enviar una acción de ensayo arbitraria | Rechazo; mundo y revisión originales conservados. |
| Encargar retirada, dormir, regresar y esperar | Copia institucional continúa en el mundo; el jugador sólo recibe el informe de su contacto y percibe la visita tras regresar. |
| Consultar vista/acciones repetidas veces | Estado, recursos y RNG no cambian. Información institucional, reservas de víctima, dados y actores fuera de escena no se exponen. |

## Qué queda pendiente

El entorno no tenía ejecutable Chromium; la descarga automatizada devolvió archivos inválidos. **Layout CSS, apariencia en navegador, controles de teclado en navegador y accesibilidad completa: UNVERIFIED**. No se creó una captura de navegador ni se presenta el arnés como sustituto de ella. Verificar escritorio/móvil y jugar las rutas descritas en las instrucciones es el siguiente paso de presentación.

La vista asume percepción directa de actores activos presentes en un lugar pequeño; no resuelve oclusión, iluminación, sigilo o percepción general. La condición de la víctima deriva de observación adquirida. Posiciones de muñecos y baldosas son geometría de dibujo, no navegación ni autoridad espacial. No hay ítems/inventario, combate, movimiento libre o arte definitivo. El tiempo avanza manualmente y está limitado a s86460.

Los modos reconstruyen fixtures interactivos con sólo la frontera nocturna inicial. No incluyen retirada, alimentación, sueño, encargo o resultados decididos por el adaptador. El modo de presión identifica sus dados de ensayo. Los saves descargados son privados y contienen el mundo completo; la vista ordinaria usa una proyección restringida. La envoltura de presentación versiona modo+snapshot sin cambiar el esquema B.

La experiencia, ritmo y balance siguen sin aceptación de dirección por práctica. El usuario delegó decisiones técnicas/control de progreso; no se requiere una nueva aprobación para esos trabajos rutinarios. Si necesita opinar, plantear en conversación una elección concreta y sus consecuencias.

## Continuidad

NEXT corregido por dirección: priorizar una microescena recorrible con avatar, obstáculos/rutas, inspección de personas/objetos y visor de observaciones. Definir su autoridad espacial y vincular alimentación/acciones al contacto alcanzable. El panel actual queda como arnés de reglas. Mantener A/B y sus mediciones intactos; no fijar motor de producción por esta corrección.

[Ejecución](../proof/scene/README.md) · [Núcleo B verificado](M2_CORE_B_RESULT_01.md).
