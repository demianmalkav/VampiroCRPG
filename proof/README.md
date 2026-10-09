# La Noche que Recuerda — prueba desnuda del núcleo A

Prueba ejecutable, offline, sin gráficos, Godot, dependencias externas ni LLM en runtime. Usa Python 3.12 y su biblioteca estándar. Dirección autorizó el alcance M2 0.2 en D-011 de DECISION_REGISTER.

Desde la raíz del repositorio:

```bash
python3 -m proof.m2 --case late_copy
python3 -m proof.m2 --case early_removal
python3 -m proof.m2 --case denied_access
python3 -m proof.m2 --case insufficient_directive
python3 -m proof.m2 --suite --report tests/results/m2_core_a_run.json
```

En Windows con Python ya disponible, se puede usar `py -3.12` en lugar de `python3`. No se requiere instalar un motor gráfico.

Para detener antes de la visita y restaurar:

```bash
python3 -m proof.m2 --case late_copy --until 9 --save snapshot.json
python3 -m proof.m2 --case late_copy --load snapshot.json --until 12
```

Para exportar la explicación causal y la vista autorizada del jugador:

```bash
python3 -m proof.m2 --case late_copy --trace trace.json
```

## Qué se ejecuta

`world.py` es la autoridad: estado, transacciones, conocimiento adquirido, mensajes, permisos, registros, procesos, cola y snapshots. Los intentos de copia/revisión/visita consultan condiciones reales; no hay QUEST_STAGE ni lectura de expectativas. `scenario.py` prepara estímulos y observa resultados. `__main__.py` narra hechos confirmados y ejecuta los ensayos. `tests/test_m2_core_a.py` verifica NQR-01–09/F-01–07 y fallos adicionales.

El JSON de fixtures contiene expectativas exclusivamente para comparación del harness. `World` recibe condiciones iniciales y perfiles, no resultados esperados. El informe identifica actual/expected, versiones, seed, inputs, cobertura y errores. Un escenario sin información puede no generar caso; retirar un vídeo temprano impide su copia sin borrar el testimonio.

El protagonista vuelve explícitamente L_INC → L_HAV entre t1 y t2 antes de dormir. Este viaje corrige una omisión del fixture candidato y evita asignar una nueva localización por el acto de dormir. I1 viaja realmente durante tres ticks; no aparece de inmediato por abrir un caso.

## Persistencia y límites

Snapshots JSON `m2-proof-json-1`, runtime `m2-python-proof-1`, perfil `m2-a-proof-profile-1`. Son formato interno de ensayo, sin migraciones ni promesa de compatibilidad de saves del juego. Versiones, IDs, targets y causas inválidas se rechazan antes de publicar. Índices se reconstruyen a partir de IDs; presentación es descartable. Comparación semántica mediante JSON UTF-8 con claves de objetos ordenadas, orden de listas preservado y SHA-256.

Las transacciones usan copias completas del pequeño estado para rollback. Es una elección clara para esta prueba, sin evaluación de rendimiento para un mundo grande. Cada Actor/Record/Process vive fuera de presentación; el scheduler ordena por due_tick/enqueue_seq. El contador de 128 handlers/tick persiste al cargar. Los procedimientos A no consumen RNG.

Es una microhistoria con procedimientos finitos configurados, no planificación general de NPC. La interfaz de comandos y los handlers implementan el flujo A; no son una API de juego completa. Alimentación entra resuelta; sangre, Bestia, moralidad, combate, Disciplinas, inventario general y arte siguen fuera de esta ejecución. Un permiso de archivo/revisor es un perfil ficticio acotado, no una simulación policial universal.

Los tests comparan estado y causas antes y después de cada commit de los cuatro escenarios al serializar/restaurar. Incluyen interrupción durante una operación, inputs repetidos, permisos revocados, acceso ilegítimo, canales ausentes y orden de eventos simultáneos. Estas pruebas demuestran el comportamiento de este prototipo bajo esos perfiles; no certifican aún el juego final.
