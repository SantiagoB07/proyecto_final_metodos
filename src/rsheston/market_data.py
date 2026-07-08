"""Descarga y limpieza de datos de mercado (opciones del S&P 500).

Fuente: yfinance. Por defecto ``SPY`` (ETF del S&P 500), cuyas opciones tienen liquidez amplia
en todo el rango de moneyness; el código también soporta ``^SPX`` (opciones europeas
del índice) pasando ``ticker="^SPX"``. Tasa libre de riesgo: ``^IRX`` (T-Bill 13 semanas),
análogo al T-Bill de 3 meses del artículo.

Dividendos: el rendimiento por dividendos ``q`` se estima por vencimiento a partir de
la paridad put-call (forward implícito), sin necesidad de datos externos de dividendos.

Reproducibilidad: yfinance es una API en vivo. ``download_option_chain`` guarda el snapshot
crudo con fecha en ``data/raw/``; el resto del pipeline lee de ese archivo.

Filtros del artículo (Sección 4.1):
    - vencimiento entre 30 y 90 días,
    - moneyness |S - K| / K < 10%,
    - precio de mercado = punto medio bid-ask.
"""

from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from .io_paths import DATA_PROCESSED, DATA_RAW, ensure_dirs


def download_option_chain(ticker="SPY", rate_ticker="^IRX", asof=None):
    """Descarga calls y puts y el spot, y guarda el snapshot crudo con fecha.

    Guarda calls y puts (columna ``type`` en {"C","P"}); las puts se usan para estimar el
    forward/dividendos por paridad put-call.

    Returns:
        Ruta del CSV crudo guardado en data/raw/.
    """
    import yfinance as yf

    ensure_dirs()
    asof = asof or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    tk = yf.Ticker(ticker)
    spot = float(tk.fast_info["lastPrice"])
    rate = float(yf.Ticker(rate_ticker).fast_info["lastPrice"]) / 100.0  # ^IRX en %

    frames = []
    for expiry in tk.options:
        chain = tk.option_chain(expiry)
        for kind, frame in [("C", chain.calls), ("P", chain.puts)]:
            f = frame.copy()
            f["type"] = kind
            f["expiry"] = expiry
            frames.append(f)
    allopt = pd.concat(frames, ignore_index=True)
    allopt["spot"] = spot
    allopt["rate"] = rate
    allopt["asof"] = asof
    allopt["underlying"] = ticker

    out = DATA_RAW / f"{ticker.strip('^').lower()}_options_{asof}.csv"
    allopt.to_csv(out, index=False)
    n_c = int((allopt["type"] == "C").sum())
    n_p = int((allopt["type"] == "P").sum())
    print(f"Snapshot crudo guardado: {out.name}  (spot={spot:.2f}, rate={rate:.4%}, "
          f"{n_c} calls, {n_p} puts, {len(tk.options)} vencimientos)")
    return out


def _mid_price(frame):
    """Precio medio bid-ask cuando ambos existen; si no, lastPrice."""
    mid = 0.5 * (frame["bid"] + frame["ask"])
    return np.where((frame["bid"] > 0) & (frame["ask"] > 0), mid, frame["lastPrice"])


def estimate_forward_q(calls_e, puts_e, S, r, tau):
    """Estima el forward implícito y el rendimiento por dividendos q para un vencimiento.

    Usa la paridad put-call C - P = e^{-r tau}(F - K) sobre los strikes con call y put válidas
    cercanos a ATM: el forward se obtiene del strike donde |C - P| es mínimo (ATM), como
    F = K + e^{r tau}(C - P). Luego q = r - ln(F / S) / tau.

    Returns:
        (forward, q) o (None, None) si no hay pares válidos.
    """
    merged = calls_e.merge(puts_e, on="strike", suffixes=("_c", "_p"))
    valid = merged[
        (merged["bid_c"] > 0) & (merged["ask_c"] > 0)
        & (merged["bid_p"] > 0) & (merged["ask_p"] > 0)
    ].copy()
    if len(valid) == 0:
        return None, None
    c_mid = np.where((valid["bid_c"] > 0) & (valid["ask_c"] > 0),
                     0.5 * (valid["bid_c"] + valid["ask_c"]), valid["lastPrice_c"])
    p_mid = np.where((valid["bid_p"] > 0) & (valid["ask_p"] > 0),
                     0.5 * (valid["bid_p"] + valid["ask_p"]), valid["lastPrice_p"])
    diff = c_mid - p_mid
    # Strike ATM: donde |C - P| es mínimo.
    i = int(np.argmin(np.abs(diff)))
    K_atm = float(valid["strike"].iloc[i])
    forward = K_atm + np.exp(r * tau) * diff[i]
    q = r - np.log(forward / S) / tau
    return float(forward), float(q)


def clean_option_data(
    raw_csv, min_days=30, max_days=90, max_abs_moneyness=0.10, min_price=0.05,
):
    """Aplica los filtros del artículo y estima q por vencimiento.

    Returns:
        DataFrame con columnas: S, K, tau, r, q, price, expiry, days, moneyness.
    """
    df = pd.read_csv(raw_csv)
    asof = pd.to_datetime(df["asof"].iloc[0])
    S = float(df["spot"].iloc[0])
    r = float(df["rate"].iloc[0])
    df["days"] = (pd.to_datetime(df["expiry"]) - asof).dt.days

    calls = df[df["type"] == "C"].copy()
    puts = df[df["type"] == "P"].copy()

    out_rows = []
    for expiry, calls_e in calls.groupby("expiry"):
        days = int(calls_e["days"].iloc[0])
        if not (min_days <= days <= max_days):
            continue
        tau = days / 365.0
        puts_e = puts[puts["expiry"] == expiry]
        forward, q = estimate_forward_q(calls_e, puts_e, S, r, tau)
        if q is None:
            q = 0.0
        calls_e = calls_e.copy()
        calls_e["price"] = _mid_price(calls_e)
        calls_e["moneyness"] = (S - calls_e["strike"]) / calls_e["strike"]
        mask = (
            (calls_e["moneyness"].abs() < max_abs_moneyness)
            & (calls_e["price"] >= min_price)
            & (calls_e["bid"] > 0)
            & (calls_e["ask"] > 0)
        )
        sel = calls_e.loc[mask]
        for _, row in sel.iterrows():
            out_rows.append({
                "S": S, "K": float(row["strike"]), "tau": tau, "r": r, "q": q,
                "price": float(row["price"]), "expiry": expiry, "days": days,
                "moneyness": float(row["moneyness"]),
            })

    clean = pd.DataFrame(out_rows).sort_values(["days", "K"]).reset_index(drop=True)
    return clean


def moneyness_bucket(m):
    """Clasifica por moneyness S/K como en el artículo (Tabla 3).

    OTM: 0.90 < S/K < 0.97; ATM: 0.97 <= S/K <= 1.03; ITM: 1.03 < S/K < 1.10.
    Con ``m = (S-K)/K``, S/K = 1 + m.
    """
    sk = 1.0 + m
    if sk < 0.97:
        return "OTM"
    if sk <= 1.03:
        return "ATM"
    return "ITM"


def save_processed(clean_df, name):
    """Guarda un DataFrame limpio en data/processed/ y devuelve la ruta."""
    ensure_dirs()
    out = DATA_PROCESSED / f"{name}.csv"
    clean_df.to_csv(out, index=False)
    return out


# --------------------------------------------------------------------------------------------
# Panel histórico (6 meses) desde DoltHub, para replicar el diseño del artículo
# --------------------------------------------------------------------------------------------

DOLT_API = "https://www.dolthub.com/api/v1alpha1/post-no-preference/options/master"


def fetch_dolthub_chain(date_str, ticker="SPY", timeout=45):
    """Descarga la cadena de opciones EOD de un día desde la base pública de DoltHub.

    La API de DoltHub expira en escaneos de rango, pero las consultas por fecha exacta
    (indexadas) son rápidas. Devuelve un DataFrame con expiration, strike, call_put, bid, ask,
    vol, o None si no hay datos ese día (feriado) o la consulta falla.
    """
    import requests

    q = (
        "SELECT expiration, strike, call_put, bid, ask, vol FROM option_chain "
        f"WHERE act_symbol='{ticker}' AND date='{date_str}'"
    )
    try:
        resp = requests.get(DOLT_API, params={"q": q}, timeout=timeout)
        data = resp.json()
    except Exception:
        return None
    if data.get("query_execution_status") != "Success" or not data.get("rows"):
        return None
    df = pd.DataFrame(data["rows"])
    for c in ["strike", "bid", "ask", "vol"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["date"] = date_str
    return df


def _forward_q_from_chain(calls_e, puts_e, S, r, tau):
    """Forward implícito y q por paridad put-call, usando columnas bid/ask (formato DoltHub)."""
    m = calls_e.merge(puts_e, on="strike", suffixes=("_c", "_p"))
    m = m[(m["bid_c"] > 0) & (m["ask_c"] > 0) & (m["bid_p"] > 0) & (m["ask_p"] > 0)]
    if len(m) == 0:
        return None, None
    c_mid = 0.5 * (m["bid_c"] + m["ask_c"]).to_numpy()
    p_mid = 0.5 * (m["bid_p"] + m["ask_p"]).to_numpy()
    diff = c_mid - p_mid
    i = int(np.argmin(np.abs(diff)))
    K_atm = float(m["strike"].to_numpy()[i])
    forward = K_atm + np.exp(r * tau) * diff[i]
    if forward <= 0:
        return None, None
    return float(forward), float(r - np.log(forward / S) / tau)


def clean_panel_date(raw, S, r, min_days=30, max_days=90, max_abs_moneyness=0.10, min_price=0.05):
    """Filtra la cadena de un día (formato DoltHub) y estima q por vencimiento.

    Devuelve filas con columnas: date, S, K, tau, r, q, price, expiry, days, moneyness.
    """
    calls = raw[raw["call_put"] == "Call"]
    puts = raw[raw["call_put"] == "Put"]
    date_str = raw["date"].iloc[0]
    asof = pd.to_datetime(date_str)
    out = []
    for expiry, ce in calls.groupby("expiration"):
        days = (pd.to_datetime(expiry) - asof).days
        if not (min_days <= days <= max_days):
            continue
        tau = days / 365.0
        pe = puts[puts["expiration"] == expiry]
        _, q = _forward_q_from_chain(ce, pe, S, r, tau)
        if q is None:
            q = 0.0
        # Recorte defensivo: la q por paridad absorbe desajustes de timing spot/opción; se acota
        # a un rango razonable para que una estimación atípica de un día no desestabilice.
        q = float(min(max(q, -0.05), 0.06))
        ce = ce.copy()
        ce["price"] = np.where((ce["bid"] > 0) & (ce["ask"] > 0),
                               0.5 * (ce["bid"] + ce["ask"]), np.nan)
        ce["moneyness"] = (S - ce["strike"]) / ce["strike"]
        sel = ce[(ce["moneyness"].abs() < max_abs_moneyness) & (ce["price"] >= min_price)
                 & (ce["bid"] > 0) & (ce["ask"] > 0)]
        for _, row in sel.iterrows():
            out.append({
                "date": date_str, "S": S, "K": float(row["strike"]), "tau": tau, "r": r,
                "q": q, "price": float(row["price"]), "expiry": expiry, "days": days,
                "moneyness": float(row["moneyness"]),
            })
    return out
