---
name: presentaciones-html
description: Crear o mejorar presentaciones en HTML (decks para exponer en clase, defensas, comités, avances de proyecto, demos de agentes, y también de concepto: naming, marca, pitch, visión) con 6 temas probados, biblioteca de láminas (gestión, ML, corporativas, concepto a sangre con ilustración y animación), builds por clic, chat simulado, notas y ventana del presentador, y exportación a PDF, one-pager y PPTX. También páginas interactivas de lectura y pósters. No usar para editar un .pptx existente (skill pptx), Google Slides, informes de métricas con guía CAS (reporte-uso-agente) ni dashboards en vivo.
---

# Presentaciones HTML

Un archivo HTML autocontenido armado desde piezas: el **motor** (`assets/motor/`: temas, estilos, comportamiento; no se edita), la **plantilla** (`assets/plantilla.html`) y **láminas**, una por archivo, copiadas de la **biblioteca** (`assets/laminas/`) y editadas. Todo sale de presentaciones reales del autor y fue revisado por un equipo de UI y por profesores, gerentes y líderes de proyecto simulados (ver «Lo que pidieron los evaluadores»).

`K` = `~/.claude/skills/presentaciones-html` (carpeta de esta skill).

## Pasos

1. **Brief.** Audiencia, duración (¿incluye plenario?), quién expone y cómo se reparte, dónde se proyecta (sala con luz, sala oscura, pantalla, PDF reenviado, celular), rúbrica o pauta (leerla), feedback previo, fuentes de datos, demo sí/no. Leer `README`/`AGENTS.md`/`CLAUDE.md` del proyecto. Decidir el **nivel de diseño** y escribirlo en `<html data-diseno="…">`:
   - `gestion` (por defecto): avance, comité, clase, defensa, decisión. Sobrio; la biblioteca resuelve casi todo.
   - `concepto`: naming, marca, pitch, visión, lanzamiento, «explicar una idea». Aquí el diseño es el mensaje: leer `K/references/concepto.md` antes del esqueleto. Si el pedido mezcla ambos (p. ej. un comité que elige un nombre), es `concepto`; si no se puede deducir, preguntarlo con una línea.
   Terminado cuando puedes escribir la tesis en una frase, la decisión o evaluación que se espera y el nivel de diseño.
2. **Tema y esqueleto.** Elegir tema con la tabla de abajo y leer `K/references/narrativa.md` (perfil de audiencia + catálogo). Escribir la lista de láminas: título-afirmación + archivo de la biblioteca (en `concepto`: **qué se ve**, la idea visual de la lámina, aunque no exista en la biblioteca) + `data-ruta` + qué se dice (+ quién, segundos y criterio de rúbrica si es grupal). Si el pedido es amplio o hay rúbrica, mostrar la lista antes de construir. Terminado cuando cada lámina tiene una afirmación distinta y cada cifra tiene origen (en `concepto`, además: un momento memorable y alternancia de fondos, ver `concepto.md`).
3. **Construir.** En la carpeta del proyecto (p. ej. `presentacion/`): copiar `K/assets/plantilla.html` como `fuente.html` y las láminas elegidas de `K/assets/laminas/` a `presentacion/laminas/` (renombrar con prefijo de orden: `01-portada.html`). Ajustar las líneas `<!--#incluir laminas/…-->` (la plantilla trae ejemplos: si no se copia la lámina, armar la toma de la biblioteca y falla por `data-plantilla`) y `data-tema`. No copiar `motor/`: `armar.py` lo toma de la skill. Rutas de imágenes e includes: relativas al archivo que las contiene (o a `fuente.html`); los includes pueden anidarse. En cada lámina copiada:
   - Reescribir contenido, **quitar `data-plantilla`** (armar falla si queda) y mantener el id único (`s-…`; los `<marker>`/`<defs>` SVG con prefijo del id).
   - Anatomía: `.kicker` → `h2` afirmación → `.bajada` → `.cuerpo` → `<footer class="pie">` (fuente o advertencia, con `.marca real|ilustrativo` si aplica) → `<aside class="notas">` (lo que se dice) → `<div class="tecnico">` opcional (respaldo, tecla T; sin `<div>` anidados).
   - Exposición grupal: `data-quien`, `data-seg`, `data-rubrica` en el `<section>`, `data-anexo` en el respaldo y `<b class="puente">` en las notas de la última lámina de cada expositor (ver «Exposición grupal evaluada» en `narrativa.md`).
   - Builds: `data-paso="n"` aparece y se queda; `data-solo="n"` solo en ese paso (dentro de `.apilar`); `data-foco="n"` en un contenedor atenúa todo menos `.sel`/`.on` desde el paso n. Entrada escalonada: `class="rise" style="--i:n"` (nunca en el mismo elemento que `data-paso`). Trazos: `class="dibujar"` (dentro de su `data-paso` si es un build). En SVG, `data-paso` en un `<g>` solo cambia la opacidad (su `transform` se respeta). Cifras: `<span data-contar="57" data-suf=" %">57 %</span>`.
   - Gráficos que avanzan con el relato: script junto a la lámina con `(window.ESCENAS ??= {})["s-id"] = (paso, s, {instantaneo}) => {…}` y `data-pasos="N"` (ejemplo: `laminas/serie.html`).
   - Chat: `data-chat="NOMBRE"` y `(window.CHATS ??= {}).NOMBRE = [...]` (ejemplo: `laminas/chat.html`; tipos de parte `text`, `tool`, `confirmar`, `aviso`).
   - Color solo con tokens (`var(--accent)`, `--support`, `--ia`, `--good/--warn/--bad`) y variables locales (`--c`, `--cols`, `--split`, `--v`). Clases de lámina: `lleno` (veredicto), `oscura` (cierre), `compacta` (contenido arriba, para tablas), `sangre` (degradado oscuro del tema) y `bruma` (degradado claro).
   - Estilo propio de la presentación (paleta de marca, fuente display, una variante de componente): `estilo.css` junto a la fuente, enlazado después de `motor/deck.css` con `<link rel="stylesheet" href="estilo.css">` (armar lo incrusta). Ahí se redefinen tokens (`:root{--accent:…;--f-display:…}`) y se crean clases; el motor no se edita.
   - Íconos: el set base `motor/iconos.html` (la plantilla ya lo incluye): `<svg class="i"><use href="#i-servidor"/></svg>`. Lista y uso en `componentes.md` §13.
   - Cifras de un análisis: en `datos.json` generado por el notebook/script y leídas desde `window.DATA`; nunca a mano.
   - Lo que no está en la biblioteca (simulador con sliders, heatmap con tooltip, ranking que se reordena, mapa persistente, Chart.js, flip/quiz, página con scroll, póster, **diagramas SVG propios generados con Python**): `K/references/componentes.md`.
   - Espacio: si las tarjetas quedan como franja baja en medio de la lámina, usar `.grilla.llena`; con 5 alternativas, tarjetas de 5 columnas solo con texto muy corto.
4. **Armar y revisar.** `python3 K/scripts/armar.py fuente.html Presentacion_<Tema>.html [--datos datos.json] [--pre "python3 graficos.py"] --guion GUION.md --pdf Presentacion_<Tema>.pdf --hojas hojas.png` (+ `--duracion MIN --rubrica C1,C2,…` si es evaluada, `--resumen OnePager.pdf` si hay láminas `data-resumen`, `--pptx` si piden PowerPoint, `--offline` si se presentará sin internet). Guardar el comando en `armar.sh` junto a la fuente. Mirar las hojas de contactos (`--hojas`): huecos, texto chico, tarjetas que se repiten; en `concepto`, además, si la hoja se ve plana (todas claras, todas con la misma estructura, nada que recordar), rediseñar antes de seguir. Terminado cuando no hay `ERROR` y cada `aviso` está corregido o justificado (`data-densa` sube el tope a 90 palabras: solo para tablas de gestión, citas o comparaciones que no se pueden partir).
5. **Verificar en el navegador.** Servir la carpeta con `python3 -m http.server <puerto libre> --bind 127.0.0.1` en segundo plano y abrir con `preview_start`. Recorrer todas las láminas y pasos con →; mirar el último paso de cada build; probar ← en láminas con chat o escenas, `#n.p`, `#s-id`, N/T/O/P y el preset `mobile`. Si el panel está oculto las transiciones no avanzan: comprobar estados finales (clases `.ver`, textos) en vez de opacidades a mitad de camino. Revisar el PDF (una página por lámina, nada cortado). Apagar el servidor.
6. **Entregar.** HTML + PDF + `GUION.md` + one-pager/PPTX si se pidieron, y los entregables previos que pida la pauta (ficha, resumen). El guion se regenera en cada armado: quién/tiempos salen de `data-quien`/`data-seg` y las preguntas probables y el plan B de `<template id="guion-extra">` en la fuente. `fuente.html`, `laminas/`, `armar.sh` y `datos.json` quedan junto al HTML para regenerar. Regenerar o marcar como desactualizadas las exportaciones anteriores.

## Temas

`<html data-tema="…">` en la fuente; `?tema=…` en la URL para comparar. Lista y fuentes en `K/assets/motor/temas.js`.

| Tema | Estilo | Cuándo |
|---|---|---|
| `industrial` (por defecto) | gris acero, naranjo de seguridad, condensada | Ingeniería, operaciones, gerencia de planta. El mejor en proyector con luz, PDF y celular. |
| `clinico` | celeste claro, teal y coral, tarjetas redondeadas | Salud, servicios, estándar sobrio para avances de equipo. |
| `editorial` | blanco, tinta y dorado, titulares pesados | Comités ejecutivos, directorio, documentos que se reenvían. El más formal. |
| `papel` | cartográfico claro, titulares condensados, tarjetas con filete | Territorio, sostenibilidad, mapas, series históricas. Titulares condensados. |
| `noche` | oscuro técnico, naranjo y teal, etiquetas mono | Demo técnica en sala oscura o pantalla grande. No con proyector y luz. |
| `envio` | oscuro cálido (marino y kraft) | Variante oscura cálida (kraft) con metáfora logística; mismas condiciones que noche. |

Si la persona no indica nada: proyectado o reenviado → `industrial`; salud o servicios → `clinico`; directorio → `editorial`. Los temas oscuros solo si lo pide o si es una demo en pantalla. En `concepto`, el contraste se logra dentro de un tema claro con láminas `sangre` y `bruma` (sirven con proyector y luz).

## Biblioteca de láminas (`K/assets/laminas/`)

Apertura: `portada` (pregunta), `portada-corporativa` (logo, confidencialidad, versión), `agenda`, `postura` (la decisión en el primer minuto). Problema y datos: `cifra` (mega-cifra + KPI), `ecuacion` (A × B × C = resultado), `serie` (avanza por clic), `datos-particion` (n, desbalance, partición sin fuga). Método y resultados: `opciones` (3 alternativas con foco), `flujo` (diagrama narrado), `resultados-ic` (punto + intervalo, n, CV/test), `matriz` (confusión con costo de errores). Demo: `chat`. Gestión: `estado` (semáforo), `hitos` (con «hoy»), `riesgos` (dueño y mitigación), `gobernanza`, `decision` (monto, plazo, responsable, criterio de éxito y de parada). Argumentar (caso ético, debate, defensa): `marcos` (marcos × alternativas, dónde chocan), `citas` (código o norma con artículo), `objeciones` (contraargumento fuerte → respuesta), `escalamiento` (escalera de peldaños). Cierre: `limitaciones`, `veredicto`, `plenario` (pregunta, votación y quién responde), `cierre`. Concepto y marca: `sangre` (manifiesto o portada a sangre con tipografía display y textura), `revelacion` (nombre o concepto con ilustración grande que se dibuja y letras que entran), `finalistas` (3–4 opciones en tarjetas altas con arte), `red` (grafo que crece por clic y propaga un pulso), `zoom` (la cámara se aleja de una pieza al todo). Referencia: `iconos` (el set base con sus nombres).

Para ver todas en un tema: `python3 K/scripts/armar.py K/assets/muestrario.html /tmp/m.html --muestra` y abrir con `?tema=…`.

## Controles (para contarle a la persona)

→/Espacio/clic en el 75 % derecho avanza paso o lámina (un clic durante el chat completa el turno) · ←/clic en el 25 % izquierdo retrocede sin animar · `F` pantalla completa · `P` ventana del presentador (notas, reloj, tiempo de la lámina vs. plan, quién expone y a quién pasa, puente, botones para ir a un anexo y volver; `R` reinicia) · `N` notas en la misma pantalla (solo para ensayar) · `O` vista general · `T` detalle técnico · `?` ayuda · URL `#5.3`, `#s-id`, `#s-id.2`, `?tema=`, `?resumen`, `?imprimir`. Para ocultar el nombre de quien expone: `<html data-quien-oculto>`.

## Lo que pidieron los evaluadores (aplicar siempre)

- **Profesores (exposición grupal):** reparto equitativo de tiempo, quién habla visible, cada criterio de la rúbrica con al menos una lámina (también el de debate/tiempo), objeciones en el cuerpo y no solo en el anexo, marcos que muestran su tensión en vez de «todos coinciden».
- **Profesores:** título-afirmación sin lenguaje causal si el dato es correlacional; n, conjunto (CV o test) e intervalo visibles en toda lámina de resultados; matriz de confusión y partición de datos en proyectos de ML; fuente en el pie con marca «real» o «ilustrativo».
- **Gerencia:** lámina de decisión con costo, ahorro, plazo, responsable, criterio de éxito y de parada; jerga traducida («detecta 81 de cada 100 fallas»; el término técnico va en `.tecnico`); one-pager con `data-resumen`; nada de «examen» ni «equipo 4» en decks para clientes.
- **Comités / salud:** portada corporativa, agenda, gobernanza (quién decide, qué datos, qué se registra, qué pasa si falla); demo de chat con confirmación humana explícita y un caso límite; temas claros.
- **Líderes de proyecto:** estado con semáforo, hitos con «hoy», riesgos con dueño; una lámina por archivo para que varias personas editen sin conflictos.

## Errores ya cometidos (el linter de armar.py detecta los marcados con ✓)

- ✓ `.rise` y `data-paso` en el mismo elemento: la animación anula el build.
- ✓ ids duplicados (también dentro de `<defs>` SVG): `url(#id)` apunta a otra lámina.
- ✓ Láminas de biblioteca entregadas sin editar; `data-chat` sin guion; colores hex fuera de `<defs>`; `font-family` fijo en SVG.
- ✓ Atributo repetido en una etiqueta (`style` dos veces: el navegador ignora el segundo); imagen o include que no existe; `ESCENAS` con id que ya no existe.
- ✓ Reparto de tiempo desigual, plan sin 10 % de margen, criterio de rúbrica sin lámina (con `--duracion` y `--rubrica`).
- ✓ Ícono usado sin incluir `motor/iconos.html` o con nombre que no existe.
- ✓ (`concepto`) Quedarse en tarjetas de la biblioteca cuando el pedido es de concepto o de marca: más de la mitad de las láminas solo texto o tarjetas, ninguna lámina que cambie el fondo, o tres seguidas de tarjetas. También avisa si no hay ningún elemento de alto impacto. Salió plana una presentación de naming que solo tenía ilustraciones chicas junto a tarjetas blancas.
- Completar el guion a mano: se sobrescribe en el próximo armado. Usar `data-quien`/`data-seg` y `<template id="guion-extra">`.
- Notas fuera de su `<section>` (se desalinearon); contador o número de lámina escrito a mano.
- Fuentes en `vw` dentro del escenario; cascadas de `<style>` con `!important` por lámina: crear una variante de componente.
- Una clase con `opacity` fija sobre un elemento con `data-paso` (misma especificidad: el build no aparece).
- Gráficos con datos inventados presentados como reales: usar `.marca ilustrativo` o datos reales.
- PDF/PPTX viejos junto a un HTML nuevo.
