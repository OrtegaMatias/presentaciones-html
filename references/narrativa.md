# Narrativa, audiencias y guion

## Reglas de contenido (todas las audiencias)

- **Título-afirmación** en toda lámina de resultado: la conclusión, no el tema («Resultados» ✗ → «El modelo elegido detecta 81 de cada 100 fallas» ✓). Las explicativas pueden usar pregunta. Si el dato es correlacional, el título también: «suben *junto con*», no «suben *porque*».
- **Una idea por lámina**, ~40–60 palabras visibles. Lo demás va en `<aside class="notas">` (lo que se dice) o `.tecnico` (respaldo, tecla T). Tablas de gestión pueden llegar a ~100 con `data-densa`.
- **Cifras con origen**: cada cifra en pantalla tiene fuente en `.pie` y marca `.marca real` o `.marca ilustrativo`. Dato faltante → `[POR CONFIRMAR]` visible, nunca inventado. Cifras de un análisis llegan por `datos.json`.
- **Decisiones metodológicas no obvias en la lámina** (pie o nota corta), no solo en las notas: un profesor preguntó por qué se entrenó con 7.000 filas porque no estaba a la vista.
- **Honestidad**: lámina de limitaciones; lo propuesto separado de lo hecho; «la decisión es de una persona» cuando hay IA.
- **Fidelidad**: al migrar material existente (PPT, diagramas, UI real), reproducirlo; ante la duda, construir una lámina y validarla.

## Perfiles de audiencia

Elegir uno en el paso 2; define tema por defecto, láminas obligatorias y registro.

| Perfil | Tema | Láminas obligatorias | Registro |
|---|---|---|---|
| **Académico** (certamen, defensa, taller) | `industrial` o `clinico`; el que pida el curso | portada, problema/cifra, datos-particion, método, resultados con n e intervalo, (ML: matriz), demo si existe, limitaciones, cierre con declaración de uso de IA | Técnico. Código de rúbrica en el kicker («R4 · Modelos»); orden según la rúbrica; responder el feedback previo explícitamente |
| **Gerencia / cliente** | `industrial` o `editorial` | portada-corporativa, cifra, opciones (en lenguaje llano), decision (`data-resumen`), riesgos, hitos | Sin jerga en pantalla: «detecta 81 de cada 100 fallas»; nombres de modelos y métricas a `.tecnico`. Decir si los datos son propios o públicos. Nada de «examen», «equipo 4», «deck de muestra» |
| **Comité / directorio / salud** | `editorial` o `clinico` | portada-corporativa (confidencialidad, versión), agenda, decision, gobernanza, riesgos | Sobrio. Gobernanza antes de que la pregunten. Demo con confirmación humana y un caso límite |
| **Avance de proyecto** (equipo, PMO, cliente recurrente) | `clinico` o `industrial` | estado (semáforo), hitos con «hoy», riesgos con dueño, próximos pasos/decisiones pendientes | Empezar por lo rojo y qué se necesita de quién. Una lámina por archivo |
| **Demo técnica** | `noche` o `envio` (sala oscura) | portada, flujo, chat o demo en vivo, limitaciones | Ritmo rápido, builds cortos; plan B en notas |
| **Caso ético / defensa de postura / debate** | `industrial` o `papel` | portada-pregunta, `postura` (primer minuto), cifras del enunciado, actores (quién decide vs. quién se expone), `opciones` (3–5 alternativas con foco), `marcos` (tensión entre marcos, no unanimidad), `citas` (códigos con artículo), `objeciones` en el cuerpo, plan con costos y `escalamiento`, respuesta literal a cada pregunta guía, `veredicto`, `plenario` | La decisión va primero, no al final. Solo las cifras del enunciado; el resto «por medir». Reconocer el costo de la propia postura (*steelman*) antes de que lo pregunten |

## Rigor para resultados (ML y análisis cuantitativo)

Toda lámina de resultados muestra, en pantalla:

1. **Métrica + conjunto + n**: «recall en test, n = 2.000 (68 fallas)». Separar elección (validación cruzada) de confirmación (test).
2. **Incertidumbre**: intervalo (bootstrap o CV) con `laminas/resultados-ic.html`. Si los intervalos se solapan, decirlo en el pie.
3. **Errores con costo**: matriz de confusión (`laminas/matriz.html`) y qué cuesta cada tipo de error; el umbral se justifica por costo.
4. **Datos**: tamaño, desbalance, partición (temporal si se predice el futuro) y chip «sin fuga» solo si es verdad (`laminas/datos-particion.html`).
5. **Gráficos honestos**: ejes con título y unidad, bandas o resaltados con rótulo (nada decorativo), etiquetado directo sobre la línea.
6. **Asociación ≠ causa** en importancia de variables y series.

Componentes adicionales en `componentes.md`: curva de costo vs. umbral con sliders, heatmap con tooltip, curvas PR/ROC con SVG a mano.

## Arco recomendado

Pregunta/gancho → problema en una cifra → datos y alcance → método → resultados (una lámina por hallazgo) → demo → decisión o recomendación → riesgos y limitaciones → cierre que vuelve a la pregunta inicial → anexo de respaldo (después del cierre, con `data-anexo`).

**Defensa de postura (caso ético, debate):** pregunta → **postura** → caso en cifras → diagnóstico técnico → actores → alternativas → marcos en tensión y códigos → objeciones más fuertes → plan, costos y escalamiento → respuesta a las preguntas guía → veredicto → plenario → anexo.

## Exposición grupal evaluada

- **Reparto en la lámina:** `data-quien="Nombre"` y `data-seg="75"` en cada `<section>`; `data-rubrica="C1 C3"` con los criterios que cubre; `data-anexo` en el respaldo. El motor muestra quién expone (esquina superior derecha) y el presentador compara tiempo real contra plan. `armar.py --guion … --duracion 20 --rubrica C1,C2,C3,C4` calcula acumulados, totales por expositor (aviso si alguien se desvía > 15 % del promedio) y la cobertura de la rúbrica (aviso si un criterio no tiene lámina; el de «manejo del debate» lo cubren `objeciones` y `plenario`).
- **Puentes:** en la última lámina de cada expositor, `<b class="puente">«¿Quién carga con el riesgo? Les cuenta Matías».</b>` dentro de las notas. El presentador la destaca y el guion la separa.
- **Notas:** lo que se dice, en primera persona; las acotaciones van entre corchetes (`[clic]`, `[pausa]`). No repetir nombre ni tiempo dentro del texto: van en `data-quien` / `data-seg`.
- **Preguntas y plan B:** en la fuente, `<template id="guion-extra">` con la tabla de preguntas probables (pregunta, quién responde, respuesta corta, lámina de respaldo); `armar.py` la copia al guion en cada armado (el guion se regenera: no editarlo a mano).
- **Entregables previos:** si la pauta pide ficha, informe o resumen antes de exponer, tratarlos en el paso 6.

`data-ruta` arma la agenda permanente (barra superior): 4–6 etapas cortas. Una metáfora temática (etapas de un envío) solo si el dominio la sugiere.

## Catálogo de tipos de lámina

| Tipo | Archivo en la biblioteca / técnica |
|---|---|
| Portada-pregunta · corporativa · agenda | `portada` · `portada-corporativa` · `agenda` |
| Mega-cifra con KPI | `cifra` |
| Serie que avanza por clic | `serie` (`ESCENAS`) |
| Datos y partición | `datos-particion` |
| Comparación con foco en la elegida | `opciones` (`data-foco`) |
| Diagrama narrado | `flujo` (nodos y flechas por paso) |
| Resultados con intervalo · errores | `resultados-ic` · `matriz` |
| Demo de chat | `chat` (`CHATS`, partes `confirmar` y `aviso`) |
| Estado · hitos · riesgos · gobernanza · decisión | `estado` · `hitos` · `riesgos` · `gobernanza` · `decision` |
| Limitaciones · veredicto · cierre | `limitaciones` · `veredicto` (`.lleno`) · `cierre` (`.oscura`) |
| VS / antes-después | `.dos` con dos cifras; `data-solo` dentro de `.apilar` |
| Caos → orden | dos láminas `flujo` con el mismo lenguaje visual |
| Dolores tachados | lista con `.tachado` que da paso a la solución |

## Guion (`GUION.md`, lo genera `armar.py --guion`)

Sale de las notas de cada lámina (una sola fuente). Completar a mano:

```markdown
| # | Lámina | Quién | Tiempo | Acumulado |
### n · Título   ← texto para DECIR, con [clic] donde avanza un paso
## Preguntas probables   | Pregunta | Respuesta corta | Lámina de respaldo |
## Si falla la demo      plan B: captura en lámina X / video local
```

## Tiempos

Planificar al **90 %** del bloque (10 % de margen) y ensayar a esa meta (el guion la calcula por expositor). Con plenario, restarlo antes: 20 min con 5 de plenario → 18:00 planificados en total, 13:00 de exposición.
Promedio 45–75 s por lámina: 7 min → 7–10 láminas; 15 min → 12–16; gerencia 5 min → 4–6, una idea cada una. Las láminas de anexo no cuentan.
