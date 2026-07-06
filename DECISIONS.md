# DECISIONS — Registro de decisiones de diseño

Decisiones importantes tomadas durante la implementación, con su justificación.

## D1 — Gestión de entorno con uv
**Decisión:** usar uv (`pyproject.toml` + `uv.lock`) en vez de pip/requirements.txt.
**Por qué:** entorno exactamente reproducible (lock versionado), instala Python si falta, instala el paquete `rsheston` en modo editable. Cubre el requisito de la rúbrica de "dependencias/versiones".

## D2 — `src` layout con paquete `rsheston`
**Decisión:** biblioteca bajo `src/rsheston/`, ejecutables en `scripts/`, tests en `tests/`.
**Por qué:** evita imports accidentales del cwd; separa lógica pura (sin I/O) de la orquestación. Una sola ruta de cálculo de precios usada por verificación y calibración.

## D3 — Trabajo escrito en Typst; slides en reveal.js
**Decisión:** Typst para el paper (PDF + fuentes `.typ`), reveal.js para las diapositivas (entrega PDF vía decktape).
**Por qué:** el usuario lo pidió. PDF equivalente a LaTeX. Riesgo: la rúbrica dice "preferentemente LaTeX" → confirmar con profesor.

## D4 — Fuente de datos: yfinance `^SPX`
**Decisión:** opciones europeas sobre el S&P 500 vía yfinance; tasa `^IRX`.
**Por qué:** mismo subyacente que el artículo, europeas (coincide con el modelo), gratis y reproducible. Verificado que funciona en el entorno.
**Consecuencia:** snapshot en vivo → guardar crudo con fecha en `data/raw/`, calibrar desde archivo.

<!-- Nuevas decisiones se agregan abajo con D5, D6, ... -->

## D5 — m(-j) analítico en el valuador de Gil-Pelaez
**Decisión:** el valuador calcula `m(-j) = S·e^{(r-q)τ}` analíticamente en vez de evaluar la fórmula cerrada de la función característica en φ=-j.
**Por qué:** la fórmula tiene una singularidad removible en φ=0 y φ=-j (allí `a+d=0` y `g` diverge → nan). Como `m(-j)=E[S_T]` vale para cualquier modelo martingala, calcularlo analíticamente es exacto y robusto, y sirve para Heston y Lin–He por igual. Los nodos de Gauss-Legendre son reales positivos, así que nunca tocan la singularidad.
