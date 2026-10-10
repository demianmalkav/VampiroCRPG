# VampiroCRPG

Estado: asimilación de Fallout 2 / preproducción. Campaña individual en **Nueva York** primero; posible online posterior. Motor productivo todavía sin elegir.

La muestra recorrible 02 fue **rechazada por dirección** por su calidad artística y coherencia espacial. Sus comprobaciones técnicas cubren casos limitados; no equivalen a aceptación del juego. Los núcleos A/B conservan sus pruebas de causalidad y reglas, todavía separados del recorrido C.

## Recuperar el trabajo

Leer [perfil y autoridades del proyecto](docs/PROJECT_PROFILE.md), [estado técnico](docs/TECHNICAL_STATE.md) y [plan de asimilación](research/FALLOUT2/ASSIMILATION_PLAN_01.md). Resolver la rama y su HEAD en vivo: el trabajo auditado está en `proof/m2-walk-01`, PR [4](https://github.com/demianmalkav/VampiroCRPG/pull/4), sobre los PR 3 → 2 → 1. `main` conserva la fundación; aún no contiene esos avances. Ningún PR se ha fusionado.

CE Linux con los DAT privados ya permitió observar parcialmente geometría, bloqueo y redirección. [Navegación](research/FALLOUT2/CE_NAVIGATION_2026-10-10.md) y [redirección](research/FALLOUT2/CE_REDIRECTION_2026-10-10.md) identifican versión, inputs, trazas y límites. No prueban el ejecutable Windows original ni aceptación de Vampiro.

[Auditoría de salud documental y GitHub](docs/PROJECT_HEALTH_AUDIT_2026-10-10.md).

## Muestras históricas y reproducción

[Descargar muestra 02](https://drive.google.com/file/d/1jSJMEnoBcrmA6WkFvQoEMKg60JocJ159/view?usp=drivesdk): pasaje ficticio de Manhattan con avatar, visor, llave, puerta y fuentes editables. Es evidencia histórica del prototipo rechazado. [Resultado y límites](docs/M2_WALK_ART_RESULT_02.md).

Descomprimir y ejecutar `iniciar-pasaje.cmd` en Windows con Python 3.11+; macOS/Linux: `python3 -m proof.walk --open`. El paquete trae PNG. Al clonar, generar primero el arte según [ejecución y autoría](proof/walk/README.md); las exportaciones no se versionan. La ejecución Windows sigue sin verificarse.

[Panel de reglas](proof/scene/README.md) · [Núcleo B](proof/m2b/README.md) · [Núcleo A](proof/README.md) · [Investigación](research/FALLOUT2/README.md).

## Alcance de las comprobaciones

El workflow Walk proof construye recursos y verifica 80 tests A/B/escena/C más navegador/arte. El workflow Research evidence ejecuta los 25 tests de lectores/verificadores y valida integridad/alcance de las trazas publicadas. Ninguno sustituye una nueva ejecución del juego de referencia ni la aceptación artística de dirección.
