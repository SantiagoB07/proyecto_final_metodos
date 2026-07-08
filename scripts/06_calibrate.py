"""Calibración a datos de mercado y comparación de modelos.

Calibra el modelo de Heston y el de Lin & He a los datos in-sample (minimizando el MSE en
dólares con dual_annealing), evalúa el ajuste in-sample y out-of-sample, y desglosa el error
por moneyness (OTM/ATM/ITM). Produce tablas análogas a las Tablas 1-3 del artículo.

Reproducibilidad: semilla fija; se reportan optimizador (dual_annealing), cotas y semilla.

Genera:
    results/tables/06_parametros.csv        (análogo Tabla 1)
    results/tables/06_errores.csv           (análogo Tabla 2: in/out-of-sample)
    results/tables/06_errores_moneyness.csv (análogo Tabla 3)
Sección del documento: Implementación, verificación y calibración.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import plt, setup_style  # noqa: E402

from rsheston.calibration import (  # noqa: E402
    HESTON_SPEC,
    LINHE_SPEC,
    calibrate,
    evaluate_by_moneyness,
    evaluate_mse,
    model_prices,
)
from rsheston.io_paths import (  # noqa: E402
    DATA_PROCESSED,
    RESULTS_FIGURES,
    RESULTS_TABLES,
    ensure_dirs,
)

MAXITER = 150
SEED = 12345


def main():
    ensure_dirs()
    insample = pd.read_csv(DATA_PROCESSED / "insample.csv")
    outsample = pd.read_csv(DATA_PROCESSED / "outofsample.csv")
    print(f"in-sample: {len(insample)} opciones | out-of-sample: {len(outsample)} opciones")

    specs = [HESTON_SPEC, LINHE_SPEC]
    calibs = {}

    # 1) Heston.
    t0 = time.perf_counter()
    calibs["Heston"] = calibrate(insample, HESTON_SPEC, seed=SEED, maxiter=MAXITER)
    print(f"\n[Heston] MSE in-sample={calibs['Heston']['mse']:.4f}  "
          f"({time.perf_counter() - t0:.1f}s)")
    for k, v in calibs["Heston"]["params"].items():
        print(f"    {k:9s} = {v:.4f}")

    # 2) Lin-He: warm-start desde Heston con lambda~0 (garantiza MSE <= Heston por anidamiento).
    hp = calibs["Heston"]["params"]
    embedded = [hp["kappa"], hp["theta"], hp["sigma"], hp["rho"], hp["v0"], 0.0, 0.0, 5.0, 5.0]
    x0 = [hp["kappa"], hp["theta"], hp["sigma"], hp["rho"], hp["v0"], 0.02, 0.02, 5.0, 5.0]
    t0 = time.perf_counter()
    calibs["Lin-He"] = calibrate(
        insample, LINHE_SPEC, seed=SEED, maxiter=MAXITER, x0=x0, extra_starts=[embedded],
    )
    print(f"\n[Lin-He] MSE in-sample={calibs['Lin-He']['mse']:.4f}  "
          f"({time.perf_counter() - t0:.1f}s)")
    for k, v in calibs["Lin-He"]["params"].items():
        print(f"    {k:9s} = {v:.4f}")

    # Verificación de anidamiento: Lin-He debe ajustar al menos tan bien como Heston.
    if calibs["Lin-He"]["mse"] > calibs["Heston"]["mse"] + 1e-6:
        print("  ADVERTENCIA: MSE(Lin-He) > MSE(Heston); el anidamiento no se cumplió.")
    else:
        print(f"  OK anidamiento: MSE(Lin-He)={calibs['Lin-He']['mse']:.4f} "
              f"<= MSE(Heston)={calibs['Heston']['mse']:.4f}")

    # Tabla 1: parámetros estimados.
    all_names = LINHE_SPEC.param_names
    with open(RESULTS_TABLES / "06_parametros.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parametro"] + [s.name for s in specs])
        for name in all_names:
            w.writerow([name] + [f"{calibs[s.name]['params'].get(name, ''):.4f}"
                                 if name in calibs[s.name]["params"] else ""
                                 for s in specs])

    # Tabla 2: errores in-sample y out-of-sample.
    with open(RESULTS_TABLES / "06_errores.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["modelo", "in_sample_mse", "out_of_sample_mse"])
        rows2 = []
        for spec in specs:
            th = calibs[spec.name]["params"]
            in_mse = evaluate_mse(th, insample, spec)
            out_mse = evaluate_mse(th, outsample, spec)
            rows2.append((spec.name, in_mse, out_mse))
            w.writerow([spec.name, f"{in_mse:.4f}", f"{out_mse:.4f}"])
    print("\nErrores (in / out-of-sample):")
    for name, i, o in rows2:
        print(f"    {name:8s}  in={i:.4f}  out={o:.4f}")

    # Tabla 3: errores out-of-sample por moneyness.
    with open(RESULTS_TABLES / "06_errores_moneyness.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["modelo", "OTM", "ATM", "ITM"])
        for spec in specs:
            th = calibs[spec.name]["params"]
            by = evaluate_by_moneyness(th, outsample, spec)
            w.writerow([spec.name] + [f"{by.get(b, float('nan')):.4f}" for b in ["OTM", "ATM", "ITM"]])

    print(f"\nTablas guardadas en {RESULTS_TABLES.name}/ (06_parametros, 06_errores, 06_errores_moneyness)")

    # Figura de ajuste: precios de mercado vs modelo para el vencimiento más corto (in-sample).
    setup_style()
    d0 = insample["days"].min()
    sub = insample[insample["days"] == d0].sort_values("K").reset_index(drop=True)
    fig, ax = plt.subplots()
    ax.plot(sub["K"], sub["price"], "ko", label="Mercado", markersize=4)
    for spec, style in [(HESTON_SPEC, "C0-"), (LINHE_SPEC, "C1--")]:
        pm = model_prices(calibs[spec.name]["params"], sub, spec)
        ax.plot(sub["K"], pm, style, label=f"{spec.name}")
    ax.set_xlabel("Strike $K$")
    ax.set_ylabel("Precio de la call")
    ax.set_title(f"Ajuste de la calibración (vencimiento {int(d0)} días, in-sample)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_FIGURES / "06_ajuste_calibracion.png")
    print("Figura de ajuste guardada: 06_ajuste_calibracion.png")


if __name__ == "__main__":
    main()
