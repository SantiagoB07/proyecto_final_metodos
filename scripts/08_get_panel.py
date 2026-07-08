"""Descarga el panel histórico de 6 meses de opciones de SPY.

Replica el diseño del artículo: opciones de los MIÉRCOLES para estimación (in-sample) y de los
JUEVES para validación (out-of-sample), a lo largo de ~6 meses. Las cadenas EOD provienen de la
base pública de DoltHub (post-no-preference/options); el spot de SPY y la tasa (^IRX) provienen
de yfinance. El rendimiento por dividendos q se estima por paridad put-call por vencimiento.

Reproducibilidad: guarda el panel crudo combinado en data/raw/ (los precios históricos son
estables). Si ya existe, lo reutiliza salvo --force.

Genera:
    data/raw/panel_spy_<inicio>_<fin>.csv
    data/processed/panel_insample.csv (miércoles), panel_outofsample.csv (jueves)
    results/tables/08_resumen_panel.csv
Sección del documento: Datos.
"""

from __future__ import annotations

import csv
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rsheston.io_paths import DATA_PROCESSED, DATA_RAW, RESULTS_TABLES, ensure_dirs  # noqa: E402
from rsheston.market_data import clean_panel_date, fetch_dolthub_chain  # noqa: E402

# Ventana de ~6 meses (cobertura verificada de DoltHub para SPY).
START = date(2026, 1, 7)
END = date(2026, 7, 2)


def _weekdays(start, end, weekday):
    """Todas las fechas en [start, end] con el día de semana dado (0=lunes ... 3=jueves)."""
    d = start
    while d.weekday() != weekday:
        d += timedelta(days=1)
    out = []
    while d <= end:
        out.append(d)
        d += timedelta(days=7)
    return out


def _price_and_rate_maps():
    """Mapas fecha->spot SPY y fecha->tasa (^IRX/100) desde yfinance."""
    import yfinance as yf

    spy = yf.Ticker("SPY").history(start=str(START), end=str(END + timedelta(days=3)))
    irx = yf.Ticker("^IRX").history(start=str(START), end=str(END + timedelta(days=3)))
    spot = {d.date().isoformat(): float(v) for d, v in spy["Close"].items()}
    rate = {d.date().isoformat(): float(v) / 100.0 for d, v in irx["Close"].items()}
    return spot, rate


def _nearest(map_, dstr, tol=4):
    """Valor del mapa en la fecha, o el más cercano hacia atrás (hasta tol días; feriados)."""
    d = date.fromisoformat(dstr)
    for back in range(tol + 1):
        key = (d - timedelta(days=back)).isoformat()
        if key in map_:
            return map_[key]
    return None


def _build(dates, spot, rate):
    rows = []
    for d in dates:
        dstr = d.isoformat()
        raw = fetch_dolthub_chain(dstr, ticker="SPY")
        if raw is None:
            continue
        S = _nearest(spot, dstr)
        r = _nearest(rate, dstr)
        if S is None or r is None:
            continue
        rows.extend(clean_panel_date(raw, S, r))
        time.sleep(0.2)  # cortesía con la API
    return pd.DataFrame(rows)


def main(force=False):
    ensure_dirs()
    raw_path = DATA_RAW / f"panel_spy_{START}_{END}.csv"

    if raw_path.exists() and not force:
        print(f"Reutilizando panel crudo: {raw_path.name} (--force para redescargar)")
        panel = pd.read_csv(raw_path)
    else:
        print("Descargando spot/tasa (yfinance)...")
        spot, rate = _price_and_rate_maps()
        wednesdays = _weekdays(START, END, 2)
        thursdays = _weekdays(START, END, 3)
        print(f"Miércoles: {len(wednesdays)} | Jueves: {len(thursdays)}. Descargando cadenas...")
        insample = _build(wednesdays, spot, rate)
        insample["session"] = "in"
        outsample = _build(thursdays, spot, rate)
        outsample["session"] = "out"
        panel = pd.concat([insample, outsample], ignore_index=True)
        panel.to_csv(raw_path, index=False)
        print(f"Panel crudo guardado: {raw_path.name} ({len(panel)} filas)")

    insample = panel[panel["session"] == "in"].drop(columns="session")
    outsample = panel[panel["session"] == "out"].drop(columns="session")
    insample.to_csv(DATA_PROCESSED / "panel_insample.csv", index=False)
    outsample.to_csv(DATA_PROCESSED / "panel_outofsample.csv", index=False)

    n_wed = insample["date"].nunique()
    n_thu = outsample["date"].nunique()
    print(f"in-sample (miércoles): {len(insample)} opciones en {n_wed} fechas")
    print(f"out-of-sample (jueves): {len(outsample)} opciones en {n_thu} fechas")

    with open(RESULTS_TABLES / "08_resumen_panel.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["metrica", "valor"])
        w.writerow(["fecha_inicio", insample["date"].min()])
        w.writerow(["fecha_fin", insample["date"].max()])
        w.writerow(["n_fechas_miercoles", n_wed])
        w.writerow(["n_fechas_jueves", n_thu])
        w.writerow(["n_opciones_in", len(insample)])
        w.writerow(["n_opciones_out", len(outsample)])
        w.writerow(["opciones_por_fecha_in", round(len(insample) / max(n_wed, 1), 1)])
        w.writerow(["spot_min", round(panel["S"].min(), 2)])
        w.writerow(["spot_max", round(panel["S"].max(), 2)])
    print("Resumen del panel guardado: 08_resumen_panel.csv")


if __name__ == "__main__":
    main(force="--force" in sys.argv)
