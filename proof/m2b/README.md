# La Noche que Recuerda — supervivencia sin gráficos

Python 3.12, biblioteca estándar; funciona offline. Esta etapa agrega sangre, víctima, hambre, Bestia, voluntad y moralidad al mundo causal de A. No necesita Godot ni un LLM.

Desde la raíz del repositorio:

```bash
python3 -m proof.m2b --case conservative
python3 -m proof.m2b --case lethal
python3 -m proof.m2b --case lucid_escape
python3 -m proof.m2b --suite --report tests/results/m2_core_b_run.json
```

En Windows, con Python 3.12 disponible, puede usarse `py -3.12` en lugar de `python3`.

Para tomar la decisión durante el frenesí:

```bash
python3 -m proof.m2b --case lethal --interactive
```

Enter avanza tres segundos. Después de la primera extracción, `v` paga un punto de voluntad para retirarse al refugio; cuatro avances permiten ver el regreso del control. `r` suelta a la víctima, `e` compra una espera lúcida, `q` termina. Soltar sin alejarse puede permitir que la Bestia vuelva a alimentarse. Una víctima en emergencia no se considera curada por salvarla de la muerte.

Los escenarios lethal/lucid_escape/botch usan dados de ensayo identificados explícitamente como TEST_VECTOR, para mostrar y comprobar esos caminos. Conservative y las variantes de investigación usan el RNG reproducible real del perfil. Las expectativas de casos están fuera de la autoridad de la simulación.

Persistencia real por disco:

```bash
python3 -m proof.m2b --case lucid_escape --until 4 --save snapshot-b.json
python3 -m proof.m2b --case lucid_escape --load snapshot-b.json --trace trace-b.json
```

Una carga de otro caso/modo/perfil se rechaza. Para reanudar una sesión interactiva, repetir el mismo `--case` y `--interactive` con `--load`. Los snapshots de B son internos y versionados; no migran saves de A ni prometen compatibilidad de producción.

La suite mide NQR-01–12, fronteras A/B e integración. Actualmente: 59 tests PASS (29 de A, 30 de B), siete escenarios B PASS. Prueba rollback de una extracción a mitad de commit, corrupción de cargas, recibos, RNG y continuidad antes/después de cada commit de los siete casos. Dos tests de CLI comprueban disco/reanudación y una decisión interactiva efectiva. El informe de A se mantiene separado.

Límites: una microhistoria con procedimientos institucionales finitos; generación 13; acceso ya viable a un adulto no resistente; calendario sintético; trauma pendiente sin comportamiento de trastorno. No se implementan agotamiento de sangre a cero, torpor, caza/combat completos, toda la jerarquía de Humanidad, poderes, inventario, gráficos o rendimiento de una ciudad. Contactos posteriores crean sus observaciones/registros, pero no constituyen un sistema general de reportes e investigación repetida.

[Resultado medido](../../docs/M2_CORE_B_RESULT_01.md) · [Perfil aprobado](../../tests/specs/m2_core_b_profile.json).
