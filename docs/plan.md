# Plan de implementación — Proyecto final

**Curso:** Métodos Numéricos en Finanzas (UNAL, 2026-I) · Prof. Oscar Javier López Alfonso
**Artículo asignado:** Lin, S. y He, X.-J. (2021), *"Analytically Pricing European Options under a New Two-Factor Heston Model with Regime Switching"*, Computational Economics, DOI [10.1007/s10614-021-10117-6](https://doi.org/10.1007/s10614-021-10117-6).

Este documento es el plan de trabajo detallado. Para la orientación rápida y las convenciones del repositorio, ver [`../AGENTS.md`](../AGENTS.md). Los documentos fuente del curso están en [`rubrica.md`](rubrica.md), [`articulo.md`](articulo.md) y [`programa.md`](programa.md).

---

## 1. Objetivo

Reconstruir, implementar, verificar y **calibrar a datos de mercado reales** el modelo de Lin–He (Heston de dos factores con cambio de régimen en la volatilidad de la volatilidad), comparándolo contra el modelo de Heston (y, si el tiempo lo permite, contra el modelo de Elliott–Lian), y comunicar los resultados en un trabajo escrito tipo artículo, código reproducible, diapositivas y una exposición oral.

El modelo, bajo la medida neutral al riesgo:

- Subyacente: `dS/S = r dt + √v dW¹`
- Varianza (dos factores): `dv = k(θ − v) dt + σ√v dW² + λ_{X_t} dB`

con `corr(W¹, W²) = ρ`, `B` browniano independiente, y `X_t` una cadena de Markov de 2 estados (tasas `λ₁₂`, `λ₂₁`) que hace que `λ_{X_t} ∈ {λ₁, λ₂}`. Con `λ₁ = λ₂ = 0` el modelo **degenera exactamente a Heston** (propiedad clave para la verificación).

El precio de la call europea se obtiene por inversión de Gil-Pelaez (ecs. 2.4–2.8 del artículo):

```
U = e^{−rτ} [ m(−j) · P₁ − K · P₂ ]
```

donde `m(φ)` es la función característica cerrada (ec. 2.20), construida en dos pasos: función característica condicional `h(φ|X_T)` (ansatz exponencial-afín de Heston → ODEs de `D` (Riccati, ec. 2.14) y `C` (ec. 2.15)) y luego la esperanza sobre la cadena de Markov vía la exponencial matricial `⟨e^M X_t, I⟩` (ecs. 2.17–2.19, resultado de Elliott–Lian 2013).

---

## 2. Decisiones ya tomadas

| Decisión | Elección | Notas |
| --- | --- | --- |
| Lenguaje | **Python 3** | Recomendado por rúbrica y programa. |
| Gestión de dependencias y venv | **[uv](https://docs.astral.sh/uv/)** | `pyproject.toml` + `uv.lock` versionado → entorno exactamente reproducible (§4). |
| Fuente de datos | **yfinance con `^SPX`** | Opciones **europeas** sobre el S&P 500 (mismo subyacente que el artículo). Verificado: hay internet, la librería descarga bid/ask/strike/vencimiento/IV. |
| Tasa libre de riesgo | **`^IRX`** (T-Bill 13 semanas) vía yfinance | Análogo al T-Bill de 3 meses del artículo. |
| Optimizador de calibración | **`scipy.optimize.dual_annealing`** (global) | Análogo abierto al ASA que usa el artículo; se debe citar y reportar cotas, punto inicial y semilla. |
| Precio de mercado | Punto medio **bid-ask** | Igual que el artículo. |
| Trabajo escrito | **[Typst](https://typst.app/)** → PDF | Detalle en §7. La rúbrica dice "preferentemente LaTeX"; Typst entrega el mismo PDF y las fuentes `.typ` (ver riesgo en §10). |
| Diapositivas | **[reveal.js](https://revealjs.com/)** → PDF | Detalle en §8. La rúbrica sugiere "Beamer u otra herramienta" y exige PDF; se exporta con decktape. |
| Idioma de los entregables | **Español** | Curso en español. |

**Advertencia de reproducibilidad (crítica):** yfinance es una API en vivo; el mercado se mueve. El script de descarga **debe guardar el snapshot crudo en `data/raw/` con su fecha**, y la calibración debe leer de ese archivo, no de la API. Así "obtener los datos" y "reproducir tablas/figuras" quedan separados y ambos funcionan meses después.

---

## 3. Dudas abiertas (no bloquean el desarrollo)

1. **¿Se calibra también el modelo Elliott–Lian?** El artículo compara los tres modelos (Tablas 1–3). Recomendación: incluirlo (fortalece la discusión crítica, 35 % de la nota), pero se puede posponer hasta tener el modelo principal funcionando.
2. **Dividendos.** El modelo del artículo no incluye rendimiento por dividendos `q`, pero el S&P 500 sí paga. Mitigación: implementar el pricer con un parámetro `q` opcional (por defecto 0), reemplazando `r` por `r − q` en la deriva. La decisión de modelado se documenta cuando se tome; no detiene el código.
3. **Typst en lugar de LaTeX.** La rúbrica dice "preferentemente LaTeX". El PDF final es indistinguible y se entregan las fuentes `.typ`; riesgo bajo, pero vale la pena confirmarlo con el profesor.

---

## 4. Estructura del proyecto: carpetas, layout y ambiente

### 4.1 Layout de carpetas

```
finanzas/
├── AGENTS.md                  # guía y contexto para agentes/colaboradores
├── README.md                  # descripción, instrucciones, mapa script → figura/tabla
├── pyproject.toml             # metadatos del proyecto + dependencias
├── uv.lock                    # versiones exactas resueltas (VERSIONADO en git)
├── .python-version            # versión de Python fijada (la usa uv)
├── .gitignore                 # .venv/, __pycache__/, *.pyc, node_modules/
├── docs/                      # rubrica.md, articulo.md, programa.md, plan.md
├── src/rsheston/              # BIBLIOTECA: lógica pura, sin I/O ni rutas
│   ├── __init__.py
│   ├── charfn.py              # D, C̄, f, M, m(φ): ecs. 2.14–2.20 (Lin–He, Heston, [Elliott–Lian])
│   ├── pricing.py             # Gil-Pelaez (P₁, P₂), Black–Scholes, volatilidad implícita
│   ├── montecarlo.py          # semi-MC (cadena de Markov + fórmula condicional), MC Euler
│   ├── calibration.py         # objetivo MSE, cotas, wrapper del optimizador global
│   └── market_data.py         # descarga yfinance, filtros, tasas, dividendos
├── tests/                     # verificación automatizada (pytest)
│   ├── test_pricing.py        # BS, paridad put-call, Heston vs referencia
│   └── test_charfn.py         # degeneración a Heston, m(0)=1, m(−j)=S·e^{rτ}
├── scripts/                   # EJECUTABLES: uno por figura/tabla del documento
│   ├── 01_verify_heston_limit.py
│   ├── 02_verify_semimc.py        # → Fig. tipo 1 (fórmula vs Monte Carlo)
│   ├── 03_figs_articulo.py        # → Figs. tipo 2 y 3 (degeneración, vencimiento)
│   ├── 04_numerical_analysis.py   # convergencia, truncamiento, tiempos
│   ├── 05_get_data.py             # descarga y guarda snapshot en data/raw/
│   ├── 06_calibrate.py            # → Tablas tipo 1–3 (semilla fija)
│   └── 07_make_all.py             # reproduce todo de principio a fin
├── data/
│   ├── raw/                   # snapshots crudos CON FECHA en el nombre (versionados)
│   └── processed/             # filtrados, separados in-sample / out-of-sample
├── results/
│   ├── figures/               # PNG/SVG que consumen el paper y las slides
│   └── tables/                # CSV que Typst lee con csv() — sin copy-paste
├── paper/                     # trabajo escrito en Typst (§7)
│   ├── main.typ
│   └── refs.bib               # BibTeX (Typst lo lee nativamente)
└── slides/                    # diapositivas reveal.js (§8)
    ├── index.html
    └── slides.pdf             # export para la entrega
```

Principios del layout:

- **Separación biblioteca / ejecutables / salidas.** `src/rsheston/` no hace I/O ni conoce rutas; `scripts/` orquesta y escribe a `results/`; `paper/` y `slides/` solo *leen* de `results/`. Así cada figura tiene una única ruta de generación.
- **`src` layout** (paquete bajo `src/`): evita imports accidentales del directorio de trabajo y obliga a que el paquete esté instalado en el venv — con uv esto es automático (`uv sync` lo instala en modo editable).
- **Qué se versiona en git:** todo lo anterior salvo `.venv/`, cachés y `node_modules/`. En particular **sí** se versionan `uv.lock` (reproducibilidad del entorno), los snapshots de `data/raw/` (son pequeños y sin ellos las tablas no son reproducibles; se cita la fuente — ver rúbrica sobre licencias) y las figuras/tablas finales de `results/` que el paper incluye (para que el PDF compile sin re-correr la calibración completa).

### 4.2 Ambiente con uv

uv gestiona la versión de Python, el venv y las dependencias desde `pyproject.toml`, con resolución exacta en `uv.lock`. Esto cubre directamente el requisito de la rúbrica de "dependencias/versiones" reproducibles.

Instalación (una vez por máquina; no está instalado en este entorno aún):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Configuración inicial del proyecto (Etapa 0):

```bash
uv init --lib --name rsheston        # crea pyproject.toml con src layout
uv add numpy scipy pandas matplotlib yfinance
uv add --dev pytest
```

`pyproject.toml` resultante (esquema): sección `[project]` con nombre, versión y dependencias; `[build-system]` (hatchling) para que `rsheston` sea instalable; `requires-python` fijado. `.python-version` fija el intérprete (uv lo descarga si no existe en la máquina).

Uso diario:

```bash
uv sync                                   # crea/actualiza .venv desde uv.lock
uv run python scripts/05_get_data.py      # ejecuta dentro del venv (sync implícito)
uv run pytest                             # corre la verificación automatizada
```

Reglas: **nunca** `pip install` suelto (todo pasa por `uv add` para que quede en el lock); `uv.lock` se commitea siempre que cambie; los scripts se ejecutan con `uv run` desde la raíz del repo (rutas relativas a la raíz — la rúbrica prohíbe rutas absolutas).

---

## 5. Arquitectura: flujo de datos y responsabilidades

**Flujo de datos:**

1. `market_data` descarga cadenas crudas → `data/raw/` (con fecha) → filtra y adjunta tasa/dividendos → `data/processed/` (in-sample y out-of-sample separados).
2. `charfn` + `pricing` = **núcleo de valoración**: parámetros → función característica → integrales de Gil-Pelaez → precio. Única ruta de cálculo de precios; la usan tanto verificación como calibración (una sola fuente de verdad).
3. `montecarlo` consume `charfn` (fórmula condicional) para producir precios de referencia independientes.
4. `calibration` toma datos procesados + núcleo de valoración → minimiza MSE → parámetros → evaluación in/out-of-sample y por moneyness.
5. Los `scripts/` orquestan y escriben a `results/`; el paper (Typst) y las slides (reveal.js) incluyen figuras y tablas desde allí sin edición manual.

**Responsabilidades por módulo:**

- `charfn.py`: concentra **todas** las fórmulas del artículo. Es donde viven los riesgos de transcripción, por eso se verifica en tres niveles (Etapas 2–3) y tiene su propio archivo de tests.
- `pricing.py`: aísla la cuadratura de Gil-Pelaez para que el análisis numérico (Etapa 4) se haga variando solo sus parámetros (truncamiento, nodos, amortiguación).
- `calibration.py`: registra optimizador, semilla, cotas y punto inicial en su salida (requisito explícito de la rúbrica).
- Scripts numerados: dan directamente el mapa "script → figura/tabla" que exige el README.

---

## 6. Plan por etapas

Cada etapa lista **objetivo, tareas, dependencias, resultado esperado y verificación**. El orden respeta las dependencias y prioriza la nota por hora invertida (el 55 % de la nota es trabajo escrito + reproducibilidad, y otro 20 % es corrección de la implementación/calibración).

### Etapa 0 — Infraestructura del proyecto
- **Objetivo:** repositorio reproducible desde el día uno.
- **Tareas:** instalar uv; crear el layout de §4.1; `uv init` + `uv add` de dependencias (§4.2); instalar el CLI de Typst (binario oficial de GitHub releases); esqueleto de `README.md`, del paquete `src/rsheston/`, de `paper/main.typ` (§7) y de `slides/index.html` (§8); `.gitignore`.
- **Dependencias:** ninguna.
- **Resultado esperado:** cualquier integrante clona y ejecuta.
- **Verificación:** en entorno limpio, `uv sync && uv run python -c "import rsheston"` funciona; `uv run pytest` corre (aunque vacío); `typst compile paper/main.typ` produce un PDF; las slides abren en el navegador.

### Etapa 1 — Pricer de referencia: Black–Scholes y Heston
- **Objetivo:** tener los casos límite contra los que se verifica todo lo demás.
- **Tareas:** Black–Scholes cerrado; función característica de Heston y pricer por Gil-Pelaez (`P₁`, `P₂` con cuadratura); volatilidad implícita (inversión de BS por Brent). Los criterios de verificación se codifican como tests en `tests/`.
- **Dependencias:** Etapa 0.
- **Resultado esperado:** módulo con Heston verificado.
- **Verificación:** (i) Heston con `v₀ = θ` y `σ → 0` converge a BS; (ii) precios contra valores de referencia publicados o QuantLib (citado); (iii) paridad put-call a tolerancia < 1e-8. Todo como tests de pytest.

### Etapa 2 — Pricer del modelo Lin–He
- **Objetivo:** la fórmula cerrada (2.20)+(2.8) implementada.
- **Tareas:** `d`, `g`, `D` (ec. 2.14); `C̄`; `f(φ;τ)` (ec. 2.19); matriz `M` (ec. 2.18) y `⟨e^M X_t, I⟩` vía `scipy.linalg.expm`; función característica `m(φ)`; pricer reutilizando la cuadratura de la Etapa 1. Vectorizar en strikes.
- **Dependencias:** Etapa 1.
- **Resultado esperado:** `precio_call(S, K, τ, r, params, estado)`.
- **Verificación:** (i) con `λ₁ = λ₂ = 0` coincide con Heston de la Etapa 1 hasta error de cuadratura (prueba más fuerte y barata); (ii) `m(0) = 1` y `m(−j) = S·e^{rτ}` numéricamente. Como tests de pytest.
- **⚠ Riesgos de transcripción a verificar numéricamente** (no confiar en el texto del artículo): entrada (2,2) de `M` (posible errata `−λ₂₁` vs `−λ₂₁τ`); inconsistencia `i`/`j` de la unidad imaginaria en ecs. 2.16/2.20; el pie de la Fig. 1 dice "variance swap" cuando son opciones europeas.

### Etapa 3 — Verificación por Monte Carlo y reproducción de figuras del artículo
- **Objetivo:** cumplir el requisito de verificación de la rúbrica y validar contra el artículo.
- **Tareas:** semi-Monte-Carlo del artículo (simular solo la cadena de Markov; valorar cada trayectoria con la fórmula condicional, integrando `∫λ²D² ds` con la forma cerrada de `f`); opcional una MC completa de Euler; reproducir Figs. 1–3 con los parámetros de la §3 del artículo (`k=10, θ=0.08, σ=0.1, ρ=−0.5, r=0.05, λ₁₂=10, λ₂₁=20, K=10, v₀=0.03`, estado 1).
- **Dependencias:** Etapa 2.
- **Resultado esperado:** figuras propias equivalentes + tabla de errores relativos, en `results/`.
- **Verificación:** error relativo fórmula vs semi-MC del orden del artículo (< 0.7 %); Fig. 2 reproduce coincidencia exacta con Heston en `z=0`.

### Etapa 4 — Análisis numérico del método
- **Objetivo:** el contenido del objetivo 4 de la rúbrica (**aporte propio**: el artículo no detalla la cuadratura).
- **Tareas:** convergencia de la cuadratura de Gil-Pelaez (truncamiento `φ_max` y nº de nodos vs error); comportamiento del integrando (decaimiento, oscilación cerca de `φ=0` por el `1/φ`); estabilidad en `τ` grandes (rama del logaritmo complejo en la forma de `D`); benchmark de tiempo (precio por opción; costo de una evaluación del objetivo).
- **Dependencias:** Etapa 2 (paralelizable con Etapa 3).
- **Resultado esperado:** 2–3 figuras/tablas para la discusión.
- **Verificación:** el error de cuadratura decae al refinar; se fija una configuración por defecto justificada.

### Etapa 5 — Datos de mercado
- **Objetivo:** dataset limpio y documentado, análogo al del artículo.
- **Tareas:** `05_get_data.py` descarga la cadena `^SPX` con yfinance y **guarda el snapshot crudo con fecha** en `data/raw/`; filtros del artículo (vencimiento 30–90 días, `|S−K|/K < 10 %`, precio = mid bid-ask); tasa libre de riesgo (`^IRX`); tratamiento de dividendos (decisión pendiente); separar in-sample / out-of-sample.
- **Dependencias:** Etapa 0 (paralelizable con 1–4).
- **Resultado esperado:** archivos procesados + tabla descriptiva para la sección de datos del trabajo.
- **Verificación:** volatilidades implícitas razonables (sonrisa visible, sin negativas ni outliers absurdos); el script regenera `data/processed/` desde el crudo guardado sin tocar la API.

### Etapa 6 — Calibración
- **Objetivo:** el 20 % de "corrección de implementación y calibración".
- **Tareas:** objetivo MSE en dólares (ec. 4.1); `dual_annealing` (semilla fija) con cotas documentadas (`k, θ, σ, v₀ > 0`; `ρ ∈ (−1,1)`; `λᵢ ≥ 0`; tasas de transición > 0); calibrar Heston (5 parámetros) y Lin–He (9 parámetros) sobre los mismos datos; Elliott–Lian si hay tiempo; evaluar out-of-sample y por buckets de moneyness (Tablas 2–3).
- **Dependencias:** Etapas 2 y 5.
- **Resultado esperado:** tablas análogas a 1–3 con nuestros datos, como CSV en `results/tables/`.
- **Verificación:** reproducible con la misma semilla; el MSE in-sample de Lin–He debe ser **≤** al de Heston (Heston es caso anidado; si no, hay bug o mínimo local); magnitudes de parámetros comparables a la Tabla 1 del artículo (sanity check).

### Etapa 7 — Trabajo escrito (Typst)
- **Objetivo:** el 35 % de la nota. Detalle técnico en §7.
- **Tareas:** redactar las 10 secciones de la rúbrica en `paper/main.typ`; comparación crítica con las Tablas 1–3 del artículo; discusión de limitaciones (Feller violada, identificación de 9 parámetros, datos actuales vs 2011); **nota de declaración de uso de IA**; bibliografía BibTeX (incluir Hirsa 2024, texto base del curso); anexos con fragmentos de código.
- **Dependencias:** Etapas 3, 4, 6 (el esqueleto arranca en la Etapa 0).
- **Resultado esperado:** PDF de 12–20 páginas + fuentes `.typ`.
- **Verificación:** checklist contra la estructura de la rúbrica; toda figura/tabla referenciada en el texto y mapeada a un script en el README; `typst compile` sin warnings de referencias rotas; formato Carta, 11–12 pt, ecuaciones numeradas.

### Etapa 8 — Diapositivas (reveal.js) y ensayo
- **Objetivo:** el 15 % de exposición + preparar el 10 % de preguntas. Detalle técnico en §8.
- **Tareas:** 15–20 diapositivas en `slides/index.html` (motivación, modelo, derivación en 2 pasos, verificación, datos, calibración, comparación con el original, conclusiones); exportar a PDF con decktape; repartir intervenciones entre **todos** los integrantes; ensayo cronometrado; preparar respuestas a preguntas previsibles (¿por qué falla Feller?, ¿por qué el enfoque en dos pasos?, ¿por qué optimización global?, ¿cómo se trunca la integral?, error de Monte Carlo).
- **Dependencias:** Etapa 7 (parcial).
- **Resultado esperado:** `slides/slides.pdf` (entregable) + guion de exposición.
- **Verificación:** el PDF exportado tiene 15–20 diapositivas legibles (ecuaciones y figuras renderizadas); ensayo ≤ 20 min con todos hablando.

---

## 7. Trabajo escrito con Typst

El trabajo escrito se redacta en [Typst](https://typst.app/) en lugar de LaTeX. Motivos: compilación casi instantánea con vista previa (`typst watch`), sintaxis mucho más liviana para el mismo resultado tipográfico, PDF de salida idéntico en calidad (que es lo que se entrega), y **typst.app como editor colaborativo web** para que todo el grupo redacte simultáneamente sin instalar nada.

**Organización:**

- `paper/main.typ` — documento principal (o dividido en un `.typ` por sección si crece).
- `paper/refs.bib` — bibliografía en BibTeX estándar; Typst lo lee nativamente con `#bibliography("refs.bib")`, así que las referencias del artículo, Hirsa 2024, scipy/yfinance, etc. se gestionan igual que en LaTeX.
- Figuras: incluidas desde `results/figures/` con `#figure(image(...), caption: [...])` y referenciadas con `@etiqueta` — cumple "figuras y tablas con leyenda y referencia en el texto".
- Tablas: los scripts exportan CSV a `results/tables/` y Typst los lee con la función nativa `csv()` — **cero copy-paste manual de números**, si la calibración cambia el documento se actualiza recompilando.

**Cumplimiento del formato de la rúbrica** (Carta, 11–12 pt, ecuaciones numeradas):

```typst
#set page(paper: "us-letter")
#set text(size: 11pt, lang: "es")
#set math.equation(numbering: "(1)")
```

**Flujo de trabajo:** las fuentes `.typ` viven en el repo (el repo es la fuente de verdad para la entrega); quien prefiera el editor web trabaja en typst.app y sincroniza al repo. El PDF final se genera localmente con `typst compile paper/main.typ` (CLI: binario oficial de [GitHub releases](https://github.com/typst/typst/releases); no está instalado aún en este entorno).

**Entrega:** PDF + fuentes `.typ` (equivalente a las "fuentes LaTeX" que la rúbrica valora entregar). Ver duda abierta §3.3: confirmar con el profesor que Typst es aceptable dado el "preferentemente LaTeX".

---

## 8. Diapositivas con reveal.js

Las diapositivas se hacen en [reveal.js](https://revealjs.com/) (HTML). Motivos: las figuras de `results/figures/` se incluyen directamente (misma fuente de verdad que el paper), ecuaciones con KaTeX, control visual total con CSS, y la presentación se puede dar desde el navegador con transiciones y notas del orador.

**Organización:**

- `slides/index.html` — deck completo cargando reveal.js (CDN o copia local para presentar sin internet — preferir copia local: el día de la exposición no se depende del wifi del salón).
- Ecuaciones: plugin de matemáticas de reveal (KaTeX) para la dinámica del modelo y la función característica.
- Contenido orientativo (15–20 slides): motivación y volatility smile → el modelo (2 factores + cadena de Markov) → derivación en dos pasos (idea, no álgebra completa) → verificación (fórmula vs semi-MC, degeneración a Heston) → datos y filtros → calibración y resultados (tablas/figuras) → comparación con el artículo original → conclusiones y limitaciones.

**Desarrollo y presentación:**

```bash
npx serve slides            # servir localmente (node ya está disponible: v24)
```

**Exportación a PDF (requisito de la rúbrica — la entrega es PDF):**

```bash
npx decktape reveal http://localhost:3000 slides/slides.pdf
```

(Alternativa manual: abrir con `?print-pdf` y usar "Imprimir → guardar como PDF" del navegador.) La verificación de la Etapa 8 incluye revisar que el PDF exportado renderice bien ecuaciones y figuras — el PDF es lo que se califica, el HTML es la herramienta.

---

## 9. Trazabilidad con la rúbrica

| Requisito de la rúbrica | Peso | Etapas que lo cubren |
| --- | --- | --- |
| Trabajo escrito (rigor, discusión crítica) | 35 % | 7 (se alimenta de 1–6) |
| Código y reproducibilidad | 20 % | 0, 5, y `07_make_all.py` + README + `uv.lock` |
| Corrección de implementación y calibración | 20 % | 1, 2, 3, 6 |
| Exposición y diapositivas | 15 % | 8 |
| Comprensión teórica (preguntas individuales) | 10 % | 2, 3, 8 (dominio de la derivación) |

---

## 10. Riesgos principales y mitigaciones

| Riesgo | Mitigación |
| --- | --- |
| Erratas al transcribir fórmulas del artículo | Verificar cada fórmula numéricamente (degeneración a Heston, `m(0)=1`, semi-MC); tests de pytest. |
| Reproducibilidad de datos en vivo (yfinance) | Guardar snapshot crudo con fecha; calibrar desde el archivo; versionar el snapshot. |
| Calibración de 9 parámetros: no convexa, mal identificada, lenta | Optimización global con semilla y cotas documentadas; verificar `MSE(Lin–He) ≤ MSE(Heston)`; vectorizar el pricer. |
| Inestabilidad de la char. function en `τ` grande (rama del log complejo) | Los vencimientos son 30–90 días (bajo riesgo); documentar en el análisis de estabilidad. |
| Feller violada → varianza negativa | Es propiedad conocida del modelo (reconocida por los autores); documentar como limitación. |
| SPX paga dividendos; el modelo no los tiene | Parámetro `q` opcional; documentar la decisión. |
| La rúbrica dice "preferentemente LaTeX" y usamos Typst | El entregable es PDF (idéntico); se entregan fuentes `.typ`; confirmar con el profesor (§3.3). |
| Las slides son HTML pero la entrega exige PDF | Export con decktape verificado como parte de la Etapa 8; el PDF es el entregable. |
