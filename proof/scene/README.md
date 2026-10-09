# La Noche que Recuerda — escena mínima

Una vista isométrica provisional sobre la simulación A/B ya verificada. La sangre, la Bestia, la voluntad, la moralidad y los procesos de otros actores siguen perteneciendo al núcleo Python. El dibujo no resuelve ninguna regla.

Requiere Python 3.12 y un navegador moderno. No instala Godot, paquetes Python ni servicios externos. Desde la raíz del repositorio:

```bash
python3 -m proof.scene --open
```

En Windows: `py -3.12 -m proof.scene --open`. Sin `--open`, entrar en `http://127.0.0.1:8765`. Ctrl+C cierra el servidor. Sólo escucha en el equipo local; no es una publicación web. El navegador necesita que el servidor siga abierto; abrir `index.html` directamente no ejecuta la simulación.

## Qué probar

1. **Alimentación controlada**: alimentarte, avanzar 3 segundos, cerrar marcas, avanzar 3 segundos. Vas a ganar 2 de sangre. Sellar las marcas no borra el registro ni el recuerdo del testigo.
2. **Al borde del frenesí**: alimentarte y avanzar 3 segundos. La víctima muestra una emergencia. Retirarte con 1 de voluntad y avanzar cuatro veces permite llegar al refugio y recuperar el control, conservándola viva. Guardar y cargar durante el traslado conserva el pago y la acción pendiente.
3. Reiniciar esa misma situación y avanzar sin intervenir permite ver otro desenlace: muerte y pérdida de Humanidad. Este modo utiliza dados de ensayo identificados en pantalla, con una víctima que ya había perdido sangre. No muestra probabilidades ni balance definitivos.
4. En la situación controlada, encargar retirar el video, ir al refugio, avanzar hasta llegar, dormir y continuar hasta despertar. El contacto informa lo que pudo hacer. Volver al callejón, avanzar hasta llegar y esperar hasta un minuto permite percibir la visita; no se muestra la investigación fuera de tu vista.

El tiempo avanza por decisión del jugador. Soltar sin alejarse puede permitir que la Bestia vuelva a alimentarse. La escena termina temporalmente en el segundo 86460. Cambiar de situación o reiniciar empieza una partida nueva. Guardar descarga un JSON privado con el mundo completo; no es la información que se muestra durante el juego. Cargar verifica formato, perfil, recursos, RNG y acciones antes de reemplazar la partida actual. La envoltura de presentación no cambia el esquema B.

## Separación y límites

El adaptador ofrece un conjunto reducido de comandos: cada posibilidad se consulta en una copia de la autoridad; la vista no gasta recursos ni resuelve dados. Las peticiones llevan revisión y recibo para rechazar vistas viejas y evitar pagos duplicados. No se aceptan comandos de ensayo arbitrarios desde la interfaz.

El jugador ve recursos propios, recuerdos/mensajes adquiridos y los actores activos presentes en su lugar. La microescena supone visibilidad directa dentro de cada lugar: todavía no hay iluminación, oclusión ni percepción generales. La condición de la víctima procede de una observación adquirida; su reserva interna no se muestra. Las posiciones de los muñecos, las baldosas, las paredes y los objetos decorativos son presentación; no son geometría navegable ni ítems simulados. No hay movimiento libre, inventario o combate. Cámara y testigo visibles no equivalen a conocer sus registros o pensamientos.

## Verificación

```bash
python3 qa/scene/check.py
python3 qa/scene/check_ui.py --report tests/results/m2_scene_ui_run.json
```

El segundo comando requiere Node sólo para el ensayo, no para jugar. Ejecuta el JavaScript real con un arnés DOM/canvas y el servidor real; comprueba decisiones y guardar/cargar. No sustituye la comprobación visual en navegador.

[Resultado](../../docs/M2_SCENE_RESULT_01.md). **Diseño CSS, accesibilidad completa y apariencia en navegador: UNVERIFIED** en este entorno: no había binario y la descarga falló. La ejecución visual en el equipo de dirección queda pendiente. No se afirma que esta prueba sea un juego completo o una elección de motor de producción.
