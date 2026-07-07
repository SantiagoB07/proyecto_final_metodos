"""Análisis numérico del método de valoración (Etapa 4 / sección Discusión).

Estudia los aspectos numéricos que exige la rúbrica:
  (a) Convergencia frente al número de nodos de Gauss-Legendre.
  (b) Convergencia frente al truncamiento u_max, y la explosión de la cola (violación de Feller).
  (c) Comportamiento del integrando de Gil-Pelaez (decaimiento y oscilación).
  (d) Costo computacional (tiempo por precio).

Genera:
    results/figures/04_convergencia_nodos.png
    results/figures/04_truncamiento_y_cola.png
    results/figures/04_integrando.png
    results/tables/04_costo_computacional.csv
Sección del documento: Discusión (análisis numérico).
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import plt, setup_style  # noqa: E402

from rsheston.charfn import LinHeParams, make_heston_cf, make_linhe_cf  # noqa: E402
from rsheston.io_paths import RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs  # noqa: E402
from rsheston.pricing import DEFAULT_U_MAX, gil_pelaez_call  # noqa: E402

# Parámetros calibrados-realistas (lambda pequeño) y de la Fig. 1 (lambda que explota antes).
P_CALIB = LinHeParams(kappa=8.4, theta=0.20, sigma=0.75, rho=-0.63, v0=0.025,
                      lambda1=0.045, lambda2=0.036, lambda12=12.1, lambda21=4.9)
P_FIG1 = LinHeParams(kappa=10, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03,
                     lambda1=0.01, lambda2=0.05, lambda12=10, lambda21=20)
S, K, R, TAU, STATE = 10.0, 10.0, 0.05, 0.5, 1


def convergence_vs_nodes():
    """Error vs número de nodos, con truncamiento fijo seguro."""
    cf = make_linhe_cf(S=S, tau=TAU, r=R, params=P_CALIB, state=STATE)
    ref = gil_pelaez_call(cf, S, K, R, TAU, u_max=100, n_nodes=2048, adaptive=False)
    ns = [8, 16, 32, 48, 64, 96, 128, 192, 256]
    errs = [abs(gil_pelaez_call(cf, S, K, R, TAU, u_max=100, n_nodes=n, adaptive=False) - ref)
            for n in ns]
    fig, ax = plt.subplots()
    ax.semilogy(ns, np.maximum(errs, 1e-16), "o-")
    ax.set_xlabel("Número de nodos de Gauss-Legendre")
    ax.set_ylabel("Error absoluto vs referencia")
    ax.set_title("(a) Convergencia frente al número de nodos")
    fig.tight_layout()
    fig.savefig(RESULTS_FIGURES / "04_convergencia_nodos.png")
    print("nodos:", dict(zip(ns, [f"{e:.1e}" for e in errs])))


def truncation_and_tail():
    """Precio vs u_max (fijo): estable en la meseta y basura tras la explosión de la cola."""
    cf = make_linhe_cf(S=S, tau=TAU, r=R, params=P_FIG1, state=STATE)
    umaxes = np.arange(20, 320, 10)
    prices = [gil_pelaez_call(cf, S, K, R, TAU, u_max=u, n_nodes=512, adaptive=False)
              for u in umaxes]
    adaptive_price = gil_pelaez_call(cf, S, K, R, TAU)  # adaptativo

    fig, ax = plt.subplots()
    ax.plot(umaxes, prices, "o-", markersize=3, label="u_max fijo")
    ax.axhline(adaptive_price, color="C2", ls="--", label="truncamiento adaptativo")
    ax.set_xlabel("Truncamiento $u_{\\max}$ (fijo)")
    ax.set_ylabel("Precio de la call")
    ax.set_ylim(0.0, 2.0)
    ax.set_title("(b) Truncamiento: meseta estable y explosión de la cola (Feller)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_FIGURES / "04_truncamiento_y_cola.png")
    valid = [p for p in prices if 0 < p < S]
    print(f"truncamiento: precio adaptativo={adaptive_price:.6f}; "
          f"meseta ~[{min(valid):.6f}, {max(valid):.6f}]")


def integrand_behavior():
    """Magnitud del integrando de Gil-Pelaez vs frecuencia (decaimiento y cola)."""
    phi = np.linspace(0.1, 250, 1000)
    cf_c = make_linhe_cf(S=S, tau=TAU, r=R, params=P_CALIB, state=STATE)
    cf_f = make_linhe_cf(S=S, tau=TAU, r=R, params=P_FIG1, state=STATE)
    with np.errstate(over="ignore", invalid="ignore"):
        mag_c = np.abs(cf_c(phi))
        mag_f = np.abs(cf_f(phi))

    fig, ax = plt.subplots()
    ax.semilogy(phi, mag_c, label="$\\lambda$ calibrado (~0.045)")
    ax.semilogy(phi, mag_f, label="$\\lambda$ Fig. 1 (0.01, 0.05)")
    ax.set_xlabel("Frecuencia $\\phi$")
    ax.set_ylabel("$|m(\\phi)|$")
    ax.set_ylim(1e-30, 1e10)
    ax.set_title("(c) |cf|: decaimiento y explosión de la cola")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_FIGURES / "04_integrando.png")
    print("integrando: figura guardada")


def computational_cost():
    """Tiempo por precio para Heston y Lin-He (n_nodes por defecto)."""
    rows = []
    for name, cf in [
        ("Heston", make_heston_cf(S=S, tau=TAU, r=R, params=P_CALIB.heston())),
        ("Lin-He", make_linhe_cf(S=S, tau=TAU, r=R, params=P_CALIB, state=STATE)),
    ]:
        n_rep = 200
        t0 = time.perf_counter()
        for _ in range(n_rep):
            gil_pelaez_call(cf, S, K, R, TAU)
        dt_ms = (time.perf_counter() - t0) / n_rep * 1000
        rows.append((name, DEFAULT_U_MAX, dt_ms))
        print(f"costo {name}: {dt_ms:.3f} ms/precio")

    with open(RESULTS_TABLES / "04_costo_computacional.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["modelo", "u_max_cap", "ms_por_precio"])
        for r in rows:
            w.writerow([r[0], f"{r[1]:.0f}", f"{r[2]:.4f}"])


def main():
    ensure_dirs()
    setup_style()
    convergence_vs_nodes()
    truncation_and_tail()
    integrand_behavior()
    computational_cost()


if __name__ == "__main__":
    main()
