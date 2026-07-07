"""Verificación 3: reproducción de las Figs. 2 y 3 del artículo.

- Fig. 2: precio del modelo vs precio de Heston al variar el parámetro de escala z de
  lambda1, lambda2 (muestra la coincidencia exacta en z=0 y la divergencia al crecer z).
- Fig. 3: precio del modelo y de Heston vs tiempo al vencimiento (ambos crecientes en tau).

Genera:
    results/figures/03_precio_vs_z.png
    results/figures/03_precio_vs_vencimiento.png
Sección del documento: Implementación, verificación y calibración.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import plt, setup_style  # noqa: E402

from rsheston.charfn import LinHeParams, make_heston_cf, make_linhe_cf  # noqa: E402
from rsheston.io_paths import RESULTS_FIGURES, ensure_dirs  # noqa: E402
from rsheston.pricing import gil_pelaez_call  # noqa: E402

BASE = dict(kappa=10, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03, lambda12=10, lambda21=20)
S, K, R, STATE = 10.0, 10.0, 0.05, 1


def fig_price_vs_z():
    """Fig. 2: precio vs parámetro de escala z (lambda1=0.3z, lambda2=0.2z), tau=0.5."""
    tau = 0.5
    z_values = np.linspace(0.0, 1.0, 21)
    linhe, heston = [], []
    for z in z_values:
        p = LinHeParams(lambda1=0.3 * z, lambda2=0.2 * z, **BASE)
        linhe.append(gil_pelaez_call(make_linhe_cf(S=S, tau=tau, r=R, params=p, state=STATE), S, K, R, tau))
        heston.append(gil_pelaez_call(make_heston_cf(S=S, tau=tau, r=R, params=p.heston()), S, K, R, tau))

    fig, ax = plt.subplots()
    ax.plot(z_values, linhe, "o-", label="Modelo Lin & He", markersize=3)
    ax.plot(z_values, heston, "--", label="Modelo Heston")
    ax.set_xlabel("Parámetro de escala $z$")
    ax.set_ylabel("Precio de la call")
    ax.set_title("Fig. 2: precio vs escala de la vol. de vol. de régimen")
    ax.legend()
    fig.tight_layout()
    out = RESULTS_FIGURES / "03_precio_vs_z.png"
    fig.savefig(out)
    print(f"Guardada: {out.name}")


def fig_price_vs_maturity():
    """Fig. 3: precio vs tiempo al vencimiento (lambda1=0.3, lambda2=0.2)."""
    p = LinHeParams(lambda1=0.3, lambda2=0.2, **BASE)
    taus = np.linspace(0.1, 1.0, 19)
    linhe, heston = [], []
    for tau in taus:
        linhe.append(gil_pelaez_call(make_linhe_cf(S=S, tau=tau, r=R, params=p, state=STATE), S, K, R, tau))
        heston.append(gil_pelaez_call(make_heston_cf(S=S, tau=tau, r=R, params=p.heston()), S, K, R, tau))

    fig, ax = plt.subplots()
    ax.plot(taus, linhe, "-", label="Modelo Lin & He")
    ax.plot(taus, heston, "--", label="Modelo Heston")
    ax.set_xlabel("Tiempo al vencimiento $\\tau$ (años)")
    ax.set_ylabel("Precio de la call")
    ax.set_title("Fig. 3: precio vs tiempo al vencimiento")
    ax.legend()
    fig.tight_layout()
    out = RESULTS_FIGURES / "03_precio_vs_vencimiento.png"
    fig.savefig(out)
    print(f"Guardada: {out.name}")


def main():
    ensure_dirs()
    setup_style()
    fig_price_vs_z()
    fig_price_vs_maturity()


if __name__ == "__main__":
    main()
