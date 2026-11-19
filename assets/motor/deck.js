/* =====================================================================
   MOTOR DE PRESENTACIONES · comportamiento. No editar por presentación.
   La presentación define (antes de cargar este archivo, o en un <script> previo):
     DATA     cifras inyectadas por armar.py --datos (opcional)
     ESCENAS  {"s-id": (paso, slide, {instantaneo}) => {...}} hooks por lámina
     CHATS    {"NOMBRE": [turnos]} guiones para láminas con data-chat
   ===================================================================== */
window.DATA = window.DATA ?? null;
window.ESCENAS = window.ESCENAS || {};
window.CHATS = window.CHATS || {};

(() => {
const $ = (q, c = document) => c.querySelector(q), $$ = (q, c = document) => [...c.querySelectorAll(q)];
const mq = matchMedia("(prefers-reduced-motion: reduce)");
let reducir = mq.matches; mq.addEventListener?.("change", e => reducir = e.matches);
const params = new URLSearchParams(location.search);
const W = 1600, H = 900, ORIGEN = location.origin === "null" ? "*" : location.origin;
const imprimiendo = () => document.body.classList.contains("imprimir");

/* ---------- Cromo: lo inyecta el motor (la presentación solo trae #escenario) ---------- */
if (!$("#cromo")) document.body.insertAdjacentHTML("beforeend", `
<div id="ruta" aria-hidden="true"></div>
<div id="cromo">
  <button id="btnAnt" aria-label="Anterior">‹</button><button id="btnSig" aria-label="Siguiente">›</button>
  <span id="titulo-actual"></span><div class="riel"><i id="riel"></i></div>
  <button id="btnTec">Detalle técnico (T)</button><span id="contador"></span><button id="btnAyuda" aria-label="Ayuda de teclado">?</button>
</div>
<div id="anuncio" class="sr" aria-live="polite"></div>
<div id="notas-panel" class="panel" aria-label="Notas del orador"></div>
<div id="tecnico-panel" class="panel" aria-label="Detalle técnico"></div>
<div id="vista-panel" class="panel" aria-label="Vista general"></div>
<div id="ayuda-panel" class="panel" aria-label="Ayuda">
  <div><kbd>→</kbd><kbd>Espacio</kbd> avanzar · <kbd>←</kbd> retroceder · <kbd>Inicio</kbd><kbd>Fin</kbd></div>
  <div><kbd>F</kbd> pantalla completa · <kbd>P</kbd> ventana del presentador · <kbd>N</kbd> notas (ensayo)</div>
  <div><kbd>O</kbd> vista general · <kbd>T</kbd> detalle técnico · <kbd>Esc</kbd> cerrar</div>
  <div>URL: <kbd>#5</kbd> lámina · <kbd>#5.3</kbd> paso · <kbd>#s-id</kbd> por id · <kbd>?tema=papel</kbd> · <kbd>?resumen</kbd> · <kbd>?imprimir</kbd></div>
</div>
<div id="vp"><div><div class="reloj" id="vp-reloj">00:00</div><div class="plan" id="vp-plan"></div><div class="meta" id="vp-meta"></div>
  <div class="quien" id="vp-quien"></div><div class="tit" id="vp-tit"></div><div class="nt" id="vp-nt"></div></div>
  <div><div class="meta">SIGUIENTE</div><div class="sig"><div class="quien" id="vp-sig-quien"></div><div class="tit" id="vp-sig"></div></div>
  <div class="puente" id="vp-puente" hidden></div><div class="saltos" id="vp-saltos"></div>
  <p class="meta" style="margin-top:18px">← → controlan la presentación · R reinicia el reloj · botones: ir a un anexo y volver</p></div></div>`);

/* ?resumen: solo las láminas con data-resumen (one-pager para reenviar) */
if (params.has("resumen")) $$(".slide").forEach(s => { if (!s.hasAttribute("data-resumen")) s.classList.add("fuera"); });
const S = $$(".slide").filter(s => !s.classList.contains("fuera")), N = S.length;
let di = 0, pi = 0, presentador = null, t0 = Date.now();

const esc = x => String(x ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const fmt = (v, d = 0) => v.toLocaleString("es-CL", {minimumFractionDigits: d, maximumFractionDigits: d});
window.fmt = fmt;

/* ---------- Contador animado: cancela el anterior y parte desde lo que se ve ---------- */
function contar(e, hasta, dec, pre, suf, retraso = 0) {
  dec = dec ?? +(e.dataset.dec || 0); pre = pre ?? (e.dataset.pre || ""); suf = suf ?? (e.dataset.suf || "");
  cancelAnimationFrame(e._raf); clearTimeout(e._to);
  const final = pre + fmt(hasta, dec) + suf;
  e.setAttribute("aria-label", final);
  const desde = e._cur ?? 0;
  if (reducir || imprimiendo() || desde === hasta) { e._cur = hasta; e.textContent = final; return; }
  e._to = setTimeout(() => {
    const ti = performance.now(), dur = 1000;
    const paso = t => { const x = Math.min(1, Math.max(0, (t - ti) / dur)), v = desde + (hasta - desde) * (1 - Math.pow(1 - x, 3));
      e._cur = v; e.textContent = pre + fmt(v, dec) + suf; if (x < 1) e._raf = requestAnimationFrame(paso); };
    e._raf = requestAnimationFrame(paso);
  }, retraso);
}
window.contar = contar;

/* ---------- Pasos de una lámina ---------- */
function pasosDe(s) {
  let m = 0;
  $$("[data-paso],[data-solo],[data-foco]", s).forEach(e => m = Math.max(m, +(e.dataset.paso || e.dataset.solo || e.dataset.foco)));
  if (s.dataset.pasos) m = Math.max(m, +s.dataset.pasos);
  if (s.dataset.chat && CHATS[s.dataset.chat]) m = Math.max(m, CHATS[s.dataset.chat].length);
  return m;
}

function ajustar() {
  if (imprimiendo()) return;
  const k = Math.min(innerWidth / W, innerHeight / H);
  $("#escenario").style.transform = `translate(${(innerWidth - W * k) / 2}px,${(innerHeight - H * k) / 2}px) scale(${k})`;
}

function pintarPasos(s, p, instantaneo = false) {
  $$("[data-paso]", s).forEach(e => e.classList.toggle("ver", p >= +e.dataset.paso));
  if (imprimiendo()) {          // PDF: en cada grupo de data-solo queda visible el de número mayor
    const grupos = new Map();
    $$("[data-solo]", s).forEach(e => { const g = e.parentElement; if (!grupos.has(g) || +e.dataset.solo > +grupos.get(g).dataset.solo) grupos.set(g, e); });
    $$("[data-solo]", s).forEach(e => e.classList.toggle("ver", grupos.get(e.parentElement) === e));
  } else $$("[data-solo]", s).forEach(e => e.classList.toggle("ver", p === +e.dataset.solo));
  $$("[data-foco]", s).forEach(e => e.classList.toggle("activo", p >= +e.dataset.foco));
  $$("[data-contar]", s).forEach(e => {
    const oculto = e.closest("[data-paso]:not(.ver),[data-solo]:not(.ver)");
    if (!oculto && !e._hecho) {
      e._hecho = true;
      if (instantaneo) e._cur = +e.dataset.contar;          // al retroceder no vuelve a contar desde 0
      const r = e.closest(".rise"), i = r ? +(getComputedStyle(r).getPropertyValue("--i") || 0) : 0;
      contar(e, +e.dataset.contar, undefined, undefined, undefined, instantaneo ? 0 : (r ? i * 110 + 220 : 0));
    }
  });
  $$("[data-paso],[data-solo]", s).forEach(e => e.setAttribute("aria-hidden", e.classList.contains("ver") ? "false" : "true"));
  if (s.dataset.chat) chatIr(s, p, instantaneo);
  if (ESCENAS[s.id]) ESCENAS[s.id](p, s, {instantaneo});
}

function mostrar(n, p = 0, instantaneo = false) {
  n = Math.max(0, Math.min(N - 1, n));
  const cambio = n !== di || !S[n].classList.contains("activa");
  if (cambio) {
    S.forEach((s, k) => { s.classList.toggle("activa", k === n); s.classList.toggle("previa", k < n); s.classList.remove("is-live");
      s.setAttribute("aria-hidden", k === n ? "false" : "true"); });
    $$("[data-contar]", S[n]).forEach(e => { e._hecho = false; e._cur = 0; cancelAnimationFrame(e._raf); clearTimeout(e._to); });
    void S[n].offsetWidth; S[n].classList.add("is-live");
    if (S[n].dataset.chat) chatReset(S[n]);
  }
  di = n; pi = Math.max(0, Math.min(pasosDe(S[n]), p));
  pintarPasos(S[di], pi, instantaneo);
  const tot = pasosDe(S[di]), tit = S[di].dataset.titulo || "";
  $("#contador").textContent = `${di + 1} / ${N}` + (tot ? ` · ${pi}/${tot}` : "");
  if (cambio) $("#anuncio").textContent = `Diapositiva ${di + 1} de ${N}: ${tit}`;
  $("#riel").style.width = ((di + 1) / N * 100) + "%";
  $("#titulo-actual").textContent = tit;
  const nt = $(".notas", S[di]); $("#notas-panel").innerHTML = nt ? nt.innerHTML : "<i>Sin notas</i>";
  const tec = $(".tecnico", S[di]); $("#btnTec").classList.toggle("ver", !!tec);
  $("#tecnico-panel").innerHTML = tec ? tec.innerHTML : ""; if (!tec) $("#tecnico-panel").classList.remove("ver");
  const etapa = S[di].dataset.ruta;
  $$("#ruta span").forEach(sp => { sp.classList.toggle("aqui", sp.textContent === etapa);
    sp.classList.toggle("hecho", rutas.indexOf(sp.textContent) < rutas.indexOf(etapa)); });
  history.replaceState(null, "", location.pathname + location.search + "#" + (di + 1) + (pi ? "." + pi : ""));
  avisarPresentador();
}
function sig() {
  const s = S[di];
  if (s._chatBusy) return chatCompletar(s);            // un clic durante la animación la completa, no la encola
  pi < pasosDe(s) ? mostrar(di, pi + 1) : mostrar(di + 1, 0);
}
function ant() { pi > 0 ? mostrar(di, pi - 1, true) : (di > 0 && mostrar(di - 1, pasosDe(S[di - 1]), true)); }
function irHash() {
  const h = decodeURIComponent(location.hash.slice(1));
  if (!h) return mostrar(0, 0);
  const porId = h.match(/^(.+?)(?:\.(\d+))?$/), k = S.findIndex(s => s.id === porId[1] || s.id === h);
  if (k >= 0) return mostrar(k, S[k].id === h ? 0 : (porId[2] ? +porId[2] : 0), true);   // #s-id o #s-id.2
  const m = h.match(/^(\d+)(?:\.(\d+))?$/);
  if (m) return mostrar(+m[1] - 1, m[2] ? +m[2] : 0, true);          // #5 o #5.3
  if (!S[di]?.classList.contains("activa")) mostrar(0, 0);            // otra ancla: no mover
}

/* ---------- Chat guionado: el paso p muestra p turnos ----------
   Partes de un turno del agente: {type:"text",html} {type:"tool",name,result,icon?}
   {type:"confirmar",titulo,html,registro}  (aprobación humana explícita)  {type:"aviso",html} (límite / no sé) */
const sleep = ms => new Promise(r => setTimeout(r, reducir ? 0 : ms));
const ICONO_TOOL = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/></svg>';
function estadoChat(s, txt) { const e = $(".chat-top .estado", s); if (e) e.textContent = txt; }
function chatReset(s) { $(".chat-msgs", s).innerHTML = ""; s._chatN = 0; s._chatBusy = false; s._chatGen = (s._chatGen || 0) + 1; estadoChat(s, "en línea"); }
function burbuja(cont, cls, html) { const r = document.createElement("div"); r.className = "msg " + cls; r.innerHTML = html; cont.appendChild(r);
  cont.scrollTop = cont.scrollHeight; return r; }
function parteHTML(pt) {
  if (pt.type === "tool") return `<span class="tool">${pt.icon || ICONO_TOOL}${pt.name} <b>→ ${pt.result}</b></span>`;
  if (pt.type === "confirmar") return `<div class="confirmar"><b>${pt.titulo || "Requiere tu confirmación"}</b>${pt.html}${pt.registro ? `<span class="reg">${pt.registro}</span>` : ""}</div>`;
  if (pt.type === "aviso") return `<div class="aviso">${pt.html}</div>`;
  return `<div class="b">${pt.html}</div>`;
}
function chatPintarHasta(s, n) {
  const guion = CHATS[s.dataset.chat], cont = $(".chat-msgs", s);
  chatReset(s);
  guion.slice(0, n).forEach(t => t.role === "user" ? burbuja(cont, "user", `<div class="b">${t.text}</div>`) : t.parts.forEach(pt => burbuja(cont, "agent", parteHTML(pt))));
  s._chatN = n;
}
function chatCompletar(s) { chatPintarHasta(s, s._chatObj ?? pi); }
async function chatIr(s, p, instantaneo) {
  const guion = CHATS[s.dataset.chat];
  if (!guion) return;
  if (imprimiendo()) return chatPintarHasta(s, guion.length);
  if (instantaneo || p < s._chatN) return chatPintarHasta(s, p);
  s._chatObj = p; if (s._chatBusy) return;
  s._chatBusy = true; const gen = s._chatGen, cont = $(".chat-msgs", s);
  while (s._chatN < s._chatObj) {
    const t = guion[s._chatN++];
    if (t.role === "user") { burbuja(cont, "user", `<div class="b">${t.text}</div>`); await sleep(250); if (gen !== s._chatGen) return; continue; }
    estadoChat(s, "escribiendo…");
    for (const pt of t.parts) {
      const ty = burbuja(cont, "agent", '<div class="typing" aria-hidden="true"><span></span><span></span><span></span></div>');
      await sleep(pt.type === "tool" ? 650 : 900); ty.remove();
      if (gen !== s._chatGen) return;                   // se salió, retrocedió o se completó
      burbuja(cont, "agent", parteHTML(pt)); await sleep(250);
      if (gen !== s._chatGen) return;
    }
    estadoChat(s, "en línea");
  }
  s._chatBusy = false;
}

/* ---------- Preparación de láminas ---------- */
const rutas = [...new Set(S.map(s => s.dataset.ruta).filter(Boolean))];
$("#ruta").innerHTML = rutas.map(r => `<span>${esc(r)}</span>`).join("");
S.forEach((s, k) => {
  if (!s.id) { let n = k + 1; while (document.getElementById("s-" + n)) n += 1000; s.id = "s-" + n; }
  const q = s.dataset.quien;
  if (q && !/^(todos|respaldo|plenario)$/i.test(q) && !s.classList.contains("lleno")) s.insertAdjacentHTML("afterbegin", `<div class="quien" aria-label="Expone">${esc(q)}</div>`);
  s.setAttribute("role", "group"); s.setAttribute("aria-roledescription", "diapositiva");
  s.setAttribute("aria-label", `${k + 1} de ${N}: ${s.dataset.titulo || ""}`);
  let pie = $(".pie", s);
  if (!pie && !s.classList.contains("lleno")) { pie = document.createElement("footer"); pie.className = "pie"; s.appendChild(pie); }
  if (pie) pie.insertAdjacentHTML("afterbegin", `<span class="num">${String(k + 1).padStart(2, "0")}</span>`);
  const msgs = $(".chat-msgs", s); if (msgs) { msgs.setAttribute("role", "log"); msgs.setAttribute("aria-live", "polite"); }
  if (s.dataset.chat && !CHATS[s.dataset.chat]) console.warn(`Lámina ${s.id}: data-chat="${s.dataset.chat}" no existe en CHATS`);
});
$$(".dibujar").forEach(p => { try { p.style.setProperty("--l", Math.ceil(p.getTotalLength()) + 1); } catch (e) {} });

/* ---------- Vista general (O) ---------- */
$("#vista-panel").innerHTML = S.map((s, k) => `<button data-k="${k}"><small>${String(k + 1).padStart(2, "0")} · ${esc(s.dataset.ruta)}${s.dataset.quien ? " · " + esc(s.dataset.quien) : ""}</small>${esc(s.dataset.titulo || s.id)}</button>`).join("");
$("#vista-panel").addEventListener("click", e => { const b = e.target.closest("button"); if (b) { cerrarPaneles(); mostrar(+b.dataset.k); } });

/* ---------- Paneles ---------- */
let focoPrevio = null;
function abrir(id) {
  const p = $(id), abre = !p.classList.contains("ver");
  cerrarPaneles();
  if (!abre) return;
  focoPrevio = document.activeElement; p.classList.add("ver");
  if (id === "#vista-panel") { const b = $$("#vista-panel button")[di]; $$("#vista-panel button").forEach((x, k) => x.classList.toggle("aqui", k === di)); b?.focus(); }
}
function cerrarPaneles() {
  const habia = $$(".panel.ver").length; $$(".panel").forEach(p => p.classList.remove("ver"));
  if (habia && focoPrevio && document.contains(focoPrevio)) focoPrevio.focus?.(); focoPrevio = null;
}
$$(".panel").forEach(p => { p.setAttribute("role", "dialog"); });
$("#btnTec").onclick = e => { e.stopPropagation(); abrir("#tecnico-panel"); };
$("#btnAyuda").onclick = e => { e.stopPropagation(); abrir("#ayuda-panel"); };
$("#btnSig").onclick = e => { e.stopPropagation(); sig(); };
$("#btnAnt").onclick = e => { e.stopPropagation(); ant(); };

/* ---------- Ventana del presentador (P) ---------- */
/* Plan de tiempos: data-seg por lámina (las data-anexo no suman). */
const segDe = s => s.hasAttribute("data-anexo") ? 0 : +(s.dataset.seg || 0);
const PLAN0 = []; S.reduce((a, s, k) => (PLAN0[k] = a, a + segDe(s)), 0);
const PLAN_TOTAL = S.reduce((a, s) => a + segDe(s), 0);
function avisarPresentador() {
  if (!presentador || presentador.closed) return;
  const s = S[di], nt = $(".notas", s), tot = pasosDe(s), prox = S[di + 1];
  const pasoSig = pi < tot ? $$(`[data-paso="${pi + 1}"],[data-solo="${pi + 1}"]`, s).map(e => e.textContent.trim().replace(/\s+/g, " ")).join(" · ").slice(0, 120) : "";
  presentador.postMessage({tipo: "estado", k: di, tit: s.dataset.titulo || s.id, meta: `Lámina ${di + 1} / ${N} · paso ${pi} de ${tot}`,
    quien: s.dataset.quien || "", seg: segDe(s), plan0: PLAN0[di], planTotal: PLAN_TOTAL, anexo: s.hasAttribute("data-anexo"),
    nt: nt ? nt.innerHTML : "", puente: $(".notas .puente", s)?.textContent.trim() || "",
    sig: pi < tot ? `Paso ${pi + 1}: ${pasoSig || "(siguiente paso en esta lámina)"}` : (prox?.dataset.titulo || "— fin —"),
    sigQuien: pi >= tot && prox?.dataset.quien && prox.dataset.quien !== s.dataset.quien ? `Pasa a ${prox.dataset.quien}` : "",
    anexos: S.map((x, j) => x.hasAttribute("data-anexo") ? {j, t: x.dataset.titulo || x.id} : null).filter(Boolean)}, ORIGEN);
}
let vpK = -1, vpT = Date.now(), vpVolver = null, vpUltimo = null;
const mmss = s => `${s < 0 ? "-" : ""}${String(Math.abs(s) / 60 | 0).padStart(2, "0")}:${String(Math.abs(s) % 60).padStart(2, "0")}`;
function pintarPlan(d) {
  if (!d) return;
  const total = Math.floor((Date.now() - t0) / 1000), aqui = Math.floor((Date.now() - vpT) / 1000), partes = [];
  if (d.seg) partes.push(`<span class="${aqui > d.seg ? "tarde" : "ok"}">lámina ${mmss(aqui)} / ${mmss(d.seg)}</span>`);
  if (d.planTotal) { const dif = total - (d.plan0 + Math.min(aqui, d.seg || 0));
    partes.push(`<span class="${dif > 15 ? "tarde" : "ok"}">${dif >= 0 ? "+" : "−"}${mmss(Math.abs(dif))} vs plan</span>`, `<span>quedan ${mmss(d.planTotal - total)}</span>`); }
  $("#vp-plan").innerHTML = partes.join("");
}
addEventListener("message", e => {
  if (ORIGEN !== "*" && e.origin !== ORIGEN) return;
  const d = e.data;
  if (document.body.classList.contains("presentador") && d?.tipo === "estado") {
    if (d.k !== vpK) { vpK = d.k; vpT = Date.now(); }
    vpUltimo = d;
    $("#vp-tit").textContent = d.tit; $("#vp-meta").textContent = d.meta; $("#vp-nt").innerHTML = d.nt; $("#vp-sig").textContent = d.sig;
    $("#vp-quien").textContent = d.quien; $("#vp-sig-quien").textContent = d.sigQuien;
    $("#vp-puente").hidden = !d.puente; $("#vp-puente").textContent = d.puente ? "Puente → " + d.puente : "";
    $("#vp-saltos").innerHTML = d.anexos.map(a => `<button data-j="${a.j}">${esc(a.t)}</button>`).join("") +
      (vpVolver !== null ? `<button data-j="${vpVolver}" data-volver>↩ Volver a la lámina ${vpVolver + 1}</button>` : "");
    pintarPlan(d);
  } else if (d?.rol === "presentador" && !document.body.classList.contains("presentador")) {
    presentador = e.source;                               // se re-vincula si la principal se recargó
    if (d.tipo === "sig") sig(); else if (d.tipo === "ant") ant(); else if (d.tipo === "hola") avisarPresentador();
    else if (d.tipo === "ir") mostrar(+d.j, 0);
  }
});

/* ---------- Teclado, clic, swipe ---------- */
const esInteractivo = el => el.closest?.("a,button,input,select,textarea,label,summary,[data-interactivo],.panel,#cromo,#ruta");
addEventListener("keydown", ev => {
  const k = ev.key, t = ev.target;
  if (t.matches?.("input,textarea,select")) return;
  if (document.body.classList.contains("presentador")) {
    if (["ArrowRight", " ", "PageDown", "Enter"].includes(k)) window.opener?.postMessage({tipo: "sig", rol: "presentador"}, ORIGEN);
    if (["ArrowLeft", "PageUp", "Backspace"].includes(k)) window.opener?.postMessage({tipo: "ant", rol: "presentador"}, ORIGEN);
    if (k.toLowerCase() === "r") t0 = Date.now();
    return;
  }
  if ($("#vista-panel").classList.contains("ver")) {      // en la vista general las flechas mueven el foco
    const bs = $$("#vista-panel button"), i = bs.indexOf(document.activeElement);
    if (k === "ArrowRight" || k === "ArrowDown") { ev.preventDefault(); bs[Math.min(bs.length - 1, i + 1)]?.focus(); return; }
    if (k === "ArrowLeft" || k === "ArrowUp") { ev.preventDefault(); bs[Math.max(0, i - 1)]?.focus(); return; }
  }
  if ((k === "Enter" || k === " ") && t.closest?.("button,a,.panel")) return;   // activar el control, no avanzar
  if (["ArrowRight", "ArrowDown", "PageDown", " ", "Enter"].includes(k)) { ev.preventDefault(); sig(); }
  else if (["ArrowLeft", "ArrowUp", "PageUp", "Backspace"].includes(k)) { ev.preventDefault(); ant(); }
  else if (k === "Home") mostrar(0); else if (k === "End") mostrar(N - 1, pasosDe(S[N - 1]), true);
  else if (k === "Escape") cerrarPaneles();
  else if (!ev.metaKey && !ev.ctrlKey) switch (k.toLowerCase()) {
    case "f": document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(); break;
    case "n": abrir("#notas-panel"); break;
    case "t": if ($(".tecnico", S[di])) abrir("#tecnico-panel"); break;
    case "o": abrir("#vista-panel"); break;
    case "h": case "?": abrir("#ayuda-panel"); break;
    case "p": presentador = window.open(location.href.split("#")[0] + "#presentador", "presentador", "width=1000,height=720"); setTimeout(avisarPresentador, 700); break;
  }
});
addEventListener("click", ev => { if (esInteractivo(ev.target) || document.body.classList.contains("presentador")) return;
  ev.clientX < innerWidth * .25 ? ant() : sig(); });
let tx = 0, tInteractivo = false;
addEventListener("touchstart", e => { tx = e.changedTouches[0].clientX; tInteractivo = !!esInteractivo(e.target); }, {passive: true});
addEventListener("touchend", e => { if (tInteractivo) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 50) dx < 0 ? sig() : ant(); }, {passive: true});
addEventListener("resize", ajustar);

/* ---------- Arranque ---------- */
if (location.hash === "#presentador") {
  document.body.classList.add("presentador");
  window.opener?.postMessage({tipo: "hola", rol: "presentador"}, ORIGEN);
  $("#vp-saltos").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return;
    vpVolver = b.hasAttribute("data-volver") ? null : vpK;
    window.opener?.postMessage({tipo: "ir", j: +b.dataset.j, rol: "presentador"}, ORIGEN); });
  setInterval(() => { $("#vp-reloj").textContent = mmss(Math.floor((Date.now() - t0) / 1000)); pintarPlan(vpUltimo); }, 1000);
  return;
}
const prepararPDF = () => { document.body.classList.add("imprimir"); S.forEach(s => { s.classList.add("is-live", "activa"); pintarPasos(s, pasosDe(s), true); });
  S[N - 1].classList.add("ultima"); };                    // sin salto de página tras la última: evita una hoja en blanco
if (params.has("imprimir")) { prepararPDF(); return; }
addEventListener("beforeprint", prepararPDF);
addEventListener("afterprint", () => { document.body.classList.remove("imprimir"); S.forEach(s => s.classList.remove("activa", "is-live")); ajustar(); irHash(); });
ajustar(); irHash();
addEventListener("hashchange", () => { if (location.hash !== "#" + (di + 1) + (pi ? "." + pi : "")) irHash(); });
})();
