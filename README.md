# VampiroCRPG

Repositorio técnico del proyecto. **La Noche que Recuerda** conecta una escena isométrica provisional con el núcleo causal y de supervivencia ya verificado.

```bash
python3 -m proof.scene --open
python3 -m proof.m2b --case conservative
python3 -m proof.m2b --case lethal --interactive
python3 -m proof.m2b --suite --report tests/results/m2_core_b_run.json
```

Python 3.12; sólo biblioteca estándar. No requiere un motor gráfico.

- [Escena mínima: ejecución y límites](proof/scene/README.md)
- [Resultado de la escena](docs/M2_SCENE_RESULT_01.md)
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

68 tests PASS (59 regresiones A/B y nueve de escena), siete escenarios B PASS. Sangre, Bestia, voluntad y moralidad mínima implementadas y conectadas a la interfaz. Apariencia en navegador pendiente de verificación. Combate, inventario general, arte y motor de producción siguen pendientes; el balance requiere prueba con jugadores.

