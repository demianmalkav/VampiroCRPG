# Auditoría de salud documental y GitHub — 2026-10-10

Estado del corte auditado: **el checkpoint técnico reciente está sincronizado; la red completa de documentación no lo estaba**. Se corrigieron inconsistencias operativas inequívocas. La normalización bibliográfica, la organización de una ficha y la consolidación del historial permanecen abiertas.

Esta revisión precede a continuar el estudio de puerta/acceso. No demuestra calidad artística, equivalencia completa con Fallout 2 ni viabilidad de un juego terminado.

## Corte y alcance verificable

- Repositorio público: demianmalkav/VampiroCRPG.
- Rama técnica: proof/m2-walk-01, HEAD de entrada `4ef0067c7a067378176144df6d2827403f9e5aef`; árbol `a575e2f1a6c70d9ed384a99e4529ff29fe1dd768`.
- Main: `551386b92dc1a3cab01a4a2ac010406f168a687a`.
- Cinco ramas; cuatro PR abiertos y en borrador. Cadena 4 → 3 → 2 → 1 → main corroborada.
- Árbol activo completo: 156 entradas, 131 blobs. Lectura de 126 archivos de texto: 37 Markdown, 28 JSON y código/configuración/instrucciones. Cuatro .gitkeep y un PNG no se trataron como texto.
- Drive: lectura de contenido y estructura nativa de 42 documentos, incluyendo seis controles, matriz Fallout, reconciliación, 14 traducciones, 19 documentos bibliográficos y INSTALL_INFO.
- Carpeta bibliográfica: 85 PDFs con IDs distintos más 00_LIBRARY_CONTROL. Es cantidad de archivos, no de títulos/ediciones ni libros leídos.
- Dos ZIP históricos comprobados por metadatos exactos: muestras 01 y 02 presentes en 09_BUILDS.
- Los 23 destinos distintos de enlaces nativos incrustados fueron resueltos: 20 documentos leídos y tres PDFs con metadatos disponibles. Los rich links no aparecen en la extracción de texto plano; esa ausencia no es un enlace roto.
- Issues devolvió sólo los cuatro PR; no se observó un backlog separado de incidencias. Sin releases publicadas. Rulesets devolvió lista vacía y las cinco ramas figuraban sin protección. Tags no pudieron inventariarse por limitación del endpoint: UNVERIFIED.
- Revisión del contrato AGENTS, workflows, estado técnico, matrices, informes, casos A2, trazas, procedencia, licencias y manifiesto de implementación.

No se volvieron a leer íntegramente los 85 PDFs; no se ejecutó de nuevo Windows/CE, Blender ni el navegador. La revisión no certifica integridad byte a byte de todo Drive ni detección de cualquier archivo fuera de las carpetas y búsquedas consultadas.

## Roles y diagnóstico

| Registro / familia | Rol esperado | Diagnóstico del corte | Tratamiento |
| --- | --- | --- | --- |
| PROJECT_CONSTITUTION | Pilares estables y límites de autoridad | Coherente; antigüedad de fecha no es desactualización | Conservado |
| PROJECT_STATE_MASTER | Estado ejecutivo y único NEXT | Coincide con último avance; mezcla resumen e historial técnico muy extenso | Conservar autoridad, añadir cierre de auditoría; simplificación futura |
| START_HERE | Entrada y recuperación de sesión | Seguía en M0 y pedía crear controles ya existentes | Corregido |
| NEXT_ACTIONS | Vista operativa derivada | Viejos NEXT y aprobación ya resuelta se leían como vigentes | Vista vigente + historial explícito |
| DECISION_REGISTER | Decisiones y alcance de autorización | Buenos Aires abierta; B/C todavía pendientes; rótulo de main engañoso | Registradas decisiones ya expresadas, sin nuevo freeze |
| ROADMAP | Etapas de producto y criterios de avance | M2 vertical slice colisionaba con M2 de ensayos | Distinción explicitada |
| FALLOUT2_SYSTEM_MATRIX en Drive | Síntesis/mirror de investigación | Latest coincide con CE navegación/redirección | Conservado; detalles técnicos en GitHub |
| GitHub SYSTEM_MATRIX | Abstracción de sistemas y evidencia | Afirmaba que no se ejecutaron runtimes ni leyeron datos | Actualizada y survey marcado histórico |
| VTM_SOURCE_HIERARCHY | Canon, ediciones y naturaleza de fuentes | Correctamente separa Revised/3e, variantes y contexto | Conservado |
| VTM_LIBRARY_INDEX / INGESTION_STATUS | Inventario y cobertura real de lectura | 44 histórico superado, sin un conteo vigente consolidado; estados dispersos | Conteo 85 y alcance clarificados; normalización pendiente |
| VTM_WORLD_MODEL / ONTOLOGY / síntesis 01–09 | Modelo fuente, causalidad, incertidumbre | Útiles; distinguen estructura de lectura parcial; referencias BA y gates antiguos | Históricos subordinados a decisiones vigentes; no reescribir investigación válida |
| VTM_CONTRADICTION_AND_VARIANT_REGISTER | Dudas/variantes activas con resolución | CV-001 seguía sin verificar pese a traducción posterior | Reconciliado a nivel de fuente registrada; otras variantes preservadas |
| READINESS 01/02 | Puente/especificación de prueba causal | Conserva la propuesta que precedió a A/B, no resume su implementación actual | Handoff aclara alcance histórico; no usar como NEXT |
| Traducciones 01–14 | Fuente → política candidata → requisitos de implementación | Están las 14; source vs adaptación normalmente explícitos | Conservar; integración/reglas completas no inferidas |
| Reconciliación de alcance | Composición de propuesta y límites | Referencias de gate/localización/etiqueta C antiguas | Leer con handoff actualizado; propuesta histórica |
| TECHNICAL_STATE / ASSIMILATION_PLAN / A2 cases | Estado técnico, siguiente unidad y cobertura | Consistentes con master y evidencias recientes | Conservados |
| Informes fechados / QA / manifiestos | Evidencia reproducible y límites del experimento | Identidades/trazas presentes; hash de 21 textos del manifiesto coincide | Conservar snapshot histórico; no convertirlo en certificación global |
| README / AGENTS / PR 4 | Entrada técnica, reglas y revisión del scope actual | README muestra 01, AGENTS fase antigua, PR 4 omite CE y rechazo | Actualizados |
| CI Walk proof | Reproducción de muestra A/B/escena/C y arte | Verde, pero omite los tests/tools nuevos de investigación | Mantener scope; añadir CI separado para evidencia |
| 09_BUILDS / fuentes de arte | Entregas y autoría recuperables | Dos ZIP presentes; muestra 02 rechazada | Etiquetar históricos; no confundir paquete accesible con producto aceptado |
| INSTALL_INFO | Procedencia de instalación original | Adecuado como dato aportado, exactitud EXE/1.02.31 pendiente | Conservar separado de CE Linux |

## Hallazgos y severidad

### H01 — Entrada operativa vieja — ALTA — CORREGIDO

START_HERE declaraba M0 y pedía crear master/constitución/registro/repositorio. También dependía de CURRENT_MILESTONE, nombre no localizado. Se reemplazaron esas tareas por lectura de fuentes actuales, resolución viva de rama/HEAD y fase en el master.

### H02 — NEXT y autorización obsoletos — ALTA — CORREGIDO

NEXT_ACTIONS acumulaba múltiples listas activas y terminaba en una aprobación del contrato ya resuelta. Se conserva el historial, pero el bloque vigente deriva del master y declara superados sus antiguos rótulos. No se repite autorización de A/B.

### H03 — Decisiones faltantes — ALTA — CORREGIDO

D-010 dejaba Buenos Aires como candidata abierta. Se registra Nueva York como decisión expresada por dirección. Se añaden las autorizaciones posteriores B/recorrido/asimilación/delegación y el rechazo de la muestra 02. “Main siempre jugable” se ajusta al contenido ya aprobado: main coherente y recuperable. No se decidió un motor ni se amplió una autorización de producto por esta auditoría.

### H04 — Ambigüedad de etiquetas — MEDIA — ACLARADO

M2 de ensayos no significa el M2 Vertical Slice del roadmap. C de una propuesta antigua de extensiones VTM no es C espacial. ROADMAP y handoff aclaran estas diferencias sin renumerar contratos ni evidencia histórica.

### H05 — Entradas de GitHub y arte — ALTA — CORREGIDO

README todavía destacaba muestra 01/72 cuadros y aceptación pendiente. La entrada ahora comunica muestra 02 rechazada, CE parcial, rama/PR y límites. AGENTS aclara la fase real y sustituye un gate inicial escrito como prohibición absoluta pese a existir implementación autorizada. La base de animaciones registra el rechazo; sus capacidades futuras permanecen propuestas.

### H06 — Matriz técnica atrasada — ALTA — CORREGIDO

SYSTEM_MATRIX de GitHub negaba ejecución/lectura de datos mientras Drive ya las registraba. Ahora referencia inspección DAT/MAP, lab CE, navegación y redirección con scope parcial. IDs nativos repetidos no se confunden con la propuesta de IDs semánticos persistentes del juego.

### H07 — CI verde con cobertura incompleta — ALTA — CORREGIDO EN CONFIGURACIÓN

Los runs [38074198813](https://github.com/demianmalkav/VampiroCRPG/actions/runs/38074198813) y [38074194433](https://github.com/demianmalkav/VampiroCRPG/actions/runs/38074194433) pasaron en HEAD 4ef0067. Walk proof descubre tests sólo en tests/, por tanto no verifica tools/research.

Se añade Research evidence: 25 tests existentes, más guards de navegación/redirección con hashes de sus fuentes. Biblioteca estándar, sin originales ni nueva dependencia mayor. Su primera ejecución remota debe consultarse por el SHA de cierre; configuración versionada no equivale por sí sola a run PASS. Tampoco pasa a ser una nueva ejecución conductual del juego.

### H08 — Registro de dudas detrás de la verificación — ALTA — RECONCILIADO

CV-001 aún pedía comprobar el límite sangre/autocontrol, mientras Traducción 01/02 y perfil B ya registran verificación Revised y aplicación. Se conserva la duda histórica y se añade su resolución documental. No se afirma nueva lectura de esas páginas durante esta auditoría; cero sangre/torpor y variantes independientes siguen abiertas.

### H09 — Inventario y estados bibliográficos — MEDIA — PARCIAL

El índice ya advertía que 44 era obsoleto, pero no daba un inventario normalizado vigente. Se añade conteo de 85 archivos PDF y se aclara que estructura estudiada no implica lectura completa. Sigue pendiente una fila canónica por ID/hash/título/edición/duplicado/estado y fuente de evidencia. READ/READ PARTIAL en distintas pasadas exige consolidación, no promoción automática.

### H10 — Ficha fuera de carpeta — MEDIA — ABIERTO

Traducción 12 fue localizada mediante búsqueda exacta fuera de 07_DESIGN. Está viva, su contenido se leyó y el enlace de la reconciliación funciona. Es un problema de organización/descubrimiento, no pérdida de contenido. No se movió ni copió durante esta auditoría.

### H11 — Enlaces y recuperación — BAJA/MEDIA — CORREGIDO EN REPO

Tres enlaces Markdown relativos no resolvían: dos del texto de licencia MakeHuman y uno del LEEME de escena. Los de licencia ahora apuntan a los archivos upstream de la revisión fijada; ambos destinos se comprobaron. El de escena es relativo a su propio directorio. Se añade PROJECT_PROFILE como adaptador estable; no introduce otro master o NEXT.

### H12 — Main y cadena de drafts — MEDIA — ABIERTO POR DISEÑO

Main no contiene los avances de las cuatro ramas/PR apilados. No es pérdida ni commit faltante: la cadena sigue abierta y el juego C está rechazado. La entrada de Drive y el perfil permiten recuperar la rama actual. La portada de main sigue siendo fundacional; no se hizo merge ni se afirmó versión jugable desde main. Revisar la cadena por unidades antes de una integración futura.

### H13 — Historial extenso y duplicación — MEDIA — ABIERTO

Master tenía 206 párrafos y matriz 131 al comienzo del corte; contienen detalles técnicos y varios NEXT históricos. El encabezado actual coincide, pero dificulta localizar qué sigue vivo. Las correcciones agregan marcadores vigentes/históricos; sigue pendiente separar resumen ejecutivo breve de historial enlazado. No eliminar trazas ni reescribirlos como si nunca hubieran sido válidos.

### H14 — Trazabilidad integral de reglas — MEDIA — ABIERTO

Existen anclas fuente en las traducciones y un perfil B estrecho con tests. No se encontró una matriz central completa que enlace cada regla diseñada con edición/página, decisión, implementación, test y cobertura jugable. Las 14 traducciones no son 14 sistemas terminados. Completar progresivamente esa matriz al implementar cada subsistema.

### H15 — Obligatoriedad de checks y releases — BAJA EN PREPRODUCCIÓN — ABIERTO

No hay rulesets y las ramas observadas no exigen checks mediante protección. La disciplina de leases/PR/validación es procedimental. No se cambiaron permisos ni políticas. Tampoco hay releases publicadas; los ZIP de Drive son entregas históricas, no releases aceptadas. Antes de integrar/producción, evaluar protección y un checkpoint/release reproducible.

## Reproducción realizada en esta auditoría

| Comprobación | Resultado | Lo que acredita |
| --- | --- | --- |
| 28 JSON del HEAD auditado | 28 parsean, cero error | Sintaxis; no validez conductual global |
| Tests tools/research | 25/25 PASS | Lectores sintéticos y rechazos de evidencia insuficiente |
| Guard navegación + hashes | PASS, 21 requests / 53 observaciones | Integridad y alcance del experimento archivado |
| Guard redirección + hashes | PASS, 5 escenarios / 429 poses | Integridad y alcance del experimento archivado |
| Unittest tests/ en checkout sin exportaciones | 79 PASS; 1 ERROR HTTP 404 de art/index.json | Precondición faltante de arte generado; no se declara 80 PASS local |
| CI Walk proof en HEAD auditado | Dos runs success | Rebuild/export/tests/navegador/arte dentro del workflow anterior |
| Manifiesto implementación muestra 02 | 21 hashes de texto coinciden; PNG presente en árbol | Sin drift en esos textos; SHA256 del PNG no revalidado aquí |
| Links nativos | 23 destinos distintos resueltos | Documento/metadata accesibles; no descarga completa de todos los PDFs |
| Muestras 01/02 | Metadatos exactos presentes en 09_BUILDS | Disponibilidad de los IDs; no nuevo chequeo ZIP CRC |
| Links relativos GitHub | Tres fallos identificados y corregidos | Navegación local de documentación |

La ausencia de art/index.json en el checkout es coherente con que las exportaciones están excluidas del repositorio y se generan/entregan aparte. No se creó un índice falso ni se omitió el fallo para reportar verde. El manifiesto antiguo se mantiene con su parent original; no es un manifiesto de todos los cambios de investigación posteriores.

La búsqueda por carpeta 09_BUILDS devolvió vacía aunque ambos IDs exactos existen y sus padres son esa carpeta. Una lista vacía del mecanismo de descubrimiento no demuestra borrado. Las comprobaciones binarias/descargas completas que no se hicieron quedan explícitas.

## Estado real que deben preservar todos los controles

- A/B: autorizados y comprobados en su ensayo estrecho; alimentación/Bestia no están integradas espacialmente a C.
- C: muestra 02 rechazada. Caja decorativa transitable, pasos diagonales con velocidad distinta y retroceso al redirigir siguen sin corregir.
- CE: navegación y redirección parcialmente observadas; referencia Linux DAT-only fijada, no el Windows original. Tres casos A2 parciales, nueve sin ejecución; ningún caso constituye aceptación de Vampiro.
- Arte: concepto aprobado; producción animada elegante/coherente todavía sin demostrar. Ropa/armas/combate/NPC/clima/vehículos son requisitos de extensión, no capacidades completadas.
- Campaña: Nueva York, individual primero. Año/dirección exactos, motor productivo y online posteriores abiertos.

## Cierre y continuidad

**DONE:** revisión cruzada y correcciones de control/evidencia descritas; histórico preservado. No se alteraron runtime, saves, originales ni la cadena de PRs mediante merge.

**EVIDENCE:** lecturas vivas, árbol/HEAD, 25 tests y dos guards PASS, 28 JSON válidos, 21 hashes coincidentes, links/metadata y resultados CI con alcance explícito.

**OPEN:** H09/H10/H12/H13/H14/H15 y límites binarios/runtime indicados. La salud documental mejora; no queda certificada como perfecta ni como garantía de calidad del juego.

**NEXT:** cerrar publicación/readback/sincronización de esta auditoría; luego retomar la unidad de puerta/acceso del master. Normalización de biblioteca y consolidación de historial son mantenimiento separado; no deben reabrir investigación general ni detener indefinidamente A2.
