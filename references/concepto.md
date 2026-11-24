# Presentaciones de concepto (naming, marca, pitch, visión)

Leer cuando la fuente lleva `<html data-diseno="concepto">`. En gestión la lámina informa y la tarjeta ordena; en concepto la lámina tiene que **hacerse ver y recordar**, y la tarjeta casi nunca sirve.

| | Gestión | Concepto |
|---|---|---|
| Objetivo | informar, decidir | que la idea se entienda de un vistazo y se recuerde |
| Protagonista de la lámina | tabla, tarjetas, cifra con fuente | una imagen: ilustración, tipografía display, gráfico que se arma, número enorme |
| Palabras visibles | 40–60 | 15–40; el resto en notas |
| Fondo | el del tema | alterna: claro, `bruma`, `sangre` |
| Movimiento | builds para narrar | builds + un momento memorable (revelación, pulso, zoom) |
| Biblioteca | punto de partida | solo las láminas de concepto; lo demás se diseña |

## 1. Dirección visual (antes del esqueleto)

Si está disponible, cargar la skill `frontend-design` y aplicarla al deck. Escribir en cinco líneas, junto a la lista de láminas:

1. **Paleta:** el tema + 1–2 tokens propios en `estilo.css` si la marca lo pide (`:root{--accent:…}` redefine todo el deck).
2. **Tipografía display:** la del tema (`--f-display`) o una propia cargada en `<head>` y declarada en `estilo.css`.
3. **El momento memorable:** una sola cosa que la audiencia va a contar después (el nombre que se revela, la falla que recorre la red, la cámara que se aleja). Todo lo demás, quieto.
4. **Ritmo de fondos:** qué láminas van a `sangre`, cuáles a `bruma` y cuáles claras. Nunca más de dos seguidas con el mismo fondo y la misma estructura.
5. **Familia de ilustración:** una metáfora visual y un solo trazo (mismo grosor y escala en todas): red, ramas, ondas, capas, órbitas, sinapsis… más el set base de íconos para objetos concretos.

Terminado cuando cada lámina de la lista tiene su «qué se ve» y la dirección se puede leer en cinco líneas.

## 2. Arcos

**Naming** (elegir entre finalistas): pregunta a sangre (`sangre`) → el problema de menos a más (`zoom`) → por qué importa (`red` con pulso) → qué debe decir el nombre (tres palabras en display sobre `bruma`, no una tabla) → los finalistas juntos (`finalistas`) → una `revelacion` por finalista, alternando `sangre`, `bruma` y claro → elección (los nombres en display, votación). 9–10 láminas.

**Pitch / visión:** gancho a sangre → tensión (`red` o `zoom`) → la idea (`revelacion`) → cómo se ve funcionando (ilustración o demo) → qué se pide (cifra grande + plazo) → cierre a sangre que vuelve al gancho.

## 3. Recetas (todas con tokens; cambian solas con `data-tema`)

```html
<section class="slide sangre">            <!-- o bruma; oscura y lleno siguen existiendo -->
  <div class="textura red desvanece"></div> <!-- puntos · lineas · cruces · ondas · red; desvanece · desvanece-izq; color --tx-c -->
  <p class="display m letras">Las fallas no avisan.</p>              <!-- display: xl 260 · base 190 · m 140 · s 104 px -->
  <p class="display m barrido" style="color:var(--accent);animation-delay:1.1s">Los datos, sí.</p>
  <p class="lema">Una frase de apoyo.</p>
</section>
```

- **Fondo a sangre con contenido encima:** `<div class="fondo velo"><svg …></svg></div>` (el `velo` oscurece la izquierda para el texto; `velo-abajo` la base). Ejemplo: `laminas/zoom.html`.
- **Entradas:** `.letras` (letra a letra; el motor separa el texto), `.barrido` (se descubre de izquierda a derecha), `.crecer` (con `data-paso`, entra desde más chico). Sirven con o sin `data-paso`.
- **Ilustración viva:** trazos con `class="dibujar"` y `style="--d:.4s;--dur:.7s"` para escalonar; `.emite` (onda que sale de un centro, en `<circle>`), `.flota` (vaivén), `.cruza` (viaja `--dx` en x, para partículas). En PDF queda el estado final.
- **Contorno:** `<span class="contorno">Eco</span>` dentro de un `.display` (letra hueca; color con `--c`).
- **Finalistas:** `.finalistas.solido` + `.finalista` con `--c` por tarjeta; el arte usa `currentColor`.

### Ilustración generada

Para metáforas orgánicas (ramas, raíces, red, dendritas) generar el SVG con un script con semilla (reproducible) y pegarlo en la lámina; `laminas/finalistas.html` y `revelacion.html` traen tres ya generadas (ondas, sinapsis, ramas). Reglas:

- `stroke="currentColor"` y `fill="none"` en un `<g>`: el color se elige en la lámina (`style="color:var(--accent)"`).
- Grosor que baja con la profundidad; `--d` que sube con la profundidad (el dibujo crece desde el centro).
- 300–600 trazos como máximo (más pesa y no se ve). Sin ids, o con prefijo del id de la lámina.
- Si se repite en varias láminas, insertarlo con marcadores y `--pre` (ver `componentes.md` §12).

Núcleo de un generador de ramas:

```python
def crecer(x, y, a, L, d):
    x2, y2 = x + cos(a) * L, y + sin(a) * L
    k = rnd.uniform(-.35, .35) * L                      # curva
    mx, my = (x + x2) / 2 - sin(a) * k, (y + y2) / 2 + cos(a) * k
    out.append(f'<path class="dibujar" d="M{x} {y}Q{mx} {my} {x2} {y2}" stroke-width="{max(1.4, 6.5 - d * 1.15)}" style="--d:{d * .22}s"/>')
    if d < PROF:
        for s in (-1, 1): crecer(x2, y2, a + s * rnd.uniform(.25, .35), L * rnd.uniform(.74, .88), d + 1)
```

## 4. Qué evitar (se ve generado)

- Grillas de tarjetas blancas iguales lámina tras lámina; ilustraciones chicas metidas en tarjetas.
- El kicker en mayúsculas en todas las láminas y una palabra en `em.ac` en todos los títulos: usarlos donde informan.
- Numeración 01/02/03 si el contenido no es una secuencia.
- Degradados o texturas sin función: la textura dice algo del tema (red = conexiones, ondas = señal, cruces = salud).
- Más de un movimiento continuo por lámina.

## 5. Lo que revisa el linter con `data-diseno="concepto"`

No avisa tema oscuro; acepta colores hex dentro de `<svg>` (paletas de ilustración) y el doble de rótulos SVG (140 palabras). En cambio avisa si más de la mitad de las láminas son solo texto o tarjetas (sin `svg`, imagen, `.display`, `.fondo`, `.textura`, fondo `sangre/bruma/oscura/lleno` ni `data-pasos`), si ninguna lámina tiene un elemento de alto impacto (`.display`, `sangre`, `.fondo`, `finalistas`, `grafo`, `zoom`), si ninguna cambia el fondo, o si hay tres láminas seguidas de tarjetas. En todas las presentaciones, las capas de un `.apilar` con `data-solo` cuentan como una sola (se ve una a la vez). El hex en `style` de HTML sigue avisando: la paleta propia va como token en `estilo.css`.

## 6. Revisión en la hoja de contactos

- Al menos un tercio de las láminas con fondo distinto al del tema, repartidas (no todas al final).
- Ninguna fila de la hoja con tres láminas de la misma estructura.
- El momento memorable se entiende también en el PDF (estado final legible, no a mitad de animación).
- Leer solo los titulares en display: ¿cuentan la historia?
