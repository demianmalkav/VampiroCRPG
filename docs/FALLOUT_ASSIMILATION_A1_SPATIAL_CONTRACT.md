# Asimilación A1 — espacio, autoridad y acciones del pasaje

Estado: CONTRACT_DEFINED_FOR_LAB / 2026-10-09 Argentina. Dirección autorizó comenzar la asimilación de Fallout 2 con vistas al motor productivo de Vampiro, campaña individual primero y online en un orden posterior. A1 cierra la extracción y reconciliación del contrato; no cierra equivalencia con el original, implementación, elección de motor ni aceptación artística.

## 1. Procedencia y límites

Los mecanismos observados proceden de CE `e97087b9582f37075db347a89898887320753f8b` y RE `b135fc46ef40c4aecd156f3cebcf88ec531bb8ac`. [Hallazgos y funciones exactas](../research/FALLOUT2/SPATIAL_ART_ANIMATION_FINDINGS_01.md) enlazan las fuentes. Las políticas de este contrato son adaptaciones nuestras, no afirmaciones de comportamiento binario. No se copió código externo.

Se inspeccionaron de nuevo `_obj_blocking_at`, `_object_move`, `actionPickUp`, `_adjust_fid`, el mapa/autoridad/renderizador C y su guardado. El [auditor reproducible](../tools/research/audit_spatial_a1.py) ejecuta el C existente; [su resultado](../research/FALLOUT2/A1_BASELINE_AUDIT_2026-10-09.json) conserva las tres fallas. Ninguna fue corregida mediante este documento.

## 2. Un registro espacial, varias consultas

| Responsabilidad | Autoridad propuesta | Representación derivada |
| --- | --- | --- |
| Identidad y existencia | ID estable de instancia; prototipo versionado; ubicación/elevación; propiedad/custodia | Sprite/modelo, icono y texto enlazados al mismo ID/prototipo |
| Posición | Nodo lógico y segmento activo con origen, destino, inicio, duración/progreso; orientación | Proyección del segmento confirmado; interpolación limitada |
| Volumen | Huella, banda de altura y estado; políticas separadas de movimiento, visión y ataques | Recurso/anclaje y piezas de oclusión compatibles con ese volumen |
| Ruta | Consulta de huellas/ocupación; desempate estable; revisión de mapa | Indicador de destino y recorrido, sin autorizar pasos |
| Acción | Actor, objetivo, comando, fase, tiempos, reservas y recibo de efecto | Clips y marcadores que siguen la acción lógica |
| Percepción | Consulta del observador, condiciones actuales y conocimiento adquirido | Objetos seleccionables autorizados y visor de ese personaje |
| Tiempo y azar | Reloj lógico, cola ordenada, perfil de reglas y RNG persistidos | Sonido/animación; ningún resultado decidido por FPS |

Fallout enlaza navegación y dibujo mediante instancias registradas; conserva consultas distintas para bloquear movimiento, disparo y luz. Adoptamos ese principio. Toda pieza visible debe referirse a una instancia o decoración registrada con política explícita. El renderer no puede inventar volúmenes físicos mediante una lista local.

La campaña local tendrá una sola autoridad. El controlador pide una intención; no escribe posición, daño, sangre ni inventario. El actual avance solicitado por el loop del navegador es una limitación del ensayo: el laboratorio de adaptación deberá separar el reloj de simulación del FPS. Pausar en individual es una operación explícita; ocultar la ventana no define por accidente el tiempo de la campaña.

## 3. Registro completo del pasaje, antes de cambiar contenido

Las decisiones siguientes son objetivos para el laboratorio, todavía no cambios en `map.json`.

| Pieza actual | Política física propuesta | Acción necesaria / comprobación |
| --- | --- | --- |
| Avatar [3,10] | Ocupante móvil, huella y altura del cuerpo; segmento reservado | Misma posición alimenta percepción, rutas y representación |
| Muros existentes | Cada celda sólida; altura baja/alta y orientación explícitas | IDs por pieza, sin derivar tipo de muro de una comparación de coordenadas en JS |
| Contenedor [5.5,5.5] | Bloquea sus cuatro celdas [5,5], [6,5], [5,6], [6,6]; volumen opaco | Contorno gráfico dentro de cobertura declarada; aproximación por borde alcanzable |
| Caja [3,4] | Sólida, huella conservadora [3,4] | Registrarla y retirar su aparición independiente del renderer |
| Contacto [7,9] | Ocupación sólida; visión no completamente opaca | Reacción y contacto propios; no diálogo a través de muro |
| Llave [7,5] | Ítem pequeño sin bloqueo de locomoción; una sola custodia | Transferencia en fase de efecto, no antes del gesto |
| Puerta [12,4] | Cerrada bloquea paso y visión; abierta libera vano con hoja fuera de trayectoria | Diseñar hoja abierta contra muro [11,4], revisar barrido; el sprite actual no demuestra esa geometría |
| Lámpara [3,9] | El pie actual es un volumen real, no decoración libre | Para este laboratorio, sustituir por luz montada en muro [2,6], sin pie en suelo; editar recurso/anclaje y verificar saliente |
| Ventana [11,4.15] | Adosada a muro [11,4], sin nuevo obstáculo transitable | Registrar pertenencia y relieve; no suponer transparencia de visión porque tenga vidrio |
| Escalera de incendio [2.1,4.5] | Elementos bajos y escalera dentro de la banda de muros [2,4]/[2,5]; plataforma elevada | Revisar ancho/saliente en recurso; si invade suelo libre, ampliar huella antes de habilitar recorrido; no trepable en A2 |
| Tubería [2.16,5.9] | Adosada a muro [2,6], incluida en su cobertura | Verificar saliente; no bloqueador independiente oculto |
| Aire acondicionado [14,4.15] | Adosado a muro [14,4], elevado; cobertura incluida en muro | Registrar altura inferior y verificar que no invada el corredor/cuerpo |
| Botellas [4,8], [3.4,8.2] | Decoración pequeña: no bloquea locomoción en este perfil | Puede ocupar visualmente suelo bajo pies; no manipulación ni tropiezo implementados |
| Desagüe [6,9], pisos, grietas, charcos | Superficie plana, transitables | Sin volumen ni efecto mecánico de clima en A2 |
| Rótulo y luces dibujadas | Elementos gráficos vinculados al muro/fuente | Ninguna autoridad de navegación; no revelar destino secreto por una etiqueta |

No se admite dar por seguro un saliente porque el centro esté en una celda bloqueada. El editor o exportador debe comprobar cobertura y banda de altura. Toda nueva pieza se incorpora al registro antes de dibujarse. Vehículos requerirán huellas orientadas distintas; no se implementan ahora.

## 4. Coordenadas y velocidad

El original separa nodos hexagonales de objetos y tiles de piso/techo, con elevaciones. C usa cuadrícula cuadrada y ocho vecinos. A1 no convierte C a hexágonos: define una frontera `GeometryProfile` con vecinos, distancia, proyección y elevación coherentes. El laboratorio CE conserva geometría nativa de seis direcciones; una futura adopción hexagonal exigirá especificar y verificar mapa, contacto y exportación. Los números de celda C no se trasladan literalmente al MAP de Fallout.

Para el cuadrado C, distancia en el mundo = longitud euclídea del tramo. Referencia de ensayo: una unidad cardinal en 300 ms; diagonal en 425 ms (redondeo entero hacia arriba de 300√2, diferencia de velocidad inferior a 0,2%). El 10/14 actual es sólo aproximación de coste de búsqueda: no es duración ni presupuesto de acción de Vampiro. La referencia hexagonal usa seis desplazamientos de igual longitud lógica; comparar velocidad sobre esa distancia, no sobre píxeles proyectados.

El anclaje es el apoyo de pies en el suelo; cámara, zoom y desplazamientos de cuadros no alteran la posición física. Los deltas FRM observados coordinan movimiento clásico con animación. Nuestro adaptador deberá elegir una única autoridad del desplazamiento: no sumar root motion visual a un segmento ya avanzado por simulación. Fases de pasos, duración y contactos se exportan como metadatos comprobables.

## 5. Redirección y bloqueos durante ejecución

Política mínima del laboratorio C: al redirigir en mitad de un tramo, cancelar inmediatamente la intención de interacción anterior, conservar origen/destino/progreso del tramo en curso y sustituir el destino posterior. Terminar ese tramo reservado y recalcular desde el nodo de llegada. No hay retroceso al origen ni efecto tardío del objetivo cancelado. La respuesta puede esperar el resto de un tramo (hasta 425 ms en este perfil). Detenerse con Escape tiene la misma política. No es una promesa de parada instantánea en cualquier punto.

Un destino inválido se rechaza sin cambiar segmento ni intención. Un comando más reciente válido sustituye el destino pendiente. Guardar conserva ese destino y el progreso. La llegada usa la ocupación vigente. Un obstáculo puede bloquear tramos futuros: recalcular una vez por revisión relevante del mapa y, si no hay ruta, detener con causa visible; no reintentar cada frame. No se permite crear un sólido encima del actor ni dentro de su segmento reservado. Esto es una política digital nueva; la reacción exacta del original a redirección/guardado sigue pendiente de A2.

## 6. Puerta y acción física

| Estado | Paso / acción | Cancelación y persistencia |
| --- | --- | --- |
| CLOSED_LOCKED | Vano bloqueado; requiere llave accesible y aproximación | Guardar estado y propietario de llave |
| UNLOCKING | Validar cercanía, llave y objetivo; preparar orientación/gesto | Antes del efecto, cancelar sin abrir; ningún éxito por señalarla |
| OPENING | En efecto lógico, confirmar desbloqueo; barrido y apertura coordinados | Guardar fase y tiempo; evitar barrido sobre cuerpo. No liberar paso antes del momento declarado |
| OPEN | Vano libre, hoja plegada fuera del corredor; permitir cruzar | Repetir comando no vuelve a cobrar ni genera otro efecto |
| BLOCKED / CANCELLED | Acción inviable o cancelada con causa | No cerrar sobre actor, borrar llave ni completar recorrido |

Cerrar y volver a bloquear la puerta se difieren; los dos sprites actuales no equivalen a estas fases. No se fija un tiempo final de animación sin un clip evaluado.

Acción general: intención → aproximación → orientación → preparación/contacto → efecto → finalización. En efecto se revalidan objetivo, acceso, disponibilidad y recursos, y se confirma una sola transacción con `ActionId`/recibo. Animación y sonido siguen el tiempo lógico. Cancelar antes del efecto no adquiere la llave; después no la devuelve. Una secuencia de alimentación podrá tener varios efectos de extracción con IDs distintos dentro de un mismo proceso, cada uno único; no se confunde con una acción de recogida de efecto único.

La proximidad debe consultar un borde/punto de contacto alcanzable y la línea local de interacción; distancias entre centros no autorizan hablar o usar a través de una pared. El bloqueo de visión no es la única prueba de contacto. El marcador `action_frame` de Fallout es evidencia de coordinación, no de contacto exacto de la mano. A3 validará fases, pago, cancelación y restauración ejecutables.

## 7. Selección, profundidad y visor

Proyección y conversión suelo↔cursor comparten perfil y cámara. Para objetos solapados, el hit test respeta máscara/piezas visibles y orden de oclusión; excluye elementos no percibidos. Un click en caja o pared no puede transformarse accidentalmente en un destino detrás de ella. Un click en suelo pide una ruta, no asigna posición.

Suelo, volúmenes y cubiertas son pasadas distintas; para piezas extensas se usan segmentos/piezas de oclusión o profundidad de motor, no sólo centro `x+y`. Transparencia para ver al avatar es presentación: no elimina bloqueo físico ni revela contenido desconocido. A2 exige recorridos delante/detrás de muro y contenedor; ningún algoritmo de ordenación queda validado sólo por este contrato.

La autoridad produce observaciones del actor. El visor conserva lo adquirido, distingue inspección de memoria y no copia clan, Humanidad, sangre del otro o intención secreta. Volver a señalar no crea spam ni nuevo conocimiento sin cambio relevante. La UI no consulta trazas de debug para construir texto de jugador.

## 8. Compatibilidad antes de tocar mapa o saves

Se conserva sin modificaciones el lector/semántica de `m2-walk-save-1` y el mapa histórico. Añadir caja, mover lámpara y cambiar duraciones altera mapa, ejecución e historia reproducida: no se puede cambiar sólo `map_hash` y reproducir una partida antigua bajo nuevas reglas.

El laboratorio nuevo usará otro namespace de contenido y una versión nueva de partida, cuando se implemente. No sobrescribirá las partidas de C ni las independientes A/B. Carga de save antiguo en el nuevo laboratorio: rechazo claro con opción de abrirlo en muestra 02 histórica; no conversión automática. Este rechazo versionado es la política acotada de compatibilidad, no una migración sin pérdida. Si posteriormente se necesita migración, tendrá formato de origen/destino, identidad/posesión/cola verificadas y pruebas propias antes de implementarse.

El nuevo snapshot deberá conservar segmento/progreso/destino pendiente, fase/efectos comprometidos, reservas, reloj, RNG, perfil de reglas, versiones de contenido, conocimientos y trabajo de mundo. Índices de dibujo son reconstruibles. Guardar/cargar no confirma un efecto todavía pendiente ni cobra dos veces una acción. La forma final del save de producción permanece abierta.

## 9. Cierre A1 y siguiente bloque

DONE: contratos y políticas explícitos; todas las piezas actuales tienen decisión de cobertura; tres defectos reproducidos; compatibilidad histórica definida antes de cambiar runtime. [Casos del laboratorio](../research/FALLOUT2/A2_ACCEPTANCE_CASES_01.json) separan resultados esperados de observados.

EVIDENCE: lectura CE/RE fijada, lectura implementación C, auditor ejecutado y hashes de archivos medidos. OPEN: ensayo original/CE, contacto/oclusión visible, capacidad productiva y calidad artística. NEXT: A2, arranque de referencia e inspección de datos; recuperar el archivo original por una ruta que soporte su tamaño. Existe en Drive; su descarga por conector devuelve 413, no se trata de falta de material del usuario.
