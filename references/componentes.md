# Componentes avanzados

Patrones probados en presentaciones anteriores. Copiar y adaptar a los tokens del motor (`assets/motor/deck.css`; usar `var(--…)`, nunca hex sueltos; en JS leer tokens con `getComputedStyle`). Antes de construir algo de aquí, revisar si ya existe en `assets/laminas/`.

```js
const css = getComputedStyle(document.documentElement), tok = n => css.getPropertyValue(n).trim();
```

## Índice

1. Gráficos SVG a mano (helper `el`, escalas, etiquetado directo)
2. Serie que avanza por tramos con cada clic (`ESCENAS`)
3. Ranking que se reordena
4. Heatmap con tooltip
5. Simulador con sliders (umbral/costo)
6. Panel persistente (mapa/figura que cambia capas entre láminas)
7. Chat guionado avanzado (composer, pills, formulario, antes/después)
8. Chart.js con tokens (cuando haya muchos datos)
9. Interactivos para páginas de lectura: flip, quiz, acordeón, timeline doble carril, partículas
10. Página larga con scroll (alternativa a slides)
11. Póster / PDF vectorial
12. Ilustraciones SVG generadas con Python (diagramas técnicos propios)
13. Set base de íconos
14. Componentes de concepto (sangre, display, texturas, revelación, grafo, zoom)

---

## 1. Gráficos SVG a mano

Sin librerías para ≤ ~200 puntos. Etiquetar directo sobre la línea/barra, sin leyenda aparte.

```js
const NS = "http://www.w3.org/2000/svg";
function el(tag, attrs = {}, padre) { const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (padre) padre.appendChild(e); return e; }
const escala = (d0, d1, r0, r1) => v => r0 + (v - d0) / (d1 - d0) * (r1 - r0);
// uso
const svg = document.querySelector("#graf"), W = 900, H = 420;
const x = escala(1984, 2024, 60, W - 30), y = escala(0, 100, H - 40, 20);
[0, 25, 50, 75, 100].forEach(v => el("line", {x1: 60, x2: W - 30, y1: y(v), y2: y(v), stroke: "var(--line)"}, svg));
el("path", {d: SERIE.map((p, i) => (i ? "L" : "M") + x(p.a) + " " + y(p.v)).join(""), fill: "none",
  stroke: "var(--support)", "stroke-width": 4, class: "dibujar"}, svg);
```

Barras horizontales: `.barra > i style="--v:72%"` ya animan al entrar o al aparecer su build. Barras SVG que crecen:

```css
.is-live .crece{transform:scaleX(0);transform-origin:left center;transform-box:fill-box;animation:crece .7s cubic-bezier(.25,.8,.3,1) forwards}
@keyframes crece{to{transform:scaleX(1)}}
```

Re-animar algo asignado por JS al activar: doble `requestAnimationFrame`.

```js
el.style.width = "0"; requestAnimationFrame(() => requestAnimationFrame(() => el.style.width = v + "%"));
```

Donut sin SVG: `background:conic-gradient(var(--accent) 0 62%, var(--card2) 0)` + círculo interior.

## 2. Serie que avanza por tramos

Implementación completa y probada en `assets/laminas/serie.html` (copiarla). Claves: fijar `strokeDashoffset` al largo total y forzar reflow **antes** de asignar la transición (si no, se ve el final antes de tiempo); con `{instantaneo}` (al retroceder) saltar sin animar. Núcleo:

```js
ESCENAS["s-serie"] = (paso, s) => {
  const linea = s.querySelector(".linea");
  if (!linea._largos) {              // precalcular largo acumulado hasta cada punto
    const d = linea.getAttribute("d"), tmp = document.createElementNS("http://www.w3.org/2000/svg", "path");
    s.querySelector("svg").appendChild(tmp);
    linea._largos = SERIE.map((_, i) => { tmp.setAttribute("d", d.split("L").slice(0, i + 1).join("L")); return i ? tmp.getTotalLength() : 0; });
    tmp.remove(); linea._L = linea.getTotalLength();
    linea.style.strokeDasharray = linea._L; linea.style.transition = "stroke-dashoffset .9s ease";
  }
  linea.style.strokeDashoffset = linea._L - linea._largos[paso];
  s.querySelector(".anio").textContent = SERIE[paso].a;
  contar(s.querySelector(".valor"), SERIE[paso].v, 1, "", " ha");
  s.querySelectorAll(".punto").forEach((p, i) => p.style.opacity = i <= paso ? 1 : 0);
};
```

Contorno que se dibuja una vez (portada con mapa): `dibujar` del deck basta; para un `path` creado por JS, setear `--l` con `getTotalLength()`.

## 3. Ranking que se reordena

Filas `position:absolute`; al cambiar pesos se reordenan con `translateY` y las barras animan el ancho.

```css
.rank{position:relative;height:380px}.rank .fila{position:absolute;left:0;right:0;transition:transform .6s var(--ease)}
.rank i{display:block;height:12px;background:var(--support);transition:width .6s var(--ease)}
```
```js
function ordenar(valores) {                        // {A: 3.2, B: 4.1, ...}
  Object.entries(valores).sort((a, b) => b[1] - a[1]).forEach(([k, v], i) => {
    const f = document.getElementById("rk-" + k); f.style.transform = `translateY(${i * 74}px)`;
    f.querySelector("i").style.width = (v / 5 * 100) + "%"; contar(f.querySelector(".v"), v, 2); });
}
```

Foco en una lista por paso: contenedor `.foco` + `.activo`, el ítem actual con `.on` (CSS incluido en el deck).

## 4. Heatmap con tooltip

```js
const fondo = diag ? `rgba(46,196,182,${.15 + p * .85})` : `rgba(255,138,61,${Math.min(.12 + p * 1.6, .95)})`;
const tinta = (diag && p > .45) || (!diag && p > .3) ? "var(--bg)" : "var(--text)";
```
```html
<div id="tip" class="panel" style="padding:10px 14px;border-radius:10px;font-size:15px;pointer-events:none"></div>
```
```js
cont.addEventListener("mousemove", e => { const c = e.target.closest(".celda"), tip = document.getElementById("tip");
  if (!c) { tip.classList.remove("ver"); return; }
  tip.innerHTML = c.dataset.tip; tip.classList.add("ver"); tip.style.left = (e.clientX + 16) + "px"; tip.style.top = (e.clientY + 16) + "px"; });
```
Marcar el contenedor con `data-interactivo` para que el clic no avance la lámina.

## 5. Simulador con sliders

Interactividad real sin backend: precalcular arrays (p. ej. FP/FN para 201 umbrales) en Python, inyectarlos por `DATA`, y recalcular en `input`.

```js
function dibujarCosto() {
  const fp = +costoFP.value, fn = +costoFN.value;
  const costos = DATA.umbrales.map((_, i) => fp * DATA.fps[i] + fn * DATA.fns[i]);
  const k = costos.indexOf(Math.min(...costos));
  umbralOptimo.textContent = fmt(DATA.umbrales[k], 2);
  teorico.textContent = fmt(fp / (fp + fn), 2);          // p* = FP/(FP+FN)
  // redibujar curva SVG con el y escalas de §1
}
[costoFP, costoFN, umbral].forEach(i => i.addEventListener("input", dibujarCosto));
```
Sliders espejo en otra lámina: sincronizar `value` y llamar al mismo render. Envolver los controles en `data-interactivo`.

```css
input[type=range]{accent-color:var(--accent);width:100%}
```

## 6. Panel persistente entre láminas

Un `#mapa` (o figura) fuera de las `<section>`, dentro de `#escenario`, que entra desde la derecha y solo cambia capas/leyenda según la lámina y el paso. Las láminas que lo usan llevan clase `conmapa` y dejan margen derecho.

```css
#mapa{position:absolute;top:0;right:0;width:540px;height:900px;transform:translateX(105%);transition:transform .8s cubic-bezier(.6,.05,.25,1);z-index:3}
#mapa.ver{transform:none}
#mapa path{opacity:0;transition:opacity .75s ease;vector-effect:non-scaling-stroke}#mapa path.on{opacity:1}
.slide.conmapa{padding-right:640px}
```
```js
const ESTADO_MAPA = { "s-hoy": [{capas: ["santuario"]}, {capas: ["santuario", "perdido"]}] };
// en cada ESCENAS[id]: const st = ESTADO_MAPA[s.id]?.[paso]; mapa.classList.toggle("ver", !!st);
// document.querySelectorAll("#mapa path").forEach(p => p.classList.toggle("on", st?.capas.includes(p.dataset.capa)));
```
Si el estado se repite en varios pasos, heredar del paso anterior (`{...prev, ...actual}`) en lugar de copiarlo.

## 7. Chat guionado avanzado

El motor trae el chat de lámina (`assets/laminas/chat.html`: cada clic = un turno; partes `text`, `tool`, `confirmar` con registro, `aviso` para límites; un clic durante la animación la completa; ← la pinta sin animar). Para una **demo autónoma** donde el presentador «escribe» (composer pre-rellenado, Enter envía), opciones clicables y comparación antes/después, este es el núcleo de la implementación de referencia:

```js
const SCRIPT = [
  {role: "user", time: "12:46", text: "Paciente no tiene cobertura"},
  {role: "agent", time: "12:46", parts: [
    {type: "text", html: "Entendido. Reviso si hay solución documentada."},
    {type: "tool", icon: ICON, name: "doc_text", result: "5 chunks relevantes"},
    {type: "text", html: "<h4>Caso identificado</h4>…"}]},
  {role: "user", input: {type: "pills", question: "¿Generamos el ticket?", options: [{value: "Sí, generar ticket"}, {value: "Aún no"}]}},
];
async function runAgentTurn(turn) {
  busy = true; setSendEnabled(false); setStatus("Agente respondiendo…");
  await sleep(400); showTyping(); await sleep(900); hideTyping();
  for (let i = 0; i < turn.parts.length; i++) {
    addAgentPart(turn.parts[i]);
    const next = turn.parts[i + 1]; if (!next) break;
    if (next.type === "text" && turn.parts[i].type === "text") { await sleep(200); showTyping(); await sleep(600); hideTyping(); }
    else await sleep(next.type === "text" ? 700 : 380);
  }
  step++; busy = false; setStatus("Listo"); await sleep(250); preloadNext();
}
function preloadNext() {                 // deja listo el siguiente turno del usuario
  const t = SCRIPT[step]; if (!t) return showEndCard();      // «Fin · ↻ reiniciar»
  if (t.role === "user") t.input ? renderInput(t.input) : (composer.value = t.text, setSendEnabled(true));
}
```
Extras que funcionaron: atajos 1–9 para elegir pills; respuesta de formulario como burbuja de pares clave/valor; tarjeta «Subagentes» con estado; toggle «actual / deseado» que cambia de SCRIPT; botón reiniciar. Para que sea creíble ante comités: confirmación humana explícita, un caso límite («no tengo datos de…»), letra ≥ 17 px; el marco tipo macOS (`.chat.ventana`) solo si suma.

Variante solo CSS (sin JS) para un único intercambio: el typing aparece y colapsa, luego los hijos del informe entran en cascada:
```css
.shown .typing{animation:typseq 2.2s ease .4s both}
.shown .respuesta>*{opacity:0;animation:aparece .45s ease both}
.shown .respuesta>*:nth-child(1){animation-delay:2.6s}.shown .respuesta>*:nth-child(2){animation-delay:3.15s}
@keyframes typseq{0%{opacity:0;max-height:46px}12%{opacity:1}76%{opacity:1;max-height:46px}100%{opacity:0;max-height:0;padding:0;margin:0}}
```

## 8. Chart.js con tokens

Solo si hay muchos datos o ejes temporales complejos. Cargar versión fija desde cdnjs.

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
```
```js
Chart.defaults.font.family = tok("--f-texto"); Chart.defaults.color = tok("--muted");
const ejes = (y = {}) => ({x: {grid: {display: false}, border: {color: tok("--line")}},
  y: {grid: {color: tok("--line")}, border: {display: false}, beginAtZero: true, ...y}});
const base = {responsive: true, maintainAspectRatio: false, animation: {duration: 900},
  interaction: {mode: "index", intersect: false}, plugins: {legend: {display: false}}};
```
Crear el gráfico la primera vez que su lámina se activa (en `ESCENAS`), no al cargar: las láminas ocultas miden 0. Poner una línea-veredicto sobre cada gráfico («menor es mejor», «C supera a B en todos los cortes»).

## 9. Interactivos para páginas de lectura

**Tarjeta que gira:**
```css
.flip{perspective:1000px;height:250px}.flip .in{position:relative;height:100%;transition:transform .6s;transform-style:preserve-3d}
.flip.on .in{transform:rotateY(180deg)}.flip .cara{position:absolute;inset:0;backface-visibility:hidden}.flip .atras{transform:rotateY(180deg)}
```
**Quiz:** datos `[pregunta, opciones, idxCorrecto, explicación]`; al responder deshabilitar, marcar `.ok`/`.bad`, mostrar explicación; puntaje final con mensaje por rango.
**Acordeón:** `<details><summary>` con `summary::after{content:"+"} details[open] summary::after{content:"−"}` (accesible sin JS).
**Timeline de doble carril:** grilla `1fr 90px 1fr`, eje central `::before` con gradiente, año en círculo al centro; móvil `52px 1fr`.
**Partículas por un flujo:** `<circle r="5" fill="var(--support)"><animateMotion dur="2.2s" repeatCount="indefinite"><mpath href="#ruta1"/></animateMotion></circle>`.
**Gráfico que se transforma entre escenarios:** interpolar `cur[i] += (target[i]-cur[i])*.12` por frame hasta converger.
**Reiniciar animación de un panel:** `p.style.animation = "none"; p.offsetHeight; p.style.animation = "";`.
**Escalonado sin JS:** `.rise` + `style="--i:n"` (ya en el deck). **Ken Burns de foto:** `@keyframes focus{from{opacity:.6;transform:scale(1.06)}to{opacity:1;transform:none}}` 2.2 s.

## 10. Página larga con scroll (resumen interactivo, informe)

Cuando no se expone sino que se lee. Responsive con `clamp()`, no escenario fijo.

```css
.progreso{position:fixed;inset:0 0 auto 0;height:4px;background:var(--accent);transform:scaleX(0);transform-origin:left;z-index:20}
nav{position:sticky;top:0;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px)}
.reveal{opacity:0;transform:translateY(28px);transition:opacity .8s ease,transform .8s cubic-bezier(.2,.7,.2,1)}
.reveal.visible{opacity:1;transform:none}
h1{font-size:clamp(3rem,8vw,7rem)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){/* tokens oscuros */}}
:root[data-theme="dark"]{/* mismos tokens oscuros */}
```
```js
const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) {
  e.target.classList.add("visible");
  document.querySelectorAll("nav a").forEach(a => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id)); } }), {threshold: .12});
document.querySelectorAll(".reveal,section[id]").forEach(el => io.observe(el));
addEventListener("scroll", () => document.querySelector(".progreso").style.transform =
  `scaleX(${scrollY / (document.documentElement.scrollHeight - innerHeight)})`, {passive: true});
```
Agregar «Cómo leer esta página», tesis explícita arriba y fuente por tarjeta.

## 11. Póster / PDF vectorial
12. Ilustraciones SVG generadas con Python (diagramas técnicos propios)

Lienzo fijo (`@page{size:1200px 1600px;margin:0}`, `print-color-adjust:exact`). Si se mide texto (`getComputedTextLength`), esperar fuentes antes de dibujar: `Promise.all([600,800].map(w => document.fonts.load(`${w} 40px "Fuente"`))).then(construir)`. Azar con semilla para que el resultado sea reproducible. Subíndices con `<tspan>` (₂ cae en otra fuente).

---

## 12. Ilustraciones SVG generadas con Python

Cuando el grupo ya tiene diagramas propios generados por código (cortes, mapas, esquemas), reutilizarlos en vez de redibujarlos.

1. Un script en la carpeta de la presentación (p. ej. `svg_tema.py`) importa las funciones que devuelven el SVG como texto y lo **inserta en la lámina entre marcadores**, de modo que se pueda volver a correr sin duplicar:

```python
# en la lámina:  <div style="height:376px"><!--svg:corte--><!--/svg--></div>
nuevo = re.sub(r"(<!--svg:(\w+)-->).*?(<!--/svg-->)",
               lambda m: m.group(1) + tematizar(DIBUJOS[m.group(2)]()) + m.group(3), texto, flags=re.S)
```

2. `tematizar()` cambia los colores fijos del dibujo por tokens: tinta → `var(--text)`, texto tenue → `var(--muted)`, agua → `var(--support)`, riesgo → `var(--accent-txt)`, panel → `var(--bg2)`, halo de rótulos → `var(--bg)`. Los colores de **material** (relave, muro, suelo, techos) pueden quedar en hex: dentro de `<defs>`/`<pattern>` o marcando el dibujo con `<svg data-material>` (el linter no los cuenta).
3. `font-family="…"` → `style="font-family:var(--f-titulo);font-stretch:var(--tit-ancho)"` (sin el `font-stretch` los rótulos quedan más anchos que en el original y se cortan en el borde del `viewBox`).
4. Fragmentos de reveal.js (`class="fragment" data-fragment-index="1"`) → `data-paso="1"`. En SVG el build solo cambia la opacidad: el atributo `transform` del `<g>` se respeta.
5. Prefijo de ids distinto por dibujo (`corte("cx")`, `valle("va")`, `valle("vb")`): el mismo dibujo dos veces en el deck necesita prefijos distintos.
6. Tamaño real de un rótulo = `font-size × ancho mostrado / ancho del viewBox`. Un panel de 430 px con `viewBox` de 700 reduce 22 → 13,5 px: subir el `font-size` o ensanchar el panel hasta que el rótulo quede ≥ 18 px.
7. Correrlo antes de armar con `armar.py … --pre "python3 svg_tema.py"`.


## 13. Set base de íconos

`assets/motor/iconos.html`: 40 íconos de trazo 24×24 (servidor, base-datos, nube, pc, app, celular, enlace, red, capas, alerta, escudo, candado, usuario, equipo, documento, lista, buscar, ajustes, rayo, corazon, pulso, salud, hospital, reloj, check, equis, flecha, etiqueta, ojo, destello, brujula, codigo, paquete, grafico, chat, chip, sincronizar, campana, llave). Se incluyen una vez al inicio de `<body>` con `<!--#incluir motor/iconos.html-->` (la plantilla ya lo hace) y toman el color del texto.

```html
<svg class="i"><use href="#i-servidor"/></svg>                  <!-- 1em; .l 64 px · .xl 120 px · dentro de .ico 38 px -->
<g style="color:var(--support)"><use href="#i-servidor" x="10" y="10" width="40" height="40"/></g>   <!-- dentro de un SVG -->
```

Para verlos con su nombre: lámina `iconos` del muestrario. Si falta uno, dibujarlo con el mismo trazo (24×24, `stroke-width` 1,8, puntas redondas) como `<symbol id="i-…">` en un archivo de la presentación incluido después del set; no mezclar íconos de otras familias. `armar.py` da ERROR si un `href="#i-…"` no tiene su símbolo.

## 14. Componentes de concepto

Recetas y criterio en `concepto.md`; aquí, el inventario (todo en `deck.css`, con tokens).

| Pieza | Uso |
|---|---|
| `.slide.sangre` · `.slide.bruma` | degradado oscuro del tema (texto claro) · degradado claro. Tokens `--sangre`, `--bruma` redefinibles en `estilo.css` |
| `.fondo` (+ `.velo`, `.velo-abajo`) | capa a sangre detrás del contenido (ilustración, mapa, gráfico) |
| `.textura` + `puntos/lineas/cruces/ondas/red` (+ `desvanece`, `desvanece-izq`) | patrón SVG enmascarado; color `--tx-c`, tamaño `--tx-tam` |
| `.display` (`.xl/.m/.s`), `.contorno`, `.tenue`, `.lema` | tipografía grande como imagen; `--f-display`, `--display-peso` |
| `.letras` · `.barrido` · `.crecer` | entradas letra a letra · de izquierda a derecha · desde más chico (con o sin `data-paso`) |
| `.dibujar` + `--d`, `--dur` · `.emite` · `.flota` · `.cruza` (`--dx`) | trazos escalonados · onda que sale de un centro · vaivén · partícula que viaja |
| `.finalistas(.solido)` > `.finalista` > `.arte` + `.txt .nombre` | opciones en tarjetas altas con arte (`--n` columnas, `--c` por tarjeta) |
| `.grafo` (`.arista`, `.nodo`, `.raiz`, `.golpe`, `.onda`) | red que crece y pulso que se propaga; el script de `laminas/red.html` la construye desde `ANILLOS` o desde datos |
| `.zoom-svg` (`.marco-z`, `.foco-z`, `.lazo`, `[data-desde]`) + `.nivel` | cámara que se aleja por niveles; script en `laminas/zoom.html` (anima el `viewBox` en escala logarítmica) |

Red con datos reales: reemplazar la generación por anillos de `laminas/red.html` por `DATA.nodos` (`{anillo, x, y, icono, etiqueta}`) y `DATA.aristas` (`{a, b}`); el resto del script (saltos por BFS, cuentas, pulso) se mantiene.
