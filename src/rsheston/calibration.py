"""Calibración de los modelos a datos de mercado (Etapa 6).

Minimiza el error cuadrático medio en dólares entre precios de mercado y de modelo (ec. 4.1 del
artículo), usando optimización global (``scipy.optimize.dual_annealing``, análogo abierto al
ASA del artículo). Se reportan optimizador, cotas, semilla y punto inicial (requisito de la
rúbrica). Los precios se calculan agrupando por vencimiento y vectorizando sobre strikes.

Interfaz de modelo genérica (``ModelSpec``): permite calibrar Heston (5 parámetros) y el modelo
de Lin & He (9 parámetros) con el mismo código.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from scipy.optimize import dual_annealing

from .charfn import HestonParams, LinHeParams, make_heston_cf, make_linhe_cf
from .pricing import gil_pelaez_calls


@dataclass
class ModelSpec:
    """Especificación de un modelo a calibrar.

    Attributes:
        name: nombre del modelo.
        param_names: nombres de los parámetros (orden del vector theta).
        bounds: cotas (min, max) por parámetro para la optimización global.
        make_cf: función ``(theta_dict, S, tau, r, q) -> cf`` que arma la función característica.
    """

    name: str
    param_names: list[str]
    bounds: list[tuple[float, float]]
    make_cf: Callable


def _heston_cf_builder(theta, S, tau, r, q):
    p = HestonParams(kappa=theta["kappa"], theta=theta["theta"], sigma=theta["sigma"],
                     rho=theta["rho"], v0=theta["v0"])
    return make_heston_cf(S=S, tau=tau, r=r, params=p, q=q)


def _linhe_cf_builder(theta, S, tau, r, q):
    p = LinHeParams(
        kappa=theta["kappa"], theta=theta["theta"], sigma=theta["sigma"], rho=theta["rho"],
        v0=theta["v0"], lambda1=theta["lambda1"], lambda2=theta["lambda2"],
        lambda12=theta["lambda12"], lambda21=theta["lambda21"],
    )
    return make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1, q=q)


# Cotas: k, theta, sigma, v0 > 0; rho en (-1, 1); lambdas de régimen >= 0; tasas de transición > 0.
HESTON_SPEC = ModelSpec(
    name="Heston",
    param_names=["kappa", "theta", "sigma", "rho", "v0"],
    bounds=[(0.1, 20.0), (0.001, 0.5), (0.01, 2.0), (-0.999, 0.0), (0.001, 0.3)],
    make_cf=_heston_cf_builder,
)

LINHE_SPEC = ModelSpec(
    name="Lin-He",
    param_names=["kappa", "theta", "sigma", "rho", "v0", "lambda1", "lambda2",
                 "lambda12", "lambda21"],
    bounds=[(0.1, 20.0), (0.001, 0.5), (0.01, 2.0), (-0.999, 0.0), (0.001, 0.3),
            (0.0, 1.0), (0.0, 1.0), (0.1, 30.0), (0.1, 30.0)],
    make_cf=_linhe_cf_builder,
)


def model_prices(theta_dict, data: pd.DataFrame, spec: ModelSpec):
    """Precios del modelo para cada fila de ``data``, agrupando por (tau, r, q).

    ``data`` debe tener columnas S, K, tau, r, q.
    """
    prices = np.empty(len(data))
    for (tau, r, q), grp in data.groupby(["tau", "r", "q"], sort=False):
        S = float(grp["S"].iloc[0])
        cf = spec.make_cf(theta_dict, S, tau, r, q)
        Ks = grp["K"].to_numpy()
        prices[grp.index.to_numpy()] = gil_pelaez_calls(cf, S, Ks, r, tau, q=q)
    return prices


def mse_objective(theta_vec, data: pd.DataFrame, spec: ModelSpec):
    """Error cuadrático medio en dólares (ec. 4.1). Penaliza parámetros que fallan numéricamente."""
    theta = dict(zip(spec.param_names, theta_vec))
    try:
        model = model_prices(theta, data, spec)
    except (FloatingPointError, ValueError):
        return 1e12
    if not np.all(np.isfinite(model)):
        return 1e12
    market = data["price"].to_numpy()
    return float(np.mean((market - model) ** 2))


def calibrate(data: pd.DataFrame, spec: ModelSpec, seed=12345, maxiter=200, x0=None):
    """Calibra ``spec`` a ``data`` minimizando el MSE con dual_annealing (optimización global).

    Returns:
        dict con: params (dict), mse, resultado (OptimizeResult), spec, seed, x0, bounds.
    """
    data = data.reset_index(drop=True)
    result = dual_annealing(
        mse_objective, bounds=spec.bounds, args=(data, spec), seed=seed, maxiter=maxiter, x0=x0,
    )
    params = dict(zip(spec.param_names, result.x))
    return {
        "model": spec.name,
        "params": params,
        "mse": float(result.fun),
        "result": result,
        "seed": seed,
        "x0": x0,
        "bounds": spec.bounds,
    }


def evaluate_mse(theta_dict, data: pd.DataFrame, spec: ModelSpec):
    """MSE de ``spec`` con parámetros ``theta_dict`` sobre ``data`` (in o out-of-sample)."""
    model = model_prices(theta_dict, data, spec)
    market = data["price"].to_numpy()
    return float(np.mean((market - model) ** 2))


def evaluate_by_moneyness(theta_dict, data: pd.DataFrame, spec: ModelSpec):
    """MSE por bucket de moneyness (OTM/ATM/ITM), como la Tabla 3 del artículo."""
    from .market_data import moneyness_bucket

    model = model_prices(theta_dict, data, spec)
    market = data["price"].to_numpy()
    buckets = data["moneyness"].apply(moneyness_bucket).to_numpy()
    out = {}
    for b in ["OTM", "ATM", "ITM"]:
        mask = buckets == b
        if mask.any():
            out[b] = float(np.mean((market[mask] - model[mask]) ** 2))
    return out
