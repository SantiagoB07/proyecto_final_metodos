# TASKS — Seguimiento del proyecto

Documento vivo de coordinación. Estado del proyecto, tareas por etapa, bloqueantes y decisiones.
Plan detallado en [`docs/plan.md`](docs/plan.md). Contexto en [`AGENTS.md`](AGENTS.md).

Leyenda: ⬜ pendiente · 🟡 en progreso · ✅ completada · ⛔ bloqueada

## Estado global

| Etapa | Descripción | Estado |
| --- | --- | --- |
| 0 | Infraestructura (uv, layout, tooling) | ✅ |
| 1 | Pricer de referencia (Black–Scholes, Heston) | 🟡 |
| 2 | Pricer del modelo Lin–He | ⬜ |
| 3 | Verificación Monte Carlo + figuras del artículo | ⬜ |
| 4 | Análisis numérico del método | ⬜ |
| 5 | Datos de mercado (yfinance ^SPX) | ⬜ |
| 6 | Calibración (MSE, dual_annealing) | ⬜ |
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

## Etapa 1 — Pricer de referencia (Black–Scholes, Heston)

- ⬜ Black–Scholes cerrado (call/put) + volatilidad implícita (Brent)
- ⬜ Función característica de Heston
- ⬜ Pricer por Gil-Pelaez (P₁, P₂ con cuadratura)
- ⬜ Tests: Heston→BS (σ→0, v₀=θ), paridad put-call, valores de referencia

## Bloqueantes

- Ninguno actualmente.

## Dudas abiertas (no bloquean)

1. ¿Calibrar también Elliott–Lian? — recomendado, se puede posponer.
2. Dividendos: pricer con `q` opcional (default 0), documentar decisión.
3. Typst vs "preferentemente LaTeX" — confirmar con profesor.

## Decisiones de diseño

Ver [`DECISIONS.md`](DECISIONS.md).
