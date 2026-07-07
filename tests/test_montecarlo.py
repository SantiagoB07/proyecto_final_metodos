"""Verificación de la Etapa 3: la fórmula cerrada coincide con Monte Carlo.

Tests rápidos (pocos caminos) con semilla fija. La verificación completa (más caminos,
figuras) está en scripts/02_verify_semimc.py.
"""

import numpy as np
import pytest

from rsheston.charfn import LinHeParams, make_linhe_cf
from rsheston.montecarlo import (
    mc_euler_call_price,
    semi_mc_call_price,
    simulate_chain_segments,
)
from rsheston.pricing import gil_pelaez_call

PARAMS = LinHeParams(
    kappa=10, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03,
    lambda1=0.01, lambda2=0.05, lambda12=10, lambda21=20,
)
S, K, R, TAU, STATE = 10.0, 10.0, 0.05, 0.5, 1


def test_semi_mc_matches_formula():
    """El semi-Monte-Carlo coincide con la fórmula cerrada (valida el paso de Elliott-Lian).

    El semi-MC reutiliza la cf condicional, así que su varianza es baja; con pocos caminos ya
    coincide muy bien con la fórmula.
    """
    cf = make_linhe_cf(S=S, tau=TAU, r=R, params=PARAMS, state=STATE)
    formula = gil_pelaez_call(cf, S, K, R, TAU)
    semi, err = semi_mc_call_price(S, K, R, TAU, PARAMS, state=STATE, n_paths=1500)
    assert semi == pytest.approx(formula, abs=5 * err + 1e-3)


def test_euler_mc_matches_formula():
    """La simulación de Euler completa (independiente) coincide dentro del error estándar."""
    cf = make_linhe_cf(S=S, tau=TAU, r=R, params=PARAMS, state=STATE)
    formula = gil_pelaez_call(cf, S, K, R, TAU)
    price, err = mc_euler_call_price(
        S, K, R, TAU, PARAMS, state=STATE, n_paths=100_000, n_steps=150, return_stderr=True
    )
    # Dentro de ~4 errores estándar + tolerancia por el sesgo de discretización.
    assert abs(price - formula) < 4 * err + 5e-3


def test_euler_mc_reproducible():
    """Misma semilla -> mismo precio (reproducibilidad, requisito de la rúbrica)."""
    kw = dict(state=STATE, n_paths=20_000, n_steps=100, seed=42)
    p1 = mc_euler_call_price(S, K, R, TAU, PARAMS, **kw)
    p2 = mc_euler_call_price(S, K, R, TAU, PARAMS, **kw)
    assert p1 == p2


def test_chain_segments_cover_horizon():
    """Los segmentos de la cadena de Markov cubren [0, tau] sin huecos."""
    rng = np.random.default_rng(0)
    segs = simulate_chain_segments(0.5, 10.0, 20.0, 1, rng)
    assert segs[0][0] == 0.0
    assert segs[-1][1] == pytest.approx(0.5)
    for (s0, s1, _), (s0n, _, _) in zip(segs, segs[1:]):
        assert s1 == pytest.approx(s0n)  # continuidad
    # Los estados alternan 1,2,1,2,...
    states = [s[2] for s in segs]
    assert all(a != b for a, b in zip(states, states[1:]))
