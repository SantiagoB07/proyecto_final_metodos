"""Verificación 2: fórmula cerrada vs simulación Monte Carlo (reproduce la Fig. 1).

Compara los precios de la fórmula cerrada contra la semi-simulación Monte Carlo del artículo
y contra una simulación de Euler completa e independiente, a lo largo de un rango de precios
del subyacente. Reporta el error relativo (el artículo exige un máximo < 0.7%).

Genera:
    results/figures/02_formula_vs_montecarlo.png
    results/tables/02_errores_montecarlo.csv
Sección del documento: Implementación, verificación y calibración.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import plt, setup_style  # noqa: E402

from rsheston.charfn import LinHeParams, make_linhe_cf  # noqa: E402
from rsheston.io_paths import RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs  # noqa: E402
from rsheston.montecarlo import mc_euler_call_price, semi_mc_call_price  # noqa: E402
from rsheston.pricing import gil_pelaez_call  # noqa: E402

# Parámetros de la Fig. 1 del artículo.
PARAMS = LinHeParams(
    kappa=10, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03,
    lambda1=0.01, lambda2=0.05, lambda12=10, lambda21=20,
)
R, TAU, K, STATE = 0.05, 0.5, 10.0, 1
S_GRID = np.linspace(8.0, 12.0, 9)
N_SEMI = 3000  # el semi-MC tiene varianza casi nula, pocos caminos bastan
N_EULER = 200_000


def main():
    ensure_dirs()
    setup_style()

    rows = []
    formula, semi, euler = [], [], []
    print(f"{'S':>5} {'formula':>10} {'semi-MC':>10} {'euler-MC':>10} {'rel.err(%)':>10}")
    for S in S_GRID:
        cf = make_linhe_cf(S=S, tau=TAU, r=R, params=PARAMS, state=STATE)
        f_price = gil_pelaez_call(cf, S, K, R, TAU)
        s_price, s_err = semi_mc_call_price(S, K, R, TAU, PARAMS, state=STATE, n_paths=N_SEMI)
        e_price = mc_euler_call_price(S, K, R, TAU, PARAMS, state=STATE, n_paths=N_EULER)
        rel = abs(f_price - s_price) / f_price * 100 if f_price > 1e-8 else 0.0
        formula.append(f_price)
        semi.append(s_price)
        euler.append(e_price)
        rows.append((S, f_price, s_price, s_err, e_price, rel))
        print(f"{S:5.1f} {f_price:10.5f} {s_price:10.5f} {e_price:10.5f} {rel:10.4f}")

    max_rel = max(r[5] for r in rows)
    print(f"\nError relativo máximo (fórmula vs semi-MC): {max_rel:.4f}%  (artículo: < 0.7%)")

    # Tabla CSV.
    table_path = RESULTS_TABLES / "02_errores_montecarlo.csv"
    with open(table_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["S", "formula", "semi_mc", "semi_mc_stderr", "euler_mc", "rel_err_pct"])
        for row in rows:
            w.writerow([f"{x:.6f}" for x in row])

    # Figura: precios y error relativo.
    formula, semi, euler = map(np.array, (formula, semi, euler))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(S_GRID, formula, "-", label="Fórmula cerrada")
    ax1.plot(S_GRID, semi, "s", label="semi-Monte-Carlo", markersize=4)
    ax1.plot(S_GRID, euler, "x", label="Euler-Monte-Carlo", markersize=6)
    ax1.set_xlabel("Precio del subyacente $S$")
    ax1.set_ylabel("Precio de la call")
    ax1.set_title("(a) Precio: fórmula vs Monte Carlo")
    ax1.legend()

    rel_err = np.abs(formula - semi) / formula * 100
    ax2.plot(S_GRID, rel_err, "o-", color="C3")
    ax2.axhline(0.7, color="gray", ls="--", label="cota del artículo (0.7%)")
    ax2.set_xlabel("Precio del subyacente $S$")
    ax2.set_ylabel("Error relativo (%)")
    ax2.set_title("(b) Error relativo fórmula vs semi-MC")
    ax2.legend()
    fig.tight_layout()
    out = RESULTS_FIGURES / "02_formula_vs_montecarlo.png"
    fig.savefig(out)
    print(f"Figura guardada: {out.name}; tabla: {table_path.name}")


if __name__ == "__main__":
    main()
