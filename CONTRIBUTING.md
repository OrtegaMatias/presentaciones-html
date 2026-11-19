# Cómo contribuir

Gracias por mejorar la skill. La rama `main` está protegida: **todo cambio entra por pull request (PR)**, también los del dueño del repositorio. No se aceptan push directos ni force push a `main`.

## 1. Preparar tu copia

**Si no tienes permiso de escritura** (lo normal): haz un fork en GitHub y clónalo donde Claude Code lo encuentre.

```bash
gh repo fork OrtegaMatias/presentaciones-html --clone=false
git clone https://github.com/<tu-usuario>/presentaciones-html ~/.claude/skills/presentaciones-html
cd ~/.claude/skills/presentaciones-html
git remote add upstream https://github.com/OrtegaMatias/presentaciones-html
```

**Si tienes permiso de escritura:** basta con clonar el repositorio original.

Antes de empezar, actualiza `main`:

```bash
git switch main && git pull upstream main   # o «git pull» si clonaste el original
```

## 2. Trabajar en una rama

Una rama por cambio, con un nombre que diga qué hace:

| Prefijo | Para |
|---|---|
| `lamina/…` | lámina nueva o cambio en una de la biblioteca |
| `motor/…` | `deck.css`, `deck.js`, `temas.js` |
| `armar/…` | `scripts/armar.py` (linter, guion, exportación) |
| `docs/…` | `SKILL.md`, `references/`, README |
| `fix/…` | corrección de un error |

```bash
git switch -c lamina/linea-de-tiempo
```

## 3. Antes de abrir el PR

Arma el muestrario. No debe haber ningún `ERROR`, y cada `aviso` nuevo tiene que estar justificado en el PR:

```bash
K=~/.claude/skills/presentaciones-html
python3 $K/scripts/armar.py $K/assets/muestrario.html /tmp/m.html --muestra --pdf /tmp/m.pdf --hojas /tmp/hoja.png
```

Después revisa lo que corresponda a tu cambio:

- **Lámina nueva:**
  - Va en `assets/laminas/` con `data-plantilla` y un id `s-…` único.
  - Los `<marker>`/`<defs>` llevan el id de la lámina como prefijo.
  - Lleva un comentario inicial que diga para qué sirve y qué editar.
  - Se incluye en `assets/muestrario.html`.
  - Se nombra en la sección «Biblioteca» de `SKILL.md`, y en `references/narrativa.md` si corresponde a un perfil.
- **Motor (CSS/JS):**
  - Solo tokens (`var(--…)`), nunca colores hex sueltos.
  - Mínimo 16 px de letra en el escenario de 1600×900.
  - Se ve bien en los **6 temas**: abre `/tmp/m.html?tema=industrial`, `clinico`, `editorial`, `papel`, `noche` y `envio`.
  - El PDF sigue saliendo con una página por lámina.
  - Si tocas `deck.js`, pruébalo en el navegador: navegar con → y ←, links `#5.3` y `#s-id`, teclas `P`, `N`, `O` y `T`, y la vista en celular.
  - Revisa la sintaxis con `node --check assets/motor/deck.js`.
- **`armar.py`:**
  - Si agregas una regla al linter, prueba que detecte el caso malo y que **no** dé falsos positivos en el muestrario.
  - Anótala en el docstring y en la sección «Errores ya cometidos» de `SKILL.md`.
- **Documentación:**
  - `SKILL.md` la lee un agente: instrucciones concretas, sin ambigüedad y cortas.
  - El detalle va en `references/`.
- **Datos personales:** no subir rutas locales, nombres de personas, correos, nombres de cursos, empresas ni datos de clientes. Los ejemplos van con cifras marcadas como ilustrativas.

## 4. Commit y PR

Mensajes de commit en español y en imperativo («Agregar lámina de línea de tiempo», «Corregir contraste del chip en papel»).

```bash
git add -A
git commit -m "Agregar lámina de línea de tiempo"
git push -u origin lamina/linea-de-tiempo
gh pr create --fill
```

En la descripción del PR incluye:

1. **Qué cambia y por qué** (el problema que resuelve).
2. **Cómo lo probaste**: comandos, temas revisados y navegador.
3. **Capturas** si cambia algo visible: una hoja de contactos (`--hojas`) o un antes/después.
4. Avisos nuevos del linter y por qué se aceptan.

Las conversaciones de revisión deben quedar resueltas antes del merge. Si `main` avanzó mientras tanto, actualiza tu rama:

```bash
git fetch upstream && git rebase upstream/main && git push --force-with-lease
```

El force push solo está permitido en tu rama, nunca en `main`.

## 5. Merge

Se usa *squash merge*: el PR queda como un solo commit en `main`. Después del merge puedes borrar tu rama:

```bash
git switch main && git pull upstream main && git branch -d lamina/linea-de-tiempo
```

## Ideas y errores

¿No vas a programarlo? Abre un *issue* con lo que intentabas hacer, qué pasó y, si puedes, la salida de `armar.py` o una captura.
