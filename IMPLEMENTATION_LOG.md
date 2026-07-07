# IMPLEMENTATION_LOG — Diario de implementación

Registro cronológico de avances, evidencia de verificación y hallazgos.

## Etapa 0 — Infraestructura ✅
- Proyecto uv con `src` layout, paquete `rsheston`, Python 3.14. Typst 0.15 y uv 0.11 instalados.
- Verificado: `uv sync`, `import rsheston`, `pytest` (vacío), `typst compile` → PDF.

## Etapa 1 — Pricer de referencia (Black–Scholes, Heston) ✅
- `charfn.py` (Heston) + `pricing.py` (Black–Scholes, IV, Gil-Pelaez).
- 13 tests verdes. Verificaciones clave:
  - Heston → Black–Scholes con σ→0 en 5 strikes (abs < 2e-3).
  - Gil-Pelaez (Gauss-Legendre) vs `scipy.integrate.quad` adaptativo (abs < 1e-4).
  - Paridad put-call, m(0)=1, m(-j)=forward.
- Hallazgo D5: singularidad removible de la cf en φ=0 y φ=-j → m(-j) analítico.

## Etapa 2 — Pricer del modelo Lin–He ✅
- `charfn.py`: f (ec. 2.19), M (ec. 2.18), cf (ec. 2.20) con forma estable por autovalores.
- 20 tests nuevos (33 total verdes). Verificaciones clave:
  - `f(φ;τ)` vs integral numérica de `D²` (abs < 1e-8) — valida la ec. 2.19 independientemente.
  - Degeneración exacta a Heston (cf y precio, λ₁=λ₂=0) en 5 strikes (abs < 1e-8).
  - expm 2×2 cerrada vs `scipy.linalg.expm` (abs < 1e-12).
- Hallazgo D6: la cf del modelo NO está acotada (viola |m|≤1) por la violación de Feller;
  decae a frecuencias moderadas y explota en la cola → truncamiento adaptativo.
- Erratas del artículo detectadas: M(2,2) sin τ (corregida); notación i/j en ecs. 2.16/2.20.

### Revisión adversarial (subagente)
Un subagente revisó símbolo por símbolo `charfn.py`/`pricing.py` contra la Sección 2 del
artículo. Conclusión: implementación fiel en los 6 puntos (D, C̄, f, M, Gil-Pelaez, i/j). Las
únicas divergencias son las dos erratas del artículo (a favor del código) y la extensión de
dividendos (idéntica con q=0). Sin errores reales.

## Etapa 3 — Verificación Monte Carlo + figuras del artículo 🟡
- `montecarlo.py`: Euler completo (independiente) + semi-MC (método del artículo).
- Verificación con parámetros del artículo (§3, Fig 1: T=0.5, λ₁=0.01, λ₂=0.05):

  | K | Fórmula | Euler MC (err) | semi-MC (err) | rel. fórmula vs semi-MC |
  |---|---------|----------------|---------------|-------------------------|
  | 9.0 | 1.47686 | 1.47389 (0.0035) | 1.47686 (0.0000) | 0.000% |
  | 10.0 | 0.86629 | 0.86352 (0.0029) | 0.86629 (0.0000) | 0.000% |
  | 11.0 | 0.45841 | 0.45543 (0.0021) | 0.45841 (0.0001) | 0.001% |

  El semi-MC coincide con la fórmula a 0.000% (valida el paso de Elliott-Lian); el Euler
  completo coincide dentro de ~1 error estándar (el sesgo es la discretización, esperado).
  El error relativo máximo (<0.7% del artículo) se cumple holgadamente.
- Figura 02 (fórmula vs MC en 9 valores de S): error relativo máximo 0.0005%. Completa ✅.
- Optimización: cache de nodos Gauss-Legendre (leggauss es O(n²)) → suite de tests 22s→5s,
  y calibración/semi-MC mucho más rápidos.
