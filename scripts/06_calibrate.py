"""Calibración a datos de mercado y comparación de modelos (Etapa 6 / sección Calibración).

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

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsheston.calibration import (  # noqa: E402
    HESTON_SPEC,
    LINHE_SPEC,
    calibrate,
    evaluate_by_moneyness,
    evaluate_mse,
)
from rsheston.io_paths import DATA_PROCESSED, RESULTS_TABLES, ensure_dirs  # noqa: E402

MAXITER = 150
SEED = 12345


def main():
    ensure_dirs()
    insample = pd.read_csv(DATA_PROCESSED / "insample.csv")
    outsample = pd.read_csv(DATA_PROCESSED / "outofsample.csv")
    print(f"in-sample: {len(insample)} opciones | out-of-sample: {len(outsample)} opciones")

    specs = [HESTON_SPEC, LINHE_SPEC]
    calibs = {}
    for spec in specs:
        t0 = time.perf_counter()
        cal = calibrate(insample, spec, seed=SEED, maxiter=MAXITER)
        dt = time.perf_counter() - t0
        calibs[spec.name] = cal
        print(f"\n[{spec.name}] MSE in-sample={cal['mse']:.4f}  ({dt:.1f}s)")
        for k, v in cal["params"].items():
            print(f"    {k:9s} = {v:.4f}")

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


if __name__ == "__main__":
    main()
