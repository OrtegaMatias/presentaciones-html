# presentaciones-html

Skill para **Claude Code** que arma presentaciones HTML autocontenidas: decks para exponer en clase, defensas, comités, avances de proyecto y demos de agentes. Exporta a PDF, one-pager y PPTX.

- **6 temas probados:** `industrial`, `clinico`, `editorial`, `papel`, `noche` y `envio`. Se cambian con `?tema=` en la URL.
- **Biblioteca de 26 láminas, una por archivo:**
  - portada, postura, cifra, ecuación, serie
  - datos y partición, opciones con foco, flujo
  - resultados con intervalo, matriz de confusión, chat simulado
  - estado, hitos, riesgos, gobernanza, decisión
  - marcos en tensión, citas, objeciones, escalamiento
  - limitaciones, veredicto, plenario, cierre
- **Builds por clic** (`data-paso`, `data-solo`, `data-foco`), trazos SVG que se dibujan, contadores y escenas que avanzan con el relato.
- **Ventana del presentador** (`P`) con:
  - notas
  - reloj
  - tiempo de cada lámina contra el plan
  - quién expone y a quién pasa la palabra
  - frase puente
  - botones para ir a un anexo y volver
- **`armar.py`** revisa y genera:
  - incluye las láminas (anidables) y deja las imágenes y las fuentes incrustadas, para funcionar sin internet
  - un linter (títulos genéricos, exceso de texto, cifras sin fuente, ids duplicados, atributos repetidos, colores fuera del tema…)
  - un guion con reparto, acumulados, meta de ensayo y cobertura de la rúbrica
  - PDF, hojas de contactos, one-pager y PPTX

## Instalación

```bash
git clone https://github.com/OrtegaMatias/presentaciones-html ~/.claude/skills/presentaciones-html
```

Claude Code la carga sola. Basta pedir «hazme una presentación de…».

Requisitos para exportar:
- Python 3.10 o superior.
- Google Chrome o Chromium, para el PDF.
- Opcionales:
  - `poppler` (`pdfinfo`/`pdftoppm`) para verificar páginas, generar las hojas de contactos y el PPTX.
  - `pillow` para `--hojas`.
  - `python-pptx` para `--pptx`.

## Uso directo (sin Claude)

```bash
K=~/.claude/skills/presentaciones-html
cp $K/assets/plantilla.html fuente.html                     # y copiar a laminas/ las láminas que se usen
python3 $K/scripts/armar.py fuente.html Presentacion.html \
  --guion GUION.md --pdf Presentacion.pdf --hojas hojas.png --offline
```

Para ver todas las láminas en un tema:

```bash
python3 $K/scripts/armar.py $K/assets/muestrario.html /tmp/m.html --muestra
open "/tmp/m.html?tema=papel"
```

## Estructura

```
SKILL.md                 instrucciones para el agente (pasos, temas, biblioteca, errores conocidos)
references/narrativa.md  perfiles de audiencia, arco, exposición grupal evaluada, tiempos
references/componentes.md  componentes avanzados (sliders, heatmap, Chart.js, SVG generado con Python…)
assets/motor/            temas.js · deck.css · deck.js (no se editan por presentación)
assets/laminas/          biblioteca de láminas
assets/plantilla.html    punto de partida
assets/muestrario.html   todas las láminas juntas
scripts/armar.py         ensambla, revisa y exporta
```

Controles: `→`/`Espacio` avanza · `←` retrocede · `F` pantalla completa · `P` presentador · `N` notas · `O` vista general · `T` detalle técnico · `?` ayuda.

## Licencia

MIT. Ver [LICENSE](LICENSE).
