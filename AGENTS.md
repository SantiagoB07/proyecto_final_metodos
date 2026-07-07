# AGENTS.md — Guía y contexto del proyecto

Orientación para cualquier agente o colaborador que trabaje en este repositorio. Para el plan de trabajo detallado por etapas, ver [`docs/plan.md`](docs/plan.md).

## Qué es este proyecto

Proyecto final del curso **Métodos Numéricos en Finanzas** (Maestría en Actuaría y Finanzas, Universidad Nacional de Colombia, 2026-I; prof. Oscar Javier López Alfonso). Vale el **40 % de la nota del curso**.

El trabajo consiste en leer, comprender e **implementar y calibrar a datos de mercado reales** un artículo de investigación sobre valoración de opciones con solución semianalítica, y comunicarlo en cuatro entregables: trabajo escrito, código reproducible, diapositivas y exposición oral.

## El artículo asignado

Lin, S. y He, X.-J. (2021), *"Analytically Pricing European Options under a New Two-Factor Heston Model with Regime Switching"*, Computational Economics, DOI [10.1007/s10614-021-10117-6](https://doi.org/10.1007/s10614-021-10117-6). Texto completo transcrito en [`docs/articulo.md`](docs/articulo.md).

**Modelo (medida neutral al riesgo):**
- Subyacente: `dS/S = r dt + √v dW¹`
- Varianza (dos factores): `dv = k(θ − v) dt + σ√v dW² + λ_{X_t} dB`

con `corr(W¹,W²)=ρ`, `B` independiente, y `X_t` cadena de Markov de 2 estados que hace `λ_{X_t} ∈ {λ₁,λ₂}`. **Con `λ₁=λ₂=0` degenera exactamente a Heston** (usar esto para verificar).

**Aporte técnico:** función característica cerrada derivada en dos pasos (condicional vía Feynman–Kac + ansatz de Heston; luego esperanza sobre la cadena de Markov vía exponencial matricial `⟨e^M X_t, I⟩`). Precio de call europea por inversión de **Gil-Pelaez** (ecs. 2.4–2.8, 2.14–2.20). Calibración empírica por **MSE** con optimización global (ASA), comparando contra Heston y Elliott–Lian sobre opciones del S&P 500.

## Entregables y criterios (rúbrica)

Detalle en [`docs/rubrica.md`](docs/rubrica.md). Pesos:

| Criterio | Peso |
| --- | --- |
| Trabajo escrito (rigor, discusión crítica) | 35 % |
| Código y reproducibilidad | 20 % |
| Corrección de implementación y calibración | 20 % |
| Exposición y diapositivas | 15 % |
| Comprensión teórica (preguntas individuales) | 10 % |

Trabajo escrito: 12–20 páginas, PDF (formato Carta, 11–12 pt, ecuaciones numeradas). Diapositivas: 15–20, PDF. Exposición: 20 min, **todos** intervienen.

## Stack y decisiones técnicas

- **Lenguaje:** Python 3 (`numpy`, `scipy`, `pandas`, `matplotlib`, `yfinance`).
- **Entorno y dependencias:** **uv** (`pyproject.toml` + `uv.lock` versionado; `src` layout con el paquete `rsheston` instalado editable por `uv sync`). Nunca `pip install` suelto: todo por `uv add`.
- **Trabajo escrito:** **Typst** (`paper/main.typ`, bibliografía BibTeX nativa, tablas leídas de CSV con `csv()`). PDF final con `typst compile`; typst.app sirve como editor colaborativo, pero el repo es la fuente de verdad.
- **Diapositivas:** **reveal.js** (`slides/index.html`, KaTeX para ecuaciones); la entrega es el **PDF** exportado con decktape.
- **Fuente de datos:** yfinance con `^SPX` — opciones **europeas** sobre el S&P 500 (mismo subyacente que el artículo). Verificado que funciona en este entorno.
- **Tasa libre de riesgo:** `^IRX` (T-Bill 13 semanas) vía yfinance.
- **Optimizador de calibración:** `scipy.optimize.dual_annealing` (análogo abierto al ASA del artículo).
- **Precio de mercado:** punto medio bid-ask.
- **Idioma de todos los entregables:** español.

## Convenciones de trabajo

- **Verificación primero:** no confiar en la transcripción de fórmulas del artículo (tiene posibles erratas). Toda fórmula se valida numéricamente — degeneración a Heston, `m(0)=1`, `m(−j)=S·e^{rτ}`, semi-Monte-Carlo — y esos criterios se codifican como tests de pytest en `tests/`.
- **Reproducibilidad:** yfinance es una API en vivo. El script de descarga **guarda el snapshot crudo con fecha en `data/raw/`** (versionado); la calibración lee de ese archivo, no de la API. Fijar semillas; reportar optimizador, cotas y valores iniciales; **sin rutas absolutas** (ejecutar siempre con `uv run` desde la raíz).
- **Un script por figura/tabla:** cada salida del documento se genera con un script numerado en `scripts/`, y el README mantiene el mapa "script → figura/tabla". `07_make_all.py` reproduce todo de principio a fin.
- **Separación biblioteca / ejecutables / salidas:** `src/rsheston/` es lógica pura sin I/O; `scripts/` orquesta y escribe a `results/`; `paper/` y `slides/` solo leen de `results/` (nunca números copiados a mano).
- **Citación:** todo código, dato o texto de terceros se cita (numpy/scipy, QuantLib, yfinance, el artículo, y Hirsa 2024 como texto base del curso). El grupo debe **comprender y poder explicar** el núcleo del método.
- **Declaración de IA:** el uso de herramientas de IA como apoyo debe declararse en una nota breve del trabajo escrito.

## Dudas abiertas

1. **¿Calibrar también el modelo Elliott–Lian?** Recomendado (fortalece la discusión crítica), pero se puede posponer.
2. **Dividendos.** El modelo no los incluye; el pricer llevará un parámetro `q` opcional (por defecto 0). Decisión de modelado a documentar.
3. **Typst vs LaTeX.** La rúbrica dice "preferentemente LaTeX"; usamos Typst (el PDF es equivalente y se entregan las fuentes `.typ`). Confirmar con el profesor.

> Nota: las fechas de entrega de `docs/rubrica.md` y `docs/programa.md` están **desactualizadas**; no tratarlas como plazos reales.

## Estructura del repositorio

Detalle completo (layout, qué se versiona, setup del ambiente) en `docs/plan.md` §4.

```
docs/          rubrica.md, articulo.md, programa.md, plan.md
src/rsheston/  charfn, pricing, montecarlo, calibration, market_data
tests/         verificación automatizada (pytest)
scripts/       01..07 (uno por figura/tabla) + 07_make_all
data/          raw/ (snapshots con fecha, versionados), processed/
results/       figures/, tables/ (CSV que consume Typst)
paper/         Typst (main.typ, refs.bib)
slides/        reveal.js (index.html) + slides.pdf exportado
```

## Comandos útiles

```bash
uv sync                                    # crear/actualizar el venv desde uv.lock
uv run python scripts/05_get_data.py       # descargar y guardar snapshot de datos
uv run python scripts/07_make_all.py       # reproducir todas las figuras y tablas
uv run pytest                              # correr la verificación automatizada
typst compile --root . paper/main.typ      # compilar el trabajo escrito a PDF (--root para leer results/)
typst watch paper/main.typ                 # vista previa en vivo del paper
npx serve slides                           # servir las diapositivas localmente
npx decktape reveal http://localhost:3000 slides/slides.pdf   # exportar slides a PDF
```

**Estado del entorno (verificado 2026-07-06):** node v24 ✓ · uv y typst **no instalados aún** (instalarlos es parte de la Etapa 0 del plan).
