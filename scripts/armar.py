#!/usr/bin/env python3
"""Arma una presentación HTML autocontenida, la revisa y exporta.

Uso:
  python3 armar.py fuente.html salida.html [opciones]

  --pre "comando"      corre un comando en la carpeta de la fuente antes de armar (p. ej. "python3 graficos.py")
  --datos datos.json   inyecta en `/*DATA*/null` (escapado para <script>)
  --guion GUION.md     guion desde las notas: quién, tiempo, acumulado, rúbrica, puentes, totales por expositor
  --duracion MIN       minutos del bloque (exposición + plenario); avisa si el plan no deja 10 % de margen
  --rubrica C1,C2,…    criterios de la pauta; avisa si alguno no tiene láminas (data-rubrica)
  --pdf archivo.pdf    PDF con todas las láminas y pasos visibles (verifica páginas y fuentes)
  --hojas hojas.png    hoja de contactos (6 láminas por imagen) del PDF, para revisar todo de un vistazo
  --resumen r.pdf      PDF solo con las láminas data-resumen (one-pager para reenviar)
  --pptx archivo.pptx  PPTX de imágenes, una por lámina, con las notas del orador
  --offline            incrusta las fuentes del tema (funciona sin internet; +0,2–0,6 MB)
  --muestra            permite láminas de biblioteca sin editar (data-plantilla), para el muestrario

Rutas: <!--#incluir x--> e imágenes se buscan primero junto al archivo que las contiene, luego junto a la fuente
y por último (solo includes) en la biblioteca de la skill. Los includes pueden anidarse (máx. 5 niveles).

Atributos de <section class="slide"> que lee el guion:
  data-quien="Sebastián"  data-seg="75"  data-rubrica="C1 C3"  data-anexo (respaldo: no suma tiempo)
  En las notas: <b class="puente">…</b> marca la frase que pasa la palabra al siguiente expositor.
  En la fuente: <template id="guion-extra">…markdown…</template> se agrega al final del guion
  (preguntas probables, plan B); si no existe se deja una tabla vacía.

ERROR (no genera): tema desconocido, ids duplicados o faltantes, marcadores __ASI__, láminas de biblioteca
  sin editar, .rise junto a data-paso, data-chat sin guion, inclusiones o imágenes que no existen,
  include sin resolver, atributo repetido en una etiqueta.
aviso: sin notas, título genérico (h2 o data-titulo), exceso de palabras (rótulos SVG aparte),
  cifras sin .pie, [POR CONFIRMAR], colores hex fuera de tokens (salvo <svg data-material>), ESCENAS sin lámina, tema oscuro,
  reparto de tiempo desigual o sin margen, criterios de rúbrica sin lámina.

Nivel de diseño: <html data-diseno="gestion|concepto"> (por defecto gestion).
  gestion   sobrio: biblioteca, tablas y tarjetas; avisa tema oscuro y colores hex.
  concepto  naming, marca, pitch, visión: no avisa tema oscuro, acepta colores propios dentro de <svg> y el doble de
            rótulos SVG; en cambio avisa si la presentación queda plana (láminas solo de texto o tarjetas, sin cambio
            de ritmo a sangre/oscuro, o tres láminas seguidas de tarjetas).
"""
import argparse, base64, html as H, json, mimetypes, os, re, shutil, subprocess, sys, tempfile, urllib.request
from html.parser import HTMLParser
from pathlib import Path

K = Path(__file__).resolve().parent.parent          # carpeta de la skill
ASSETS = K / "assets"
GENERICOS = {"resultados", "los datos", "datos", "metodología", "metodologia", "introducción", "introduccion", "conclusiones",
             "conclusión", "conclusion", "análisis", "analisis", "contexto", "problema", "agenda", "objetivos", "resumen",
             "plenario", "anexo", "preguntas", "discusión", "discusion", "propuesta", "solución", "solucion"}
GENERICOS_RE = re.compile(r"(tienen? respuesta|^(las |los )?preguntas( guía)?$|^qué (vamos|veremos)|^nuestra propuesta$)", re.I)
MAX_PALABRAS = 60          # texto visible por lámina (sin notas, .tecnico ni rótulos SVG)
MAX_SVG = 70               # palabras en rótulos <text> de SVG (el doble con data-diseno="concepto")
DISENOS = ("gestion", "concepto")
FONDO_RITMO = {"sangre", "oscura", "lleno", "bruma"}         # láminas que cambian el fondo
VISUAL_CLS = {"display", "fondo", "textura", "finalistas", "grafo", "zoom-svg"}
CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium", "chromium-browser", "chrome"]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
VACIOS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr", "path", "circle",
          "rect", "line", "polyline", "polygon", "stop", "use", "ellipse", "image"}
INC_RE = re.compile(r"<!--#incluir\s+(.+?)\s*-->")
HEX_RE = re.compile(r"(?<!url\()#[0-9a-fA-F]{3,8}\b")
NO_LOCAL = re.compile(r"^(data:|https?:|//|#|var\(|about:|mailto:)")


def temas() -> dict:
    js = (ASSETS / "motor" / "temas.js").read_text(encoding="utf-8")
    return {m.group(1): {"tipo": m.group(2), "fuentes": m.group(3)}
            for m in re.finditer(r'(\w+):\s*\{tipo:\s*"(\w+)",\s*fuentes:\s*"([^"]+)"', js)}


class Laminas(HTMLParser):
    """Por lámina: atributos, título, notas, puente, texto visible, rótulos SVG, banderas para el linter."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.L, self.pila, self.act, self.repetidos = [], [], None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs); cls = (a.get("class") or "").split()
        if len(a) != len(attrs):
            nombres = [n for n, _ in attrs]
            self.repetidos.append(f"<{tag}> con {', '.join(sorted({n for n in nombres if nombres.count(n) > 1}))} repetido "
                                  f"(el navegador usa solo el primero) en {self.act['attrs'].get('id') if self.act else 'la fuente'}")
        if tag == "section" and "slide" in cls:
            self.act = {"attrs": a, "clases": cls, "h": "", "notas": "", "puente": "", "visible": [], "svg": [], "pie": False,
                        "tabla": False, "cifras": False, "hex": 0, "hex_svg": 0, "cards": 0, "solos": {}, "impacto": False,
                        "visual": bool(FONDO_RITMO & set(cls)) or "data-pasos" in a}
            self.L.append(self.act); self.pila.append(("section", "slide")); return
        if self.act is not None:
            s = self.act
            if tag == "table": s["tabla"] = True
            if "card" in cls: s["cards"] += 1
            if VISUAL_CLS & set(cls) or {"letras", "sangre"} & set(cls): s["impacto"] = True
            if tag in ("img", "canvas", "video") or VISUAL_CLS & set(cls) or \
                    (tag == "svg" and "i" not in cls and not any(t == "svg" for t, _ in self.pila)): s["visual"] = True
            if "data-contar" in a or {"cifra", "cifra-m", "ic", "matriz"} & set(cls): s["cifras"] = True
            material = "data-material" in a or any(r == "material" for _, r in self.pila) or \
                any(t in ("defs", "pattern", "marker", "lineargradient", "radialgradient") for t, _ in self.pila)
            en_svg = tag == "svg" or any(t == "svg" for t, _ in self.pila)
            for n in ("fill", "stroke", "stop-color"):
                if not material and HEX_RE.match(a.get(n) or ""): s["hex_svg" if en_svg else "hex"] += 1
            if not material and HEX_RE.search(a.get("style") or ""): s["hex_svg" if en_svg else "hex"] += 1
        if tag in VACIOS:
            return
        rol = None
        if self.act is not None:
            if tag == "aside" and "notas" in cls: rol = "notas"
            elif "puente" in cls and any(r == "notas" for _, r in self.pila): rol = "puente"
            elif "tecnico" in cls or tag in ("script", "style", "template"): rol = "oculto"
            elif tag == "svg": rol = "material" if "data-material" in a else "svg"
            elif tag in ("h1", "h2") and not self.act["h"]: rol = "titulo"
            elif tag == "footer" and "pie" in cls: rol = "pie"
            elif "data-solo" in a: rol = f"solo{len(self.act['solos'])}"; self.act["solos"][rol] = []   # se ve una capa a la vez
        self.pila.append((tag, rol))

    def handle_endtag(self, tag):
        if tag in VACIOS:
            return
        for i in range(len(self.pila) - 1, -1, -1):
            if self.pila[i][0] == tag:
                cerrado = self.pila[i]; del self.pila[i:]
                if cerrado == ("section", "slide"): self.act = None
                return

    def handle_data(self, d):
        if self.act is None or not d.strip():
            return
        roles = {r for _, r in self.pila}
        if "notas" in roles:
            self.act["notas"] += d
            if "puente" in roles: self.act["puente"] += d
        elif "oculto" in roles: return
        elif "svg" in roles or "material" in roles: self.act["svg"].append(d)
        else:
            if "titulo" in roles: self.act["h"] += d
            if "pie" in roles: self.act["pie"] = True
            solo = [r for _, r in self.pila if r and r.startswith("solo")]
            (self.act["solos"][solo[-1]] if solo else self.act["visible"]).append(d)


def fuentes_offline(familias: str) -> str:
    req = urllib.request.Request(f"https://fonts.googleapis.com/css2?family={familias}&display=swap", headers={"User-Agent": UA})
    css = urllib.request.urlopen(req, timeout=30).read().decode()
    bloques = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]+\})", css)
    salida = []
    for subset, b in bloques:
        if subset != "latin":                      # latin ya incluye á é í ó ú ñ ¿ ¡
            continue
        url = re.search(r"url\((https://[^)]+)\)", b).group(1)
        datos = base64.b64encode(urllib.request.urlopen(url, timeout=30).read()).decode()
        salida.append(b.replace(url, f"data:font/woff2;base64,{datos}"))
    if not salida:
        raise RuntimeError("Google Fonts no devolvió bloques latin")
    return "\n".join(salida)


def chrome() -> str:
    c = next((c for c in CHROME if Path(c).exists() or shutil.which(c)), None)
    if not c: sys.exit("ERROR  no encontré Chrome/Chromium para exportar")
    return c


def paginas(pdf: Path):
    if not shutil.which("pdfinfo"): return None
    m = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout)
    return int(m.group(1)) if m else None


def imprimir(html_path: Path, pdf: Path, query: str, esperadas: int, familias: str, tema: str):
    try:
        r = subprocess.run([chrome(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=10000",
                            f"--print-to-pdf={pdf}", html_path.as_uri() + query], capture_output=True, text=True, timeout=150)
    except subprocess.TimeoutExpired:
        sys.exit("ERROR  Chrome no terminó en 150 s (¿un script en bucle o datos con </script>?)")
    if r.returncode or not pdf.exists():
        sys.exit(f"ERROR  Chrome falló al imprimir:\n{r.stderr[-800:]}")
    pags = paginas(pdf)
    if pags is not None and pags != esperadas: print(f"aviso  {pdf.name}: {pags} páginas, se esperaban {esperadas} (¿lámina que desborda?)")
    if shutil.which("pdffonts"):
        f = subprocess.run(["pdffonts", str(pdf)], capture_output=True, text=True).stdout
        principal = familias.split(":")[0].replace("+", "")
        if principal not in f.replace(" ", "") and not (tema == "clinico" and "Helvetica" in f):
            print(f"aviso  {pdf.name}: la fuente {principal} no quedó en el PDF (¿sin internet? usar --offline)")
    print(f"ok  {pdf}")


def rasterizar(pdf: Path, ppp: int) -> list[Path]:
    if not shutil.which("pdftoppm"):
        sys.exit("ERROR  falta pdftoppm (poppler): brew install poppler")
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["pdftoppm", "-r", str(ppp), "-png", str(pdf), str(tmp / "p")], check=True, capture_output=True)
    return sorted(tmp.glob("p-*.png"), key=lambda f: int(f.stem.split("-")[1]))


def mmss(seg: int) -> str:
    return f"{seg // 60}:{seg % 60:02d}"


def celda(t: str) -> str:
    return t.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def guion(L, salida: Path, destino: Path, html_fuente: str, a, avisos):
    rel = os.path.relpath(salida, destino.parent)
    con_tiempo = any("data-seg" in s["attrs"] for s in L)
    filas = ["| # | Lámina | Quién | Tiempo | Acumulado | Rúbrica |", "|---|---|---|---|---|---|"]
    acum, por_quien, por_crit, cuerpo = 0, {}, {}, []
    for k, s in enumerate(L, 1):
        at = s["attrs"]; tit = at.get("data-titulo") or " ".join(s["h"].split())
        quien = at.get("data-quien", ""); anexo = "data-anexo" in at
        seg = int(at.get("data-seg") or 0)
        t_txt = "respaldo" if anexo else (f"{seg} s" if seg else "")
        a_txt = "" if anexo or not con_tiempo else mmss(acum)
        if not anexo:
            acum += seg
            if quien: por_quien[quien] = por_quien.get(quien, 0) + seg
        crit = at.get("data-rubrica", "").split()
        for c in crit: por_crit.setdefault(c, []).append((k, quien))
        filas.append(f"| {k} | [{celda(tit)}]({rel}#{at.get('id', k)}) | {celda(quien)} | {t_txt} | {a_txt} | {' '.join(crit)} |")
        notas = " ".join(s["notas"].split()) or "_(sin notas)_"
        cab = f"### {k} · {tit}" + (f" — {quien}" if quien else "") + (f" · {seg} s" if seg and not anexo else "")
        bloque = f"{cab}\n\n{notas}\n"
        if s["puente"].strip(): bloque += f"\n**Puente →** {' '.join(s['puente'].split())}\n"
        cuerpo.append(bloque)
    partes = ["# Guion\n", "\n".join(filas)]
    if con_tiempo:
        partes.append(f"\n**Total planificado:** {mmss(acum)}" + (f" de {a.duracion} min" if a.duracion else ""))
        grupo = {q: t for q, t in por_quien.items() if q.lower() not in ("todos", "plenario", "respaldo")}
        if grupo:
            partes.append("\n| Expositor | Tiempo | Meta de ensayo (90 %) |\n|---|---|---|")
            partes += [f"| {celda(q)} | {mmss(t)} | {mmss(int(t * .9))} |" for q, t in grupo.items()]
            if len(grupo) > 1:
                media = sum(grupo.values()) / len(grupo)
                for q, t in grupo.items():
                    if abs(t - media) > .15 * media:
                        avisos.append(f"reparto: {q} tiene {mmss(t)} y el promedio es {mmss(int(media))} (> 15 % de diferencia)")
        if a.duracion and acum > a.duracion * 60 * .9:
            avisos.append(f"tiempo: el plan suma {mmss(acum)} de {a.duracion} min; dejar al menos 10 % de margen")
    if por_crit or a.rubrica:
        partes.append("\n## Cobertura de la rúbrica\n\n| Criterio | Láminas | Quién |\n|---|---|---|")
        criterios = [c.strip() for c in a.rubrica.split(",")] if a.rubrica else sorted(por_crit)
        for c in criterios:
            ls = por_crit.get(c, [])
            if not ls: avisos.append(f"rúbrica: el criterio {c} no tiene ninguna lámina (data-rubrica)")
            partes.append(f"| {c} | {', '.join(str(k) for k, _ in ls) or '**sin lámina**'} | "
                          f"{', '.join(sorted({q for _, q in ls if q})) } |")
    partes.append("\n## Texto por lámina\n\n" + "\n".join(cuerpo))
    extra = re.search(r'<template id="guion-extra">([\s\S]*?)</template>', html_fuente)
    if extra:
        partes.append(H.unescape(extra.group(1)).strip() + "\n")
    else:
        partes.append("## Preguntas probables\n\n| Pregunta | Quién responde | Respuesta corta | Lámina de respaldo |\n|---|---|---|---|\n")
        if "data-chat" in html_fuente:
            partes.append("## Si falla la demo\n\nPlan B: \n")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(partes), encoding="utf-8")
    print(f"ok  guion → {destino}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuente"); ap.add_argument("salida")
    for o in ("--pre", "--datos", "--guion", "--pdf", "--hojas", "--resumen", "--pptx", "--rubrica"): ap.add_argument(o)
    ap.add_argument("--duracion", type=float)
    ap.add_argument("--offline", action="store_true"); ap.add_argument("--muestra", action="store_true")
    a = ap.parse_args()
    fuente, salida = Path(a.fuente).resolve(), Path(a.salida).resolve()
    base = fuente.parent
    if a.pre:
        r = subprocess.run(a.pre, shell=True, cwd=base)
        if r.returncode: sys.exit(f"ERROR  --pre «{a.pre}» terminó con código {r.returncode}")
    html = fuente.read_text(encoding="utf-8")
    html_fuente = html
    errores, avisos, de_biblioteca = [], [], []

    # 1. inclusiones (recursivas); rutas relativas de imágenes dentro de cada lámina se fijan a su carpeta
    def fijar_rutas(texto: str, carpeta: Path) -> str:
        def r(m):
            ruta = m.group(2)
            if NO_LOCAL.match(ruta) or Path(ruta).is_absolute(): return m.group(0)
            f = (carpeta / ruta).resolve()
            return m.group(1) + str(f) + m.group(3) if f.is_file() else m.group(0)
        return re.sub(r'(<(?:img|source|image)\b[^>]*?\b(?:src|href|xlink:href)=")([^"]+)(")', r, texto)

    def expandir(texto: str, carpeta: Path, nivel: int) -> str:
        def incluir(m):
            ruta = m.group(1).strip()
            for raiz in (carpeta, base):
                f = (raiz / ruta).resolve()
                if f.is_file(): break
            else:
                f = (ASSETS / ruta).resolve()
                if not f.is_file(): errores.append(f"no existe la lámina incluida: {ruta}"); return ""
                if "motor/" not in ruta: de_biblioteca.append(ruta)
            if nivel >= 5: errores.append(f"include anidado más de 5 niveles: {ruta}"); return ""
            return expandir(fijar_rutas(f.read_text(encoding="utf-8"), f.parent), f.parent, nivel + 1)
        return INC_RE.sub(incluir, texto)
    html = expandir(html, base, 0)

    # 2. motor (css/js locales) incrustado
    def resolver(ruta: str):
        for raiz in (base, ASSETS):
            f = (raiz / ruta).resolve()
            if f.is_file(): return f
    def css(m):
        f = resolver(m.group(1))
        return f"<style>\n{f.read_text(encoding='utf-8')}\n</style>" if f else m.group(0)
    def js(m):
        f = resolver(m.group(1))
        return f"<script>\n{f.read_text(encoding='utf-8')}\n</script>" if f else m.group(0)
    html = re.sub(r'<link\s+rel="stylesheet"\s+href="(?!https?:)([^"]+\.css)"\s*/?>', css, html)
    html = re.sub(r'<script\s+src="(?!https?:)([^"]+\.js)"\s*>\s*</script>', js, html)

    # 3. tema
    T = temas()
    tema = (re.search(r'<html[^>]*\bdata-tema="([^"]+)"', html) or [None, "industrial"])[1]
    if tema not in T: errores.append(f"tema «{tema}» no existe. Temas: {', '.join(T)}")
    diseno = (re.search(r'<html[^>]*\bdata-diseno="([^"]+)"', html) or [None, "gestion"])[1]
    if diseno not in DISENOS: errores.append(f"data-diseno «{diseno}» no existe: usar {' o '.join(DISENOS)}"); diseno = "gestion"
    concepto = diseno == "concepto"
    if tema in T and T[tema]["tipo"] == "oscuro" and not concepto:
        avisos.append(f"tema oscuro «{tema}»: solo para sala oscura o pantalla; con proyector y luz usar uno claro")

    # 4. datos
    if a.datos:
        if html.count("/*DATA*/null") != 1: errores.append("se pidió --datos pero '/*DATA*/null' no aparece exactamente una vez")
        else:
            datos = json.dumps(json.loads(Path(a.datos).read_text(encoding="utf-8")), ensure_ascii=False)
            html = html.replace("/*DATA*/null", datos.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))

    # 5. imágenes (img, source, <image> de SVG, url() en CSS)
    n_img = 0
    def img(m):
        nonlocal n_img
        ruta = m.group(2)
        if NO_LOCAL.match(ruta): return m.group(0)
        f = Path(ruta) if Path(ruta).is_absolute() else (base / ruta).resolve()
        if not f.is_file(): errores.append(f"imagen no encontrada: {ruta} (ruta relativa a la lámina o a la fuente)"); return m.group(0)
        n_img += 1
        return f"{m.group(1)}data:{mimetypes.guess_type(f.name)[0] or 'application/octet-stream'};base64,{base64.b64encode(f.read_bytes()).decode()}{m.group(3)}"
    html = re.sub(r'(<(?:img|source|image)\b[^>]*?\b(?:src|href|xlink:href)=")([^"]+)(")', img, html)
    html = re.sub(r"(url\(['\"]?)([^'\")]+)(['\"]?\))", img, html)

    # 6. revisión
    sin_com = re.sub(r"<!--[\s\S]*?-->", "", html)
    sin_code = re.sub(r"<(script|style|template)\b[\s\S]*?</\1>", "", sin_com)
    scripts = " ".join(re.findall(r"<script\b[^>]*>([\s\S]*?)</script>", sin_com))
    if INC_RE.search(html): errores.append("quedó un <!--#incluir--> sin resolver")
    sobrantes = sorted(set(re.findall(r"__[A-Z][A-Z0-9_]+__", sin_code)))
    if sobrantes: errores.append(f"marcadores sin reemplazar: {', '.join(sobrantes)}")
    ids = re.findall(r'(?<![\w-])id="([^"]+)"', sin_code)
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup: errores.append(f"ids duplicados (rompen url(#id) en SVG y los enlaces): {', '.join(dup)}")
    for tag in re.findall(r"<[^>]*\bclass=\"[^\"]*\brise\b[^\"]*\"[^>]*>", sin_code):
        if "data-paso" in tag: errores.append(f".rise y data-paso en el mismo elemento (el build se anula): {tag[:90]}…")
    for nombre in set(re.findall(r'data-chat="([^"]+)"', sin_code)):
        if not re.search(rf"\b{re.escape(nombre)}\b\s*[:=]", scripts): errores.append(f'data-chat="{nombre}" no tiene guion en CHATS')
    if not a.muestra and "data-plantilla" in sin_code:
        sin_editar = re.findall(r'<section[^>]*\bid="([^"]+)"[^>]*data-plantilla', sin_code)
        detalle = f" — tomadas de la biblioteca porque no existen junto a la fuente: {', '.join(de_biblioteca)}" if de_biblioteca else ""
        errores.append(f"lámina(s) de biblioteca sin editar (quitar data-plantilla al adaptarlas): {', '.join(sin_editar) or '?'}{detalle}")
    simbolos = set(re.findall(r'<symbol\b[^>]*\bid="(i-[\w-]+)"', sin_code))
    faltan = sorted(set(re.findall(r'href="#(i-[\w-]+)"', sin_code)) - simbolos)
    if faltan:
        errores.append(f"íconos sin definir: {', '.join(faltan)} — " + ("revisar el nombre (lista en motor/iconos.html)" if simbolos
                       else "incluir el set con <!--#incluir motor/iconos.html--> al inicio de <body>"))
    if re.search(r'font-family="(?!var)', sin_code): avisos.append('SVG con font-family fijo: usar style="font-family:var(--f-titulo)"')

    p = Laminas(); p.feed(sin_com); L = p.L
    errores += [f"atributo repetido: {r}" for r in p.repetidos]
    if not L: errores.append('no se encontraron <section class="slide">')
    for k, s in enumerate(L, 1):
        at = s["attrs"]; tag = f"lámina {k} ({at.get('id') or 'sin id'})"
        palabras = len(" ".join(s["visible"]).split()) + max([len(" ".join(v).split()) for v in s["solos"].values()] or [0])
        svg = len(" ".join(s["svg"]).split())
        h = " ".join(s["h"].split()); dt = at.get("data-titulo", "")
        if not at.get("id"): errores.append(f"{tag}: sin id (el guion, #s-id y el presentador lo necesitan)")
        if not dt: avisos.append(f"{tag}: sin data-titulo")
        if not s["notas"].strip(): avisos.append(f"{tag}: sin <aside class=\"notas\">")
        for t in {h, dt} - {""}:
            if t.lower().strip(" .:¿?") in GENERICOS or GENERICOS_RE.search(t.strip(" .:¿?")):
                avisos.append(f"{tag}: título genérico «{t}» → escribir la afirmación"); break
        tope = MAX_PALABRAS * 2 if (s["tabla"] or "compacta" in s["clases"]) else int(MAX_PALABRAS * 1.5) if "data-densa" in at else MAX_PALABRAS
        if palabras > tope: avisos.append(f"{tag}: {palabras} palabras visibles (> {tope}); mover detalle a notas o .tecnico")
        tope_svg = MAX_SVG * 2 if concepto else MAX_SVG
        if svg > tope_svg: avisos.append(f"{tag}: {svg} palabras en rótulos SVG (> {tope_svg}); el diagrama se vuelve ilegible proyectado")
        if s["cifras"] and not s["pie"] and not {"lleno", "oscura"} & set(s["clases"]):
            avisos.append(f"{tag}: muestra cifras sin .pie con su fuente")
        nhex = s["hex"] + (0 if concepto else s["hex_svg"])
        if nhex: avisos.append(f"{tag}: {nhex} color(es) hex (fill/stroke/style); usar tokens var(--…), definir la paleta propia en estilo.css "
                               f"o marcar la ilustración con <svg data-material>")
    if concepto and L:
        planas = [s["attrs"].get("id", "?") for s in L if not s["visual"] and "data-anexo" not in s["attrs"]]
        cuerpo_n = sum(1 for s in L if "data-anexo" not in s["attrs"])
        if len(planas) * 2 > cuerpo_n:
            avisos.append(f"diseño concepto: {len(planas)} de {cuerpo_n} láminas son solo texto o tarjetas ({', '.join(planas[:6])}"
                          f"{'…' if len(planas) > 6 else ''}); cada lámina de concepto necesita algo que se vea: ilustración, fondo a sangre, "
                          f"tipografía display o un gráfico que se arma (references/concepto.md)")
        if not any(s["impacto"] or "sangre" in s["clases"] for s in L):
            avisos.append("diseño concepto: ninguna lámina tiene un elemento de alto impacto (tipografía .display, lámina sangre, "
                          ".fondo a sangre, finalistas, grafo o zoom); falta el momento que la audiencia va a recordar")
        if not any(FONDO_RITMO & set(s["clases"]) for s in L):
            avisos.append("diseño concepto: ninguna lámina cambia el fondo (sangre, bruma, oscura o lleno); sin cambio de ritmo el deck se ve plano")
        racha = []
        for s in L + [None]:
            if s and s["cards"] >= 2 and not s["visual"]: racha.append(s["attrs"].get("id", "?")); continue
            if len(racha) >= 3: avisos.append(f"diseño concepto: {len(racha)} láminas seguidas de tarjetas ({', '.join(racha)}); romper con una ilustración o una lámina a sangre")
            racha = []
    escenas = set(re.findall(r'ESCENAS[^\[]*\[\s*["\']([^"\']+)["\']\s*\]', scripts))
    idsl = {s["attrs"].get("id") for s in L}
    for e in escenas - idsl: avisos.append(f'ESCENAS["{e}"] no corresponde a ninguna lámina (¿id renombrado?)')
    for s in L:
        if "data-pasos" in s["attrs"] and s["attrs"].get("id") not in escenas:
            avisos.append(f'lámina {s["attrs"].get("id")}: data-pasos sin ESCENAS["{s["attrs"].get("id")}"]')
    pend = sin_code.count("[POR CONFIRMAR]")
    if pend: avisos.append(f"{pend} dato(s) [POR CONFIRMAR] visibles")
    resumen_n = sum(1 for s in L if "data-resumen" in s["attrs"])
    if a.resumen and not resumen_n: avisos.append("--resumen: ninguna lámina tiene data-resumen (no se genera)")

    # 7. fuentes sin internet
    if a.offline and not errores:
        try:
            html = html.replace("<head>", f"<head>\n<style data-fuentes>\n{fuentes_offline(T[tema]['fuentes'])}\n</style>", 1)
        except Exception as e:
            avisos.append(f"--offline: no pude descargar las fuentes ({e}); el deck las pedirá a Google Fonts")

    if a.guion and not errores:
        guion(L, salida, Path(a.guion).resolve(), html_fuente, a, avisos)
    for e in errores: print("ERROR  " + e)
    for w in avisos: print("aviso  " + w)
    if errores: sys.exit(1)

    salida.write_text(html, encoding="utf-8")
    print(f"ok  {salida}  ·  tema {tema}  ·  diseño {diseno}  ·  {len(L)} láminas ({resumen_n} en resumen)  ·  {n_img} imágenes  ·  {salida.stat().st_size / 1024:.0f} KB")

    fam = T[tema]["fuentes"]
    pdf = Path(a.pdf).resolve() if a.pdf else None
    if (a.pptx or a.hojas) and not pdf:
        pdf = Path(tempfile.mkdtemp()) / "deck.pdf"
    if pdf:
        imprimir(salida, pdf, "?imprimir", len(L), fam, tema)
    if a.resumen and resumen_n:
        imprimir(salida, Path(a.resumen).resolve(), "?imprimir&resumen", resumen_n, fam, tema)
    if a.hojas:
        try:
            from PIL import Image
        except ImportError:
            sys.exit("ERROR  --hojas necesita Pillow: pip install pillow")
        imgs = [Image.open(f) for f in rasterizar(pdf, 40)]
        w, h = imgs[0].size; destino = Path(a.hojas).resolve()
        for i in range(0, len(imgs), 6):
            hoja = Image.new("RGB", (w * 2, h * 3), "white")
            for j, im in enumerate(imgs[i:i + 6]): hoja.paste(im, ((j % 2) * w, (j // 2) * h))
            nombre = destino if len(imgs) <= 6 else destino.with_name(f"{destino.stem}-{i // 6 + 1}{destino.suffix}")
            hoja.save(nombre); print(f"ok  hoja de contactos → {nombre}")
    if a.pptx:
        try:
            from pptx import Presentation
            from pptx.util import Inches
        except ImportError:
            sys.exit("ERROR  falta python-pptx: pip install python-pptx")
        imgs = rasterizar(pdf, 144)
        prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
        for k, f in enumerate(imgs):
            sl = prs.slides.add_slide(prs.slide_layouts[6])
            sl.shapes.add_picture(str(f), 0, 0, prs.slide_width, prs.slide_height)
            if k < len(L): sl.notes_slide.notes_text_frame.text = " ".join(L[k]["notas"].split())
        prs.save(a.pptx)
        print(f"ok  pptx → {a.pptx} ({len(imgs)} láminas como imagen, con notas; no editable)")


if __name__ == "__main__":
    main()
