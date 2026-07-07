"""Verificación de las Etapas 5-6: estimación de q, objetivo MSE y calibración."""

import numpy as np
import pandas as pd
import pytest

from rsheston.calibration import (
    HESTON_SPEC,
    LINHE_SPEC,
    evaluate_mse,
    model_prices,
    mse_objective,
)
from rsheston.charfn import HestonParams, make_heston_cf
from rsheston.market_data import estimate_forward_q, moneyness_bucket
from rsheston.pricing import gil_pelaez_calls


def _synthetic_data(q_true=0.0):
    """Genera precios de Heston (con q) para varias opciones: base de prueba de calibración."""
    S, r, tau = 100.0, 0.04, 0.5
    params = HestonParams(kappa=3.0, theta=0.05, sigma=0.5, rho=-0.6, v0=0.04)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params, q=q_true)
    Ks = np.array([92.0, 96.0, 100.0, 104.0, 108.0])
    prices = gil_pelaez_calls(cf, S, Ks, r, tau, q=q_true)
    df = pd.DataFrame({
        "S": S, "K": Ks, "tau": tau, "r": r, "q": q_true, "price": prices,
        "moneyness": (S - Ks) / Ks,
    })
    return df, params


def test_moneyness_bucket():
    assert moneyness_bucket(0.05) == "ITM"   # S/K = 1.05
    assert moneyness_bucket(0.0) == "ATM"     # S/K = 1.00
    assert moneyness_bucket(-0.05) == "OTM"   # S/K = 0.95


def test_estimate_forward_q_recovers_yield():
    """estimate_forward_q recupera q a partir de precios que cumplen la paridad put-call."""
    S, r, tau, q = 100.0, 0.04, 0.5, 0.015
    Ks = np.array([90.0, 95.0, 100.0, 105.0, 110.0])
    forward = S * np.exp((r - q) * tau)
    # Precios sintéticos que cumplen exactamente C - P = e^{-r tau}(F - K).
    call = np.maximum(forward - Ks, 0.0) * np.exp(-r * tau) + 5.0  # valor temporal arbitrario +5
    put = call - np.exp(-r * tau) * (forward - Ks)
    calls_e = pd.DataFrame({"strike": Ks, "bid": call - 0.1, "ask": call + 0.1, "lastPrice": call})
    puts_e = pd.DataFrame({"strike": Ks, "bid": put - 0.1, "ask": put + 0.1, "lastPrice": put})
    fwd_est, q_est = estimate_forward_q(calls_e, puts_e, S, r, tau)
    assert q_est == pytest.approx(q, abs=1e-3)
    assert fwd_est == pytest.approx(forward, rel=1e-3)


def test_model_prices_shape_and_finite():
    df, _ = _synthetic_data()
    theta = dict(kappa=3.0, theta=0.05, sigma=0.5, rho=-0.6, v0=0.04)
    prices = model_prices(theta, df, HESTON_SPEC)
    assert prices.shape == (len(df),)
    assert np.all(np.isfinite(prices))


def test_mse_zero_at_true_params():
    """El MSE es ~0 cuando se evalúa en los parámetros que generaron los datos."""
    df, params = _synthetic_data()
    theta = dict(kappa=params.kappa, theta=params.theta, sigma=params.sigma,
                 rho=params.rho, v0=params.v0)
    mse = evaluate_mse(theta, df, HESTON_SPEC)
    assert mse < 1e-6


def test_mse_objective_penalizes_invalid():
    """Parámetros que producen precios no finitos reciben una penalización grande."""
    df, _ = _synthetic_data()
    # sigma enorme + rho extremo pueden desestabilizar; el objetivo no debe devolver nan.
    bad = np.array([20.0, 0.5, 2.0, -0.999, 0.3])
    val = mse_objective(bad, df, HESTON_SPEC)
    assert np.isfinite(val)


def test_heston_spec_bounds_consistent():
    assert len(HESTON_SPEC.param_names) == len(HESTON_SPEC.bounds) == 5
    assert len(LINHE_SPEC.param_names) == len(LINHE_SPEC.bounds) == 9
