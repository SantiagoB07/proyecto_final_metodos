# rsheston — Modelo Heston de dos factores con cambio de régimen

Implementación, verificación y calibración del modelo de valoración de opciones europeas de
**Lin, S. y He, X.-J. (2021)**, *"Analytically Pricing European Options under a New Two-Factor
Heston Model with Regime Switching"*, Computational Economics,
DOI [10.1007/s10614-021-10117-6](https://doi.org/10.1007/s10614-021-10117-6).

Proyecto final del curso *Métodos Numéricos en Finanzas* (Maestría en Actuaría y Finanzas,
Universidad Nacional de Colombia, 2026-I). Ver [`AGENTS.md`](AGENTS.md) para el contexto y
[`docs/plan.md`](docs/plan.md) para el plan de implementación.

## Requisitos

- [uv](https://docs.astral.sh/uv/) (gestiona Python, el entorno virtual y las dependencias).
- [Typst](https://typst.app/) ≥ 0.15 (para compilar el trabajo escrito).
- [Node.js](https://nodejs.org/) ≥ 18 (para servir/exportar las diapositivas reveal.js).

## Instalación

```bash
uv sync          # crea .venv e instala dependencias exactas desde uv.lock
```

## Uso

```bash
uv run pytest                                 # verificación automatizada
uv run python scripts/05_get_data.py          # descargar y guardar snapshot de datos
uv run python scripts/07_make_all.py          # reproducir todas las figuras y tablas
typst compile --root . paper/main.typ paper/main.pdf   # compilar el trabajo escrito
```

## Estructura

```
src/rsheston/   biblioteca: charfn, pricing, montecarlo, calibration, market_data
tests/          verificación automatizada (pytest)
scripts/        ejecutables numerados (uno por figura/tabla)
data/           raw/ (snapshots con fecha), processed/ (filtrados)
results/        figures/, tables/ (consumidos por el paper)
paper/          trabajo escrito (Typst)
slides/         diapositivas (reveal.js)
docs/           rúbrica, artículo, programa, plan
```

## Mapa script → figura/tabla

| Script | Genera | Sección del documento |
| --- | --- | --- |
| `scripts/01_verify_heston_limit.py` | `figures/01_degeneracion_heston.png` | Verificación |
| `scripts/02_verify_semimc.py` | `figures/02_formula_vs_montecarlo.png`, `tables/02_errores_montecarlo.csv` | Verificación |
| `scripts/03_figs_articulo.py` | `figures/03_precio_vs_z.png`, `figures/03_precio_vs_vencimiento.png` | Verificación |
| `scripts/04_numerical_analysis.py` | `figures/04_convergencia_nodos.png`, `04_truncamiento_y_cola.png`, `04_integrando.png`, `tables/04_costo_computacional.csv` | Discusión |
| `scripts/05_get_data.py` | `data/raw/`, `data/processed/`, `figures/05_sonrisa_volatilidad.png`, `tables/05_resumen_datos.csv` | Datos |
| `scripts/06_calibrate.py` | `tables/06_parametros.csv`, `06_errores.csv`, `06_errores_moneyness.csv`, `figures/06_ajuste_calibracion.png` | Calibración |
| `scripts/07_make_all.py` | reproduce todo lo anterior | — |

Diapositivas: `slides/index.html` (reveal.js); exportar a PDF con
`npx decktape reveal --chrome-arg=--no-sandbox http://localhost:PORT/index.html slides/slides.pdf`
(servir `slides/` con `python -m http.server` primero).

## Nota sobre el uso de IA

Este proyecto se desarrolló con apoyo de herramientas de IA (asistente de código) para depuración
y redacción. La responsabilidad intelectual y la comprensión de los resultados son del grupo.
