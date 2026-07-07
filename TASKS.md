# TASKS — Seguimiento del proyecto

Documento vivo de coordinación. Estado del proyecto, tareas por etapa, bloqueantes y decisiones.
Plan detallado en [`docs/plan.md`](docs/plan.md). Contexto en [`AGENTS.md`](AGENTS.md).

Leyenda: ⬜ pendiente · 🟡 en progreso · ✅ completada · ⛔ bloqueada

## Estado global

| Etapa | Descripción | Estado |
| --- | --- | --- |
| 0 | Infraestructura (uv, layout, tooling) | ✅ |
| 1 | Pricer de referencia (Black–Scholes, Heston) | ✅ |
| 2 | Pricer del modelo Lin–He | ✅ |
| 3 | Verificación Monte Carlo + figuras del artículo | 🟡 |
| 4 | Análisis numérico del método | 🟡 (script listo) |
| 5 | Datos de mercado (yfinance **SPY**, ver D7) | 🟡 (datos listos) |
| 6 | Calibración (MSE, dual_annealing) | 🟡 (código listo) |
| 7 | Trabajo escrito (Typst) | ⬜ |
| 8 | Diapositivas (reveal.js) + ensayo | ⬜ |

## Etapa 0 — Infraestructura ✅

- ✅ Instalar uv (v0.11.27) y typst CLI (v0.15.0) en `~/.local/bin`
- ✅ `uv init --lib` + `pyproject.toml` con `src` layout, paquete `rsheston`, Python 3.14
- ✅ `uv add` dependencias: numpy 2.5, scipy 1.18, pandas 3.0, matplotlib, yfinance; dev: pytest
- ✅ Layout de carpetas (src, tests, scripts, data, results, paper, slides) + .gitkeep
- ✅ `.gitignore`, README.md con mapa script→figura
- ✅ Esqueleto paper/main.typ (compila a PDF ✓) + refs.bib
- ✅ Esqueleto slides/index.html (reveal.js + KaTeX)
- ✅ Verificación: `uv sync` ✓, `import rsheston` ✓, `pytest` corre ✓, `typst compile` ✓

Nota: exportación de slides a PDF se verifica en Etapa 8 (requiere navegador, no headless).

## Etapa 1 — Pricer de referencia (Black–Scholes, Heston) ✅

- ✅ Black–Scholes cerrado (call/put con q) + volatilidad implícita (Brent)
- ✅ Función característica de Heston (`charfn.py`: heston_core/D/Cbar/cf)
- ✅ Pricer por Gil-Pelaez (P₁, P₂; Gauss-Legendre truncado, defaults u_max=200, n=256)
- ✅ 13 tests: BS ref, paridad put-call (BS y Heston), IV roundtrip, m(0)=1/m(-j)=fwd,
  Heston→BS (σ→0) en 5 strikes, GL vs quad adaptativo, convergencia
- Decisión D5: m(-j) se calcula analíticamente como S·e^{(r-q)τ} (singularidad removible en φ=-j)

## Etapa 2 — Pricer del modelo Lin–He ✅

- ✅ f(φ;τ) (ec. 2.19) — VALIDADA contra integral numérica de D²
- ✅ Matriz M (ec. 2.18) + expm 2×2 en forma cerrada vectorizada (vs scipy.linalg.expm)
- ✅ Función característica m(φ) (ec. 2.20) con forma estable (autovalores μ±) anti-overflow
- ✅ Truncamiento adaptativo en Gil-Pelaez (D6: la cf no está acotada, explota en la cola)
- ✅ 20 tests nuevos: degeneración exacta a Heston (cf y precio en 5 strikes), m(0)=1,
  expm vs scipy, f vs ∫D², truncamiento adaptativo, monotonía en S
- Erratas del artículo detectadas: M(2,2) sin τ (corregida), pie Fig.1 "variance swap"
- Decisión D6: truncamiento adaptativo por la cf no acotada (violación de Feller)

## Etapa 3 — Verificación Monte Carlo + figuras del artículo

- ✅ Semi-Monte-Carlo (cadena de Markov + cf condicional) y Euler completo independiente
- ✅ Figs. 01 (degeneración), 03 (precio vs z, precio vs vencimiento) generadas y revisadas
- 🟡 Script 02 (fórmula vs MC, tabla de errores) corriendo — pendiente su figura/tabla
- ✅ 4 tests MC verdes (semi-MC vs fórmula, Euler vs fórmula, reproducibilidad, cadena)

## Nota — cambio de fuente de datos (D7)
^SPX fuera de horario solo da calls ITM válidas → cambiado a **SPY** (cobertura completa
OTM/ATM/ITM). Opciones americanas ≈ europeas para calls de corto plazo (limitación documentada).
Dividendos q estimados por paridad put-call (D8). 650 contratos → 325 in / 325 out.

## Etapas 4-6 — código listo, pendiente ejecución/commit
- Etapa 4: scripts/04_numerical_analysis.py (convergencia, truncamiento, integrando, costo)
- Etapa 5: market_data.py + scripts/05 (SPY, filtros, q por paridad) — datos ya generados
- Etapa 6: calibration.py + scripts/06 (Heston y Lin-He, MSE, dual_annealing, in/out/moneyness)

## Bloqueantes

- Ninguno actualmente.

## Dudas abiertas (no bloquean)

1. ¿Calibrar también Elliott–Lian? — recomendado, se puede posponer.
2. Dividendos: pricer con `q` opcional (default 0), documentar decisión.
3. Typst vs "preferentemente LaTeX" — confirmar con profesor.

## Decisiones de diseño

Ver [`DECISIONS.md`](DECISIONS.md).
