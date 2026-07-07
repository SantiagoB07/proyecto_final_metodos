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

## D7 — Fuente de datos: SPY en vez de ^SPX (bloqueo de liquidez)
**Decisión:** usar opciones de **SPY** (ETF del S&P 500) para la calibración, en vez de ^SPX.
**Por qué:** el snapshot de ^SPX (tomado fuera del horario de mercado de EE. UU.) solo trae cotizaciones bid/ask válidas para calls ITM (strike < spot); las OTM/ATM tienen bid=ask=0 (verificado: 43 calls válidas, 0 con K>S). Una calibración solo-ITM está mal condicionada y no muestra el desempeño OTM que el artículo destaca. SPY, en cambio, tiene cobertura completa (650 calls válidas: 323 OTM + 327 ITM). El código conserva soporte para ^SPX (parámetro `ticker`), así que la elección es reversible si se descarga en horario de mercado.
**Consecuencia (limitación a documentar):** las opciones de SPY son AMERICANAS, mientras el modelo es europeo. Para calls de corto plazo (30-90 días) sobre un subyacente de bajo dividendo (~1.2%), la prima de ejercicio anticipado es despreciable, así que la valoración europea es una buena aproximación. Se documenta en la discusión.

## D8 — Rendimiento por dividendos q estimado por paridad put-call
**Decisión:** incorporar dividendos con un `q` estimado por vencimiento a partir de la paridad put-call (forward implícito), en vez de q=0 o un q fijo.
**Por qué:** SPY paga dividendos (~1.2%). La paridad C - P = e^{-rτ}(F - K) da el forward implícito F por vencimiento usando pares call/put líquidos; luego q = r - ln(F/S)/τ. Es autocontenido (no requiere datos externos de dividendos) y consistente con los precios observados. Resuelve la duda abierta de dividendos.

## D9 — Panel histórico de 6 meses (fidelidad al diseño del artículo)
**Decisión:** además del corte transversal único, construir un PANEL de ~6 meses (miércoles in-sample, jueves out-of-sample) replicando el diseño del artículo, calibrando por fecha y promediando ("daily-averaged").
**Fuente:** cadenas EOD de SPY de la base pública de DoltHub (post-no-preference/options), que sí ofrece histórico diario (yfinance solo da la cadena actual). Spot de SPY y tasa ^IRX de yfinance; q por paridad put-call por fecha (recortada a [-0.05,0.06]). La API de DoltHub expira en escaneos de rango → se consulta por fecha exacta (indexada). Calibración por fecha en paralelo (multiprocessing, 4 procesos).
**Resultado:** con el panel, Lin-He SÍ mejora a Heston (in-sample medio 0.0437 vs 0.0455, ~4%; mejora estricta en 52% de fechas; λ medio ~0.015 > 0). Dirección coincide con el artículo, magnitud mucho menor (el artículo reporta ~45% en SPX 2011, periodo de crisis con más cambio de régimen; nosotros SPY 2026, más calmo, con menos opciones/vencimientos por fecha). Out-of-sample: mediana 0.268 vs 0.270 (la media se infla por 2 fechas con saltos overnight → se reporta mediana como estadística robusta).
