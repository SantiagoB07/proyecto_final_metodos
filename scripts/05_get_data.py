"""Descarga y limpieza de datos de mercado (Etapa 5 / sección Datos).

Descarga las opciones (calls y puts) de SPY (S&P 500) con yfinance, guarda el snapshot crudo
con fecha en data/raw/, aplica los filtros del artículo (estimando el rendimiento por dividendos
q por vencimiento vía paridad put-call) y guarda los conjuntos limpios en data/processed/.
Separa in-sample y out-of-sample alternando strikes por vencimiento. Ver decisiones D7, D8.

Reproducibilidad: si ya existe un snapshot crudo del día, lo reutiliza en vez de volver a
llamar a la API (usar --force para redescargar).

Genera:
    data/raw/spy_options_<fecha>.csv   (snapshot crudo, versionado)
    data/processed/insample.csv, data/processed/outofsample.csv
    results/tables/05_resumen_datos.csv
Sección del documento: Datos.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import plt, setup_style  # noqa: E402

from rsheston.io_paths import DATA_RAW, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs  # noqa: E402
from rsheston.market_data import (  # noqa: E402
    clean_option_data,
    download_option_chain,
    moneyness_bucket,
    save_processed,
)
from rsheston.pricing import implied_vol  # noqa: E402


def main(force=False):
    ensure_dirs()

    existing = sorted(DATA_RAW.glob("spy_options_*.csv"))
    if existing and not force:
        raw = existing[-1]
        print(f"Reutilizando snapshot existente: {raw.name} (usar --force para redescargar)")
    else:
        raw = download_option_chain(ticker="SPY", rate_ticker="^IRX")

    clean = clean_option_data(raw)
    print(f"Contratos tras filtros del artículo: {len(clean)}")
    if len(clean) == 0:
        print("ADVERTENCIA: 0 contratos tras filtros. Revisar el snapshot crudo.")
        return

    clean["bucket"] = clean["moneyness"].apply(moneyness_bucket)

    # Separación in/out-of-sample: por cada vencimiento, alternar strikes (par/impar por orden).
    clean = clean.sort_values(["days", "K"]).reset_index(drop=True)
    clean["idx_in_expiry"] = clean.groupby("days").cumcount()
    insample = clean[clean["idx_in_expiry"] % 2 == 0].drop(columns="idx_in_expiry")
    outsample = clean[clean["idx_in_expiry"] % 2 == 1].drop(columns="idx_in_expiry")

    p_in = save_processed(insample, "insample")
    p_out = save_processed(outsample, "outofsample")
    print(f"in-sample: {len(insample)} -> {p_in.name}")
    print(f"out-of-sample: {len(outsample)} -> {p_out.name}")

    # Tabla resumen para la sección de datos.
    summary = RESULTS_TABLES / "05_resumen_datos.csv"
    with open(summary, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metrica", "valor"])
        w.writerow(["spot_S", f"{clean['S'].iloc[0]:.2f}"])
        w.writerow(["tasa_r", f"{clean['r'].iloc[0]:.4f}"])
        w.writerow(["q_min", f"{clean['q'].min():.4f}"])
        w.writerow(["q_max", f"{clean['q'].max():.4f}"])
        w.writerow(["n_contratos", len(clean)])
        w.writerow(["n_vencimientos", clean["days"].nunique()])
        w.writerow(["dias_min", int(clean["days"].min())])
        w.writerow(["dias_max", int(clean["days"].max())])
        w.writerow(["strikes_min", f"{clean['K'].min():.0f}"])
        w.writerow(["strikes_max", f"{clean['K'].max():.0f}"])
        for b in ["OTM", "ATM", "ITM"]:
            w.writerow([f"n_{b}", int((clean["bucket"] == b).sum())])
    print(f"Resumen guardado: {summary.name}")

    # Figura: sonrisa/superficie de volatilidad implícita del conjunto limpio.
    setup_style()
    clean["iv"] = clean.apply(
        lambda x: implied_vol(x.price, x.S, x.K, x.r, x.tau, q=x.q, is_call=True), axis=1
    )
    fig, ax = plt.subplots()
    for days, grp in clean.groupby("days"):
        g = grp.dropna(subset=["iv"]).sort_values("K")
        if len(g) > 2:
            ax.plot(g["K"] / g["S"], g["iv"], "o-", markersize=3, label=f"{int(days)} días")
    ax.set_xlabel("Moneyness $K/S$")
    ax.set_ylabel("Volatilidad implícita")
    ax.set_title("Superficie de volatilidad implícita (SPY, datos limpios)")
    ax.legend(title="Vencimiento", fontsize=8)
    fig.tight_layout()
    out_fig = RESULTS_FIGURES / "05_sonrisa_volatilidad.png"
    fig.savefig(out_fig)
    print(f"Figura de sonrisa guardada: {out_fig.name}")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
