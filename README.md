# VampiroCRPG

Repositorio técnico del proyecto. Primera prueba ejecutable sin gráficos: **La Noche que Recuerda** — un incidente observado, recordado, transmitido y convertido en una consecuencia persistente.

```bash
python3 -m proof.m2b --case conservative
python3 -m proof.m2b --case lethal --interactive
python3 -m proof.m2b --suite --report tests/results/m2_core_b_run.json
```

Python 3.12; sólo biblioteca estándar. No requiere un motor gráfico.

- [Ejecución y límites de B](proof/m2b/README.md)
- [Núcleo A conservado](proof/README.md)
- [Resultados B verificados](docs/M2_CORE_B_RESULT_01.md)
- [Resultados A](docs/M2_CORE_A_RESULT_01.md)
- [Contrato M2](docs/M2_CAUSAL_SIMULATION_CONTRACT.md)
- [Paquete de revisión 0.2](docs/M2_REVIEW_02.md)
- [Especificación de aceptación](docs/M2_CORE_A_ACCEPTANCE.md)
- [Perfil B aprobado y ejecutado](docs/M2_CORE_B_PROPOSAL_01.md)
- [Estado técnico](docs/TECHNICAL_STATE.md)
- [Investigación Fallout 2](research/FALLOUT2/README.md)

59 tests PASS (29 de A, 30 de B), siete escenarios B PASS. Sangre, Bestia, voluntad y moralidad mínima implementadas. Combate, inventario general y gráficos siguen pendientes; el balance del juego requiere prueba con jugadores.

