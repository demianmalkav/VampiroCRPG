# Investigación previa: ingeniería inversa y ecosistema de Fallout 2

Fecha: 9 de octubre de 2026, Argentina; 10 de octubre UTC. Estado: inventario y lectura dirigida completados; asimilación funcional y selección de motor pendientes.

## Conclusión ejecutiva

Ya existe suficiente código reconstruido y documentación pública para comenzar la asimilación por subsistemas. No hace falta iniciar una decompilación general de Fallout 2. La prioridad es aprovechar ese corpus, fijar variantes y comprobar los comportamientos que importan al proyecto. Este hallazgo no demuestra todavía cuál será el motor de producción más económico.

El inventario comprende 18 repositorios con revisiones exactas y 75 recursos recuperados. Se revisaron pasajes pertinentes de código y documentación, no todos los archivos ni todos los subsistemas. La cobertura se registra en [el manifiesto](SOURCE_INVENTORY_2026-10-09.json). No se ejecutó ningún motor, editor o compilador externo, ni se inspeccionaron los DAT originales en esta pasada.

La investigación previa del proyecto se concentraba en causalidad, scripts, persistencia y economía de acciones. La muestra recorrible rechazó en la práctica nuestra suposición de que esa comprensión bastaba para construir una presentación espacial sólida. Esta revisión añade geometría, bloqueo, selección con cursor, recursos, animaciones, equipo visible y herramientas de producción.

## Fuentes y variantes principales

Las fechas corresponden al último commit de la rama por defecto consultada, no a la fecha de actualización del repositorio ni a una garantía de mantenimiento. Las revisiones completas están en el manifiesto; los enlaces siguientes fijan los textos examinados.

| Fuente | Evidencia y alcance | Utilidad y límite para VampiroCRPG |
| --- | --- | --- |
| [Fallout 2 Reference Edition](https://github.com/alexbatalov/fallout2-re/blob/b135fc46ef40c4aecd156f3cebcf88ec531bb8ac/README.md) | Código reconstruido del binario. Su autor declara que lo esencial para jugar está reconstruido; quedan pocas funciones no esenciales. Último commit observado: 2023-01-20. | Referencia principal para investigar mecanismos cercanos al original, incluidas imperfecciones. No afirmar equivalencia binaria completa ni que sea el código original publicado por Interplay. |
| [Fallout 2 Community Edition](https://github.com/alexbatalov/fallout2-ce/blob/e97087b9582f37075db347a89898887320753f8b/README.md) | Derivada de RE, multiplataforma, con correcciones y funciones adicionales. Rama examinada: 2025-02-16; última release observada: v1.3.0, 2024-04-21. | Base más legible y candidata a laboratorio ejecutable. No confundir el HEAD consultado con la release, ni las correcciones CE con conducta original. |
| [sfall](https://github.com/sfall-team/sfall/blob/6c65e67342bda1488671601e417194199ec72a09/README.md) | Extensiones mediante DLL que modifica el ejecutable en memoria; hooks y opcodes adicionales. Commit observado: 2026-10-03. | Muestra cómo se extendió Fallout 2 en la práctica. No es un motor independiente ni una DLL que podamos cargar indistintamente en CE. |
| [rotators / fodev](https://github.com/rotators/fallout2-docs/blob/fa5b3a90b342975998f10e270c5cd7f5293af9e9/README.md) | Documentación mantenida de formatos, comportamiento, símbolos y herramientas. Commit observado: 2026-09-12. | Guía para localizar datos y reconstruir relaciones entre formatos. Las afirmaciones críticas se cruzan con código; una descripción no sustituye un lector probado con archivos reales. |
| [JanSimek / fallout2-modding](https://github.com/JanSimek/fallout2-modding/blob/a892a3ee901931d34a9ed77b4653da0ab14382c6/README.md) | Documentación de SSL, API y formatos; incluye material de editor. Commit observado: 2026-01-22. | Segunda guía de navegación y comprobación. Se examinó arquitectura de formatos, no toda la API ni los PDF del repositorio. |
| [FOnline actual](https://github.com/cvet/fonline/blob/8b6a5f60204e6f24623a6c6341e66c0a22fc1aeb/README.md) | Motor distinto, orientado a multijugador, con autoridad de servidor, herramientas y recursos propios. Commit fijado: 2026-10-09 UTC. | Candidato por geometría, ropa y armas compuestas. No es Fallout 2 decompilado ni incorpora automáticamente su campaña o todas sus mecánicas. No seleccionado. |

### Compatibilidad que no debemos dar por supuesta

El README de CE declara soporte parcial para conversiones: Nevada y Sonora originales probablemente funcionan cuando no necesitan sfall extendido, sin confirmación de recorrido completo; Restoration Project, Fallout et Tu y Olympus 2207 no están soportados en el estado documentado. Esta es una declaración upstream, no una prueba nuestra. La existencia de un mod exitoso sobre el ejecutable clásico no prueba compatibilidad con CE.

Debemos anotar, en cada observación, si procede de ORIGINAL, RE, CE, SFALL o de OTRO MOTOR. Las conclusiones sólo pasan a nuestra arquitectura después de una prueba pertinente y de reconciliarlas con los requisitos de Vampiro.

## Documentación técnica disponible

| Recurso | Qué permite investigar | Comprobación hecha y trabajo pendiente |
| --- | --- | --- |
| DAT | Archivos de recursos y precedencia de búsqueda/parches. | Documentación recuperada; faltan extracción y validación de un archivo legalmente disponible. |
| FRM / PAL / FID / LST | Fotogramas, orientaciones, anclajes, selección de arte y relación con listas. | FRM y LST contrastados con `art.cc`, `art.h` y animación. PAL localizado, no analizado de forma completa. |
| PRO | Prototipos de ítems, personajes y decorado; referencias de arte y campos según subtipo. | Lectura dirigida de documentación y `proto_types.h`. Falta comprobar prototipos concretos y validar un cambio de equipo. |
| MAP | Instancias, posición, elevación, flags, inventario y registros de scripts. | Descripción contrastada con consultas de bloqueo y dibujo. No se escribió un parser ni se probó round-trip. |
| SSL / INT / MSG / SCRIPTS.LST | Fuente de scripts, bytecode, texto y registro de ejecución. | Se revisaron relaciones y límites de compilación/decompilación. No se compiló ni ejecutó un script. |
| SAVE.DAT y archivos asociados | Persistencia coordinada, mapas visitados y extensiones. | Documentación recuperada; se mantuvo la corrección previa sobre vida de timers. Falta medir partidas y acciones en curso en el runtime de referencia. |
| Símbolos, structs e IDA | Correspondencia entre funciones y ejecutable. | Índices y enlaces localizados. Bases IDA y binarios no descargados ni verificados. Sólo útiles si aparece una discrepancia que el código público no resuelve. |

Índice operativo: [fodev](https://fodev.net/files/fo2/). Las referencias exactas por archivo están en el manifiesto. La documentación más reciente combina información histórica con CE/sfall: su fecha reciente no transforma una extensión en función del original.

## Herramientas y material práctico

| Herramienta o corpus | Hallazgo | Uso propuesto y precaución |
| --- | --- | --- |
| [Gecko](https://github.com/JanSimek/gecko/blob/c14c0438468976bf91e1cf55603c62571e05eaef/README.md) | Editor con código, Qt6/SFML3, capas, edición de objetos y objetivo de compatibilidad con mapas clásicos. Commit observado: 2026-10-09. | Evaluar para inspeccionar un mapa y evitar inventar un editor. Su configuración utiliza recursos de Fallout; instalación y mapas no probados aquí. |
| [SSLC](https://github.com/sfall-team/sslc/blob/3991207639c133bd14948fae6c18df59310b5287/README.md) | Compilador/parser con preprocesado y opciones de compatibilidad. | Herramienta para un script mínimo. Encabezados, opciones y opcodes deben coincidir con el runtime. La búsqueda inicial `BGforgeNet/sslc` dio 404; la fuente verificada es `sfall-team/sslc`. |
| int2ssl | Recuperación de texto legible desde INT; distribución documentada en modderspack de sfall. | Inspección y recuperación, no sustituto perfecto del SSL original. Comentarios y estructura original no se recuperan automáticamente. Ejecutable no verificado. |
| [BGforge MLS](https://github.com/BGforgeNet/BGforge-MLS/blob/55caa048f09e4f894f42e32ec079825083c7d598/README.md) | Integración de editor para scripts y herramientas de contenido. | Evaluar completado, navegación y compilación después de fijar el runtime; no instalar por disponibilidad solamente. |
| [dat-unpacker](https://github.com/falltergeist/dat-unpacker/blob/d536ef630d9a47e866cddd7e826480c3ac34bb3d/README.md) | Extracción DAT1/DAT2 por CLI y normalización opcional a minúsculas. | Extracción de laboratorio. El README describe extracción; no inferir capacidad de empaquetado. |
| [frm2png](https://github.com/falltergeist/frm2png/blob/4788b4d0ed8aa67571871714372eb92e4ede6829/README.md) | Conversor FRM a PNG. | Inspección visual. Validar conservación de offsets, direcciones y metadatos por separado: obtener un PNG no prueba fidelidad del ciclo. |
| [Visor de rotators](https://github.com/rotators/fallout-animations/tree/95f6469096cb71694249fac7bcef48cfba0ac882) | Código de visor y conversión; commit de rama observado: 2026-03-07. | Estudiar catálogo y secuencias; no reutilizar los sprites del juego como contenido propio. |
| [Unofficial Patch](https://github.com/BGforgeNet/Fallout2_Unofficial_Patch/tree/aced3527b56d3f73ee03a21ef567886b0dde66ac/scripts_src) | Árbol SSL disponible y correcciones mantenidas. | Corpus de patrones y fallos. Son scripts modificados de contenido, no una licencia automática para distribuir una nueva campaña. Sólo se verificó la presencia del árbol, no se absorbió íntegro. |
| [Hero Appearance](https://github.com/BGforgeNet/Fallout2_Hero_Appearance/blob/d9533daa062d34d315b720b3331ab4c8c242ed6d/README.md) | Colección de variantes del jugador que requiere sfall; advierte que algunos conjuntos pueden estar incompletos. | Evidencia de personalización posible y del costo de completar catálogos. No prueba composición libre de prendas ni identidad exacta de cada arma. |
| BIS Mapper, Dims Mapper, FRM Workshop y FORT | Localizados en índices o repositorios públicos. FORT se presenta como WIP. | Candidatos secundarios; no descargados ni ejecutados. Evitar montar todos antes de escoger la tarea de laboratorio. |

El paquete histórico de scripts oficiales fue localizado mediante un enlace RAR, pero no se abrió: no declararlo verificado ni confundir el árbol de Unofficial Patch con los scripts originales exactos.

## Fuentes históricas y proyectos alternativos

DarkFO está archivado, con commit de rama observado de 2019; conserva investigación útil sobre mapas y luz. Falltergeist tiene código y una rama `develop` cuya última revisión observada es de 2022. FOClassic está archivado y documenta una cadena de compilación antigua. Son material de consulta, no candidatos elegidos para producción. No confundir FOClassic, FOnline moderno y juegos particulares de FOnline.

Se encontró también jsFO, cuyo autor declara que cesó su desarrollo. Sirve como precedente de representación de Fallout en navegador, sin demostrar que sea una base mantenida para nosotros. No se inventarió todo su código.

La búsqueda halló un tutorial de su autor sobre crear un personaje en Blender, renderizar seis direcciones e integrarlo como FRM/PRO. La página completa devolvió 403 y sus adjuntos no se verificaron. Por ahora es una pista de flujo artístico, no una receta validada: [referencia localizada](https://www.nma-fallout.com/threads/making-a-new-critter-for-fallout-2.219904/).

## Reutilización y derechos: conclusión acotada

- RE y CE declaran Sustainable Use License. El texto de CE limita usos y distribución; no debe tratarse como permiso general para vender un juego derivado.
- sfall declara GPLv3. FOnline actual tiene texto MIT examinado. Gecko declara Apache 2.0. La licencia de una herramienta o motor no concede derechos sobre los recursos del juego que abre.
- No se emitió dictamen jurídico ni se comprobó cada dependencia. Herramientas sin licencia clara en la documentación leída quedan pendientes de revisión antes de incorporar código.
- Esta actualización guarda conclusiones originales, enlaces y metadatos. No incorpora código externo, mapas, arte ni scripts de Fallout al proyecto.

## DONE / EVIDENCE / OPEN / NEXT

**DONE:** inventario fechado y fijado por revisiones; fuentes y variantes separadas; lectura dirigida de subsistemas espaciales y artísticos; plan de asimilación con criterios de salida.

**EVIDENCE:** manifiesto de repositorios/archivos; funciones examinadas en [el análisis espacial](SPATIAL_ART_ANIMATION_FINDINGS_01.md); límites de cada fuente expuestos aquí.

**OPEN:** ejecutar un laboratorio de referencia; costo de adaptar cada base; identidad visual de equipo; comportamiento exacto al interrumpir y guardar acciones; motor de producción; acabado artístico.

**NEXT:** ejecutar A1 del [plan de asimilación](ASSIMILATION_PLAN_01.md). No continuar ampliando la muestra rechazada ni iniciar una lectura indiscriminada del corpus.
