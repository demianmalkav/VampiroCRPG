# Perfil de recuperación — VampiroCRPG

Este perfil identifica fuentes y autoridades estables. No fija un NEXT, HEAD o motor permanente.

- Repositorio: https://github.com/demianmalkav/VampiroCRPG
- Contrato de trabajo: [AGENTS.md](../AGENTS.md).
- Drive: PROJECT_STATE_MASTER decide estado ejecutivo/NEXT; DECISION_REGISTER y PROJECT_CONSTITUTION gobiernan decisiones y pilares. START_HERE es entrada y NEXT_ACTIONS una vista derivada, no otra autoridad.
- GitHub decide código, herramientas, pruebas, esquemas, arquitectura implementada y evidencia técnica. [TECHNICAL_STATE](TECHNICAL_STATE.md) resume ese estado.
- Bibliografía VTM: Revised/3e como centro; síntesis y traducciones conservan variantes y separan fuente de política de adaptación.
- Referencia Fallout: instalación original privada y CE fijado por revisión. CE Linux DAT-only no es el Windows original; verificar hashes publicados en cada experimento antes de repetirlo.
- Destino aprobado: campaña individual de Nueva York; online posterior. Elección de motor productivo abierta.

## Procedimiento de recuperación

1. Leer START_HERE, PROJECT_STATE_MASTER y AGENTS.
2. Obtener ramas/PR y HEAD vivos; comprobar que el estado técnico de la rama corresponde al checkpoint ejecutivo. La cadena abierta auditada el 2026-10-10 termina en PR 4 (`proof/m2-walk-01`); es orientación de recuperación, no obligación permanente.
3. Contrastar TECHNICAL_STATE, ASSIMILATION_PLAN y casos A2. Un checkpoint anterior conserva su fecha y alcance; no reemplaza el estado vigente.
4. Consultar las fichas fuente/sistema requeridas por ese NEXT. No reiniciar absorción general ni repetir autorizaciones registradas.
5. Verificar identidad de inputs privados si se necesita ejecución. Si faltan bytes, avanzar sólo en trabajo independiente y registrar la limitación.
6. Publicar un commit semántico con lease, verificarlo y actualizar el master; dejar sincronización pendiente si la escritura falla, sin repetir implementación.

## Validación reproducible

Desde la raíz, sin datos originales ni dependencias externas:

```bash
python3 -m unittest discover -s tools/research -p 'test_*.py' -v
python3 tools/research/check_ce_navigation_evidence.py research/FALLOUT2/CE_NAVIGATION_2026-10-10.json --check-source-hashes
python3 tools/research/check_ce_redirect_evidence.py research/FALLOUT2/CE_REDIRECTION_2026-10-10.json --check-source-hashes
python3 tools/research/check_ce_door_evidence.py research/FALLOUT2/CE_DOOR_2026-10-10.json --check-source-hashes
python3 tools/research/check_ce_container_evidence.py research/FALLOUT2/CE_CONTAINER_2026-10-10.json --check-source-hashes
python3 tools/research/check_ce_pickup_evidence.py research/FALLOUT2/CE_PICKUP_2026-10-10.json --check-source-hashes
python3 tools/research/check_ce_pickup_cycle_evidence.py research/FALLOUT2/CE_PICKUP_CYCLE_2026-10-10.json --check-source-hashes
```

A/B/escena/C: `python3 -m unittest discover -s tests -v`. El test HTTP del arte C necesita las exportaciones generadas; seguir [la receta](../proof/walk/README.md) antes de ejecutarlo. CI Walk proof las construye.

Una traza archivada que pasa sus guards demuestra integridad y alcance documental; no una nueva observación de runtime. El arte y la física aceptados requieren evidencia distinta.
