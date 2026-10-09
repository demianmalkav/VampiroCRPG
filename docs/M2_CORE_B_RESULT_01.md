# M2 B — resultado de la prueba sin gráficos

Estado: IMPLEMENTED / EXECUTED / PASS en el perfil de ensayo aprobado. La dirección indicó que asume la lógica propuesta, delega decisiones técnicas rutinarias y pidió continuar. Esto autoriza B; no equivale a elegir el motor ni a aprobar el balance final.

Sangre y pérdida de la víctima se comprometen juntas; hambre deriva de sangre; el frenesí cambia quién gobierna; voluntad paga una sola acción; moralidad evalúa un incidente con contexto y recibo. Los procesos, acciones pendientes y RNG sobreviven a guardar/cargar y a descargar presentación. Los hechos de alimentación generan observaciones/registros mediante el adaptador de A, sin InjectResolvedIncident ni un resultado impuesto.

| Escena | Resultado observado |
| --- | --- |
| Alimentación controlada | Primera noche: V0 2→4, víctima 10→8; se sellan puncturas; vídeo/recuerdos sobreviven. En la segunda noche la reserva pasa a 3 por el coste nocturno; copia, informe y visita siguen sus causas |
| Frenesí sin intervención | Víctima previamente reducida a 8: extracciones 3+3+2; V0=10, víctima muerta; incidente nivel 4; el vector de fallo deja Humanidad 6 |
| Retirada lúcida | Tras extraer 3: voluntad 5→4; movimiento real al refugio, víctima viva con reserva 5 y emergencia médica. La Bestia vuelve a gobernar en segundo 6; episodio termina en segundo 15 |
| Botch | Humanidad 6, Conciencia 2 y consecuencia traumática pendiente; episodio prolongado termina en segundo 27 |
| Retirada temprana / acceso denegado / encargo incompleto | Mantienen las diferencias de copia, disponibilidad, gasto y conocimiento privado de A sobre el incidente real |

## Evidencia

[Informe medido](../tests/results/m2_core_b_run.json): 59 tests PASS, 0 fallos, 0 errores; 29 son regresión A y 30 son B. Siete escenarios B PASS; 28 grupos cubiertos (NQR-01–12, F-01–07, B-F01–08 y B-I01). Estado, causas, cola, recursos y RNG iguales al serializar/cargar antes y después de cada commit de los siete casos.

Los ensayos cubren depósito/extracción, velocidad/capacidad, ausencia de acceso/percepción, cinco éxitos, cancelación versus botch, gobierno, pago/expiración de lucidez, coste nocturno dormido, recuperación una vez, prohibición moral de voluntad, evaluación única, cámara ausente, rollback a mitad de transferencia y cargas corruptas. Se detectó y corrigió una validación que permitía desligar gobierno y acción lúcida en una carga alterada. También se validan contra sus trazas los recibos, los saldos iniciales y la posición del RNG.

La CLI se ejecutó realmente: guardar en segundo 4 y reanudar produce el mismo JSON que la ejecución continua; cargar otro escenario se rechaza. Una entrada interactiva después de la primera extracción altera el resultado y conserva a la víctima viva. Tras traducir las etiquetas visibles de la CLI, sus dos tests se repitieron con PASS; los sistemas no cambiaron.

[Traza controlada](../tests/results/m2_core_b_conservative_trace.json) · [Traza de lucidez](../tests/results/m2_core_b_lucid_trace.json). Las trazas de debug contienen hechos privados; la salida de jugador muestra su propia reserva y percepciones. Los vectores de ensayo se identifican como tales: no se atribuyen al seed del RNG real.

## Ajustes de integración y límites

Se añadió un regreso explícito al lugar del incidente entre 86400 y 86403 antes de observar la visita en 86460: despertarse en el refugio no teletransporta al personaje. El encargo espera su not_before, viaja y usa permisos reales. La visita espera el horario planificado y luego viaja, en vez de aparecer al abrir el caso.

Las unidades/snapshots de A permanecen intactas. Sus dos extensiones son un adaptador de hechos observables y un punto de despacho diferido; el runner A conserva sólo sus propios tests. Su informe histórico no se sobrescribió.

Es una prueba de lógica con acceso y procedimientos acotados, no un juego completo. No hay engine seleccionado, gráficos, inventario, combate general, torpor o trastornos completos. El marcador de trauma es una limitación expresa del perfil, no una simulación de sus efectos. La corrección técnica no demuestra todavía ritmo, diversión o balance para jugadores.

NEXT: preparar una presentación mínima de la escena que permita inspeccionar las decisiones y consecuencias del núcleo verificado. Mantenerlo separado de un motor y evitar reinstalar/reinvestigar fases cerradas sin evidencia. Sólo pedir criterio de dirección sobre una decisión concreta que afecte la experiencia o el alcance.
