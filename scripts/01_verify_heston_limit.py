"""Verificación 1: degeneración del modelo Lin & He al modelo de Heston.

Reproduce el argumento de la Fig. 2 del artículo: al escalar lambda1, lambda2 por z en [0, 1],
el precio del modelo se acerca al de Heston, y coincide EXACTAMENTE cuando z = 0.

Genera: results/figures/01_degeneracion_heston.png
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


def main():
    ensure_dirs()
    setup_style()

    # Parámetros de la Fig. 2 del artículo.
    S, K, r, tau, state = 10.0, 10.0, 0.05, 0.5, 1
    base_l1, base_l2 = 0.3, 0.2

    z_values = np.linspace(0.0, 1.0, 21)
    linhe_prices, heston_prices = [], []
    for z in z_values:
        p = LinHeParams(
            kappa=10, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03,
            lambda1=base_l1 * z, lambda2=base_l2 * z, lambda12=10, lambda21=20,
        )
        cf_l = make_linhe_cf(S=S, tau=tau, r=r, params=p, state=state)
        cf_h = make_heston_cf(S=S, tau=tau, r=r, params=p.heston())
        linhe_prices.append(gil_pelaez_call(cf_l, S, K, r, tau))
        heston_prices.append(gil_pelaez_call(cf_h, S, K, r, tau))

    linhe_prices = np.array(linhe_prices)
    heston_prices = np.array(heston_prices)
    err_at_zero = abs(linhe_prices[0] - heston_prices[0])
    print(f"Precio Lin-He en z=0: {linhe_prices[0]:.6f}")
    print(f"Precio Heston:        {heston_prices[0]:.6f}")
    print(f"Diferencia en z=0:    {err_at_zero:.2e}  (debe ser ~0)")

    fig, ax = plt.subplots()
    ax.plot(z_values, linhe_prices, "o-", label="Modelo Lin & He", markersize=3)
    ax.axhline(heston_prices[0], color="C1", ls="--", label="Modelo Heston")
    ax.set_xlabel("Parámetro de escala $z$ ($\\lambda_1=0.3z,\\ \\lambda_2=0.2z$)")
    ax.set_ylabel("Precio de la call europea")
    ax.set_title("Degeneración a Heston cuando $z \\to 0$")
    ax.legend()
    fig.tight_layout()
    out = RESULTS_FIGURES / "01_degeneracion_heston.png"
    fig.savefig(out)
    print(f"Figura guardada: {out.relative_to(RESULTS_FIGURES.parents[1])}")


if __name__ == "__main__":
    main()
