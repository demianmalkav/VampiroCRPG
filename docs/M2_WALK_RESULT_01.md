# M2 C — El pasaje

Estado inicial: IMPLEMENTED / REMOTE_VERIFICATION_PENDING / PLAYER_ACCEPTANCE_PENDING.

Muestra acotada: avatar, rutas sin cortar esquinas, obstáculos, objetos percibidos, visor de inspección, aproximación real, llave con propietario único, puerta y entrada al refugio. Guardado/carga de movimiento e intención pendiente. A/B permanecen separados y sin cambios.

Arte generado desde modelos editables comunes con Blender 4.5.14; atlas de 72 cuadros, props y variante de abrigo desde un material. No hay dependencia Blender para jugar. Geometría y textura iniciales simples; aceptación estética pendiente.

Evidencia inicial local: lógica del recorrido llave/puerta y replay de partida correctos; Python/JS compilaron; navegador Chromium 153 abrió la escena y produjo captura inicial sin errores JS. El entorno se desconectó durante el recorrido de QA, antes de verificar su final y antes de empaquetar. No se presume PASS del recorrido por esa captura.

Continuación: workflow Walk proof, desde la rama proof/m2-walk-01, genera recursos, corre regresión A/B/escena/C, verifica mouse real, inventario, guardado/carga, final del recorrido y cambio de abrigo con estado idéntico; conserva capturas y paquete. Registrar resultados reales al completarse. No entregar una carpeta como verificada antes de eso.

NEXT: resolver cualquier fallo observado, verificar arranque del paquete limpio y dar a dirección una descarga del ZIP. Su criterio requerido: si el movimiento/inspección se acercan a la experiencia buscada y qué falta a la estética urbana noventera; el control técnico no requiere revisión por su parte.
