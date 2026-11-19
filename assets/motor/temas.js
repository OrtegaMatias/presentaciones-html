/* Manifiesto de temas (fuente única: lo leen el cargador, armar.py y la guía de SKILL.md).
   Uso: <html data-tema="industrial"> en la plantilla, o ?tema=papel en la URL para previsualizar. */
window.TEMAS = {
  industrial: {tipo: "claro",  fuentes: "Barlow:wght@400;500;600;700&family=Barlow+Semi+Condensed:wght@500;600;700",
               uso: "Por defecto. Ingeniería, operaciones, gerencia de planta; se lee bien proyectado con luz, en PDF y celular."},
  clinico:    {tipo: "claro",  fuentes: "Inter:wght@400;500;600;700;800",
               uso: "Salud, servicios, equipos de proyecto; estándar sobrio y amable para avances recurrentes."},
  editorial:  {tipo: "claro",  fuentes: "Inter:wght@400;500;600;700;800",
               uso: "Comités ejecutivos, directorio, documentos que se reenvían; el más formal."},
  papel:      {tipo: "claro",  fuentes: "Archivo:wdth,wght@62..125,300..900",
               uso: "Territorio, sostenibilidad, mapas y series históricas; titulares condensados con personalidad."},
  noche:      {tipo: "oscuro", fuentes: "Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Space+Grotesk:wght@500;600;700",
               uso: "Demos técnicas en sala oscura o pantalla grande; evitar con proyector y luz ambiente."},
  envio:      {tipo: "oscuro", fuentes: "Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Space+Grotesk:wght@500;600;700",
               uso: "Variante oscura cálida (kraft) para proyectos con metáfora logística; mismas condiciones que noche."}
};
(() => {
  const r = document.documentElement, q = new URLSearchParams(location.search).get("tema");
  let t = q || r.dataset.tema || "industrial";
  if (!TEMAS[t]) { console.warn(`Tema desconocido «${t}»; uso industrial. Temas: ${Object.keys(TEMAS).join(", ")}`); t = "industrial"; }
  r.dataset.tema = t;
  if (!document.querySelector("style[data-fuentes]"))      // armar.py --offline incrusta las fuentes y salta esto
    document.write(`<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=${TEMAS[t].fuentes}&display=swap">`);
})();
