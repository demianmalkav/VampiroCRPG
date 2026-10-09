# VampiroCRPG

Repositorio técnico del proyecto. Primera prueba ejecutable sin gráficos: **La Noche que Recuerda** — un incidente observado, recordado, transmitido y convertido en una consecuencia persistente.

```bash
python3 -m proof.m2 --case late_copy
python3 -m proof.m2 --suite --report tests/results/m2_core_a_run.json
```

Python 3.12; sólo biblioteca estándar. No requiere un motor gráfico.

- [Ejecución y límites de la prueba](proof/README.md)
- [Resultados verificados](docs/M2_CORE_A_RESULT_01.md)
- [Contrato M2](docs/M2_CAUSAL_SIMULATION_CONTRACT.md)
- [Paquete de revisión 0.2](docs/M2_REVIEW_02.md)
- [Especificación de aceptación](docs/M2_CORE_A_ACCEPTANCE.md)
- [Estado técnico](docs/TECHNICAL_STATE.md)
- [Investigación Fallout 2](research/FALLOUT2/README.md)

29 tests y cuatro escenarios PASS en el prototipo. Sangre, Bestia, moralidad, combate, inventario general y gráficos todavía no están implementados.

