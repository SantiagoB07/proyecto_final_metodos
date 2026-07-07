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

## D6 — Truncamiento adaptativo en Gil-Pelaez (cf no acotada del modelo)
**Decisión:** el valuador trunca la integral de Gil-Pelaez donde `|m(φ)|` ya decayó por debajo de una tolerancia, en vez de usar un límite superior fijo.
**Por qué:** al romperse la condición de Feller (el término λ·dB permite varianza negativa), la función característica FORMAL del modelo no está acotada por 1 como una cf genuina: decae a frecuencias moderadas pero **crece exponencialmente en la cola** (verificado: con λ=(0.01,0.05) y T=0.5, |m| baja a 1e-40 en φ≈120 y sube a 1e+25 en φ=200). Un u_max fijo demasiado grande contamina el precio. El truncamiento adaptativo elige u_max en la región de decaimiento (antes de la explosión), dando precios estables. Para λ calibrado (~0.045) la explosión está lejísimos en la cola y el precio es estable en cualquier u_max razonable.
**Consecuencia:** este comportamiento se analiza y documenta en la Etapa 4 (análisis numérico) y se conecta con la discusión de la violación de Feller (limitación del modelo). El parámetro `adaptive=False` permite estudiar la convergencia con u_max fijo.
