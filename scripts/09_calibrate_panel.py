"""Calibración de panel (6 meses) — replica el diseño del artículo (Etapa 6-panel).

Para cada MIÉRCOLES: calibra Heston y Lin & He al corte transversal de ese día (in-sample) y
evalúa fuera de muestra en el JUEVES siguiente. Se reportan resultados promediados sobre las
fechas (Tabla 1: parámetros medios; Tabla 2: MSE medio in/out; Tabla 3: MSE medio por moneyness),
análogos a las Tablas 1-3 del artículo. Las fechas se calibran en paralelo (multiprocessing).

Reproducibilidad: semilla fija por fecha; optimizador dual_annealing + pulido local.

Genera:
    results/tables/09_parametros_panel.csv, 09_errores_panel.csv, 09_moneyness_panel.csv
    results/figures/09_mse_por_fecha.png, 09_lambda_por_fecha.png
Sección del documento: Implementación, verificación y calibración (estudio de panel).
"""

from __future__ import annotations

import csv
import sys
from concurrent.futures import ProcessPoolExecutor
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
)
from rsheston.io_paths import DATA_PROCESSED, RESULTS_FIGURES, RESULTS_TABLES, ensure_dirs  # noqa: E402

MAXITER = 80  # por fecha; menor que el caso de un solo corte, pues promediamos sobre 25 fechas
SEED = 12345


def _calibrate_one(args):
    """Calibra ambos modelos en una fecha (in-sample) y evalúa out-of-sample. Ejecutado por worker."""
    date, ins_df, out_df = args
    ins_df = ins_df.reset_index(drop=True)

    heston = calibrate(ins_df, HESTON_SPEC, seed=SEED, maxiter=MAXITER)
    hp = heston["params"]
    x0 = [hp["kappa"], hp["theta"], hp["sigma"], hp["rho"], hp["v0"], 0.02, 0.02, 5.0, 5.0]
    embedded = [hp["kappa"], hp["theta"], hp["sigma"], hp["rho"], hp["v0"], 0.0, 0.0, 5.0, 5.0]
    linhe = calibrate(ins_df, LINHE_SPEC, seed=SEED, maxiter=MAXITER, x0=x0, extra_starts=[embedded])

    res = {"date": date, "n_in": len(ins_df),
           "heston_in": heston["mse"], "linhe_in": linhe["mse"],
           "heston_params": heston["params"], "linhe_params": linhe["params"]}
    if out_df is not None and len(out_df) > 0:
        out_df = out_df.reset_index(drop=True)
        res["heston_out"] = evaluate_mse(heston["params"], out_df, HESTON_SPEC)
        res["linhe_out"] = evaluate_mse(linhe["params"], out_df, LINHE_SPEC)
        res["heston_mny"] = evaluate_by_moneyness(heston["params"], out_df, HESTON_SPEC)
        res["linhe_mny"] = evaluate_by_moneyness(linhe["params"], out_df, LINHE_SPEC)
    return res


def _pair_thursday(wed_date, out_dates):
    """Jueves de la misma semana (miércoles + 1 día) si existe en el panel out-of-sample."""
    thu = (pd.to_datetime(wed_date) + pd.Timedelta(days=1)).date().isoformat()
    return thu if thu in out_dates else None


def main():
    ensure_dirs()
    ins = pd.read_csv(DATA_PROCESSED / "panel_insample.csv")
    out = pd.read_csv(DATA_PROCESSED / "panel_outofsample.csv")
    out_dates = set(out["date"].unique())

    tasks = []
    for date, grp in ins.groupby("date"):
        thu = _pair_thursday(date, out_dates)
        out_df = out[out["date"] == thu] if thu else None
        tasks.append((date, grp.copy(), out_df.copy() if out_df is not None else None))

    print(f"Calibrando {len(tasks)} fechas (miércoles) en paralelo...")
    with ProcessPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(_calibrate_one, tasks))
    results.sort(key=lambda r: r["date"])

    # Agregados (promediados sobre fechas), como los "daily-averaged" del artículo.
    def avg(key):
        vals = [r[key] for r in results if key in r]
        return float(np.mean(vals)) if vals else float("nan")

    hp_avg = {p: np.mean([r["heston_params"][p] for r in results]) for p in HESTON_SPEC.param_names}
    lp_avg = {p: np.mean([r["linhe_params"][p] for r in results]) for p in LINHE_SPEC.param_names}

    print("\n== Resultados promediados sobre fechas ==")
    print(f"MSE in-sample:  Heston={avg('heston_in'):.4f}  Lin-He={avg('linhe_in'):.4f}")
    print(f"MSE out-sample: Heston={avg('heston_out'):.4f}  Lin-He={avg('linhe_out'):.4f}")
    improved = np.mean([r["linhe_in"] < r["heston_in"] - 1e-9 for r in results]) * 100
    print(f"Fechas donde Lin-He mejora estrictamente in-sample: {improved:.0f}%")

    # Detalle por fecha (diagnóstico y para estadísticas robustas).
    with open(RESULTS_TABLES / "09_por_fecha.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "n_in", "heston_in", "linhe_in", "heston_out", "linhe_out"])
        for r in results:
            w.writerow([r["date"], r["n_in"], f"{r['heston_in']:.4f}", f"{r['linhe_in']:.4f}",
                        f"{r.get('heston_out', float('nan')):.4f}",
                        f"{r.get('linhe_out', float('nan')):.4f}"])
    # Estadísticas robustas (mediana) además de la media, por si hay fechas atípicas.
    h_out = [r["heston_out"] for r in results if "heston_out" in r]
    l_out = [r["linhe_out"] for r in results if "linhe_out" in r]
    print(f"MSE out-sample (mediana): Heston={np.median(h_out):.4f}  Lin-He={np.median(l_out):.4f}")

    # Tabla 1: parámetros medios.
    with open(RESULTS_TABLES / "09_parametros_panel.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parametro", "Heston", "Lin-He"])
        for p in LINHE_SPEC.param_names:
            w.writerow([p, f"{hp_avg[p]:.4f}" if p in hp_avg else "", f"{lp_avg[p]:.4f}"])

    # Tabla 2: MSE in/out (media y mediana; la mediana es robusta a fechas con saltos overnight).
    def med(key):
        vals = [r[key] for r in results if key in r]
        return float(np.median(vals)) if vals else float("nan")

    with open(RESULTS_TABLES / "09_errores_panel.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["modelo", "in_mse_medio", "out_mse_medio", "out_mse_mediana"])
        w.writerow(["Heston", f"{avg('heston_in'):.4f}", f"{avg('heston_out'):.4f}", f"{med('heston_out'):.4f}"])
        w.writerow(["Lin-He", f"{avg('linhe_in'):.4f}", f"{avg('linhe_out'):.4f}", f"{med('linhe_out'):.4f}"])

    # Tabla 3: MSE out-of-sample por moneyness (MEDIANA sobre fechas, robusta a atípicos).
    def avg_mny(model_key, bucket):
        vals = [r[model_key][bucket] for r in results if model_key in r and bucket in r[model_key]]
        return float(np.median(vals)) if vals else float("nan")

    with open(RESULTS_TABLES / "09_moneyness_panel.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["modelo", "OTM", "ATM", "ITM"])
        for name, key in [("Heston", "heston_mny"), ("Lin-He", "linhe_mny")]:
            w.writerow([name] + [f"{avg_mny(key, b):.4f}" for b in ["OTM", "ATM", "ITM"]])

    # Figuras: MSE in-sample por fecha y lambda de régimen por fecha.
    setup_style()
    dates = [r["date"] for r in results]
    x = range(len(dates))
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(x, [r["heston_in"] for r in results], "o-", label="Heston", markersize=3)
    ax.plot(x, [r["linhe_in"] for r in results], "s--", label="Lin & He", markersize=3)
    ax.set_xticks(list(x)[::3]); ax.set_xticklabels([dates[i] for i in list(x)[::3]], rotation=45, fontsize=7)
    ax.set_ylabel("MSE in-sample"); ax.set_title("MSE in-sample por fecha (miércoles)"); ax.legend()
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "09_mse_por_fecha.png")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(x, [r["linhe_params"]["lambda1"] for r in results], "o-", label="$\\lambda_1$", markersize=3)
    ax.plot(x, [r["linhe_params"]["lambda2"] for r in results], "s-", label="$\\lambda_2$", markersize=3)
    ax.set_xticks(list(x)[::3]); ax.set_xticklabels([dates[i] for i in list(x)[::3]], rotation=45, fontsize=7)
    ax.set_ylabel("Nivel de vol-of-vol de régimen"); ax.set_title("$\\lambda_1,\\lambda_2$ calibrados por fecha"); ax.legend()
    fig.tight_layout(); fig.savefig(RESULTS_FIGURES / "09_lambda_por_fecha.png")

    print("\nTablas y figuras del panel guardadas (09_*).")


if __name__ == "__main__":
    main()
