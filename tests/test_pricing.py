"""Verificación de la Etapa 1: Black-Scholes y valuador de Heston por Gil-Pelaez."""

import numpy as np
import pytest

from rsheston.charfn import HestonParams, make_heston_cf
from rsheston.pricing import (
    black_scholes_call,
    black_scholes_put,
    gil_pelaez_call,
    gil_pelaez_calls,
    implied_vol,
)


def test_black_scholes_reference_value():
    """Valor conocido de Black-Scholes (S=K=100, r=5%, tau=1, sigma=20%)."""
    price = black_scholes_call(100, 100, 0.05, 1.0, 0.20)
    assert price == pytest.approx(10.4506, abs=1e-3)


def test_put_call_parity_bs():
    """C - P = S*e^{-q tau} - K*e^{-r tau}."""
    S, K, r, tau, sigma, q = 100, 90, 0.03, 0.5, 0.25, 0.01
    call = black_scholes_call(S, K, r, tau, sigma, q)
    put = black_scholes_put(S, K, r, tau, sigma, q)
    lhs = call - put
    rhs = S * np.exp(-q * tau) - K * np.exp(-r * tau)
    assert lhs == pytest.approx(rhs, abs=1e-10)


def test_implied_vol_roundtrip():
    """La volatilidad implícita recupera la sigma que generó el precio."""
    S, K, r, tau, sigma = 100, 105, 0.04, 0.75, 0.30
    price = black_scholes_call(S, K, r, tau, sigma)
    iv = implied_vol(price, S, K, r, tau, is_call=True)
    assert iv == pytest.approx(sigma, abs=1e-6)


def test_gil_pelaez_cf_normalization():
    """La función característica cumple m(0)=1 y m(-j)=S*e^{(r-q)tau} (como límites).

    La fórmula cerrada tiene singularidades removibles exactamente en phi=0 y phi=-j
    (allí a+d=0); se verifica el límite evaluando cerca de esos puntos.
    """
    S, r, tau, q = 100.0, 0.05, 0.5, 0.0
    params = HestonParams(kappa=2.0, theta=0.04, sigma=0.5, rho=-0.7, v0=0.04)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params, q=q)
    assert cf(1e-7) == pytest.approx(1.0, abs=1e-5)
    assert cf(-1j + 1e-7) == pytest.approx(S * np.exp((r - q) * tau), abs=1e-3)


def test_heston_degenerates_to_black_scholes():
    """Con sigma->0 y v0=theta, Heston debe coincidir con Black-Scholes de vol sqrt(theta).

    Al anular la volatilidad de la volatilidad y fijar la varianza en su nivel de reversión,
    la varianza es constante = theta, y el precio debe ser el de Black-Scholes con
    sigma_bs = sqrt(theta).
    """
    S, K, r, tau = 100.0, 100.0, 0.05, 1.0
    theta = 0.04
    params = HestonParams(kappa=2.0, theta=theta, sigma=1e-6, rho=0.0, v0=theta)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params)
    heston_price = gil_pelaez_call(cf, S, K, r, tau)
    bs_price = black_scholes_call(S, K, r, tau, np.sqrt(theta))
    assert heston_price == pytest.approx(bs_price, abs=1e-3)


@pytest.mark.parametrize("K", [80, 90, 100, 110, 120])
def test_heston_degenerates_across_strikes(K):
    """La degeneración a Black-Scholes se cumple en todo el rango de strikes."""
    S, r, tau = 100.0, 0.03, 0.5
    theta = 0.05
    params = HestonParams(kappa=3.0, theta=theta, sigma=1e-6, rho=-0.5, v0=theta)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params)
    heston_price = gil_pelaez_call(cf, S, K, r, tau)
    bs_price = black_scholes_call(S, K, r, tau, np.sqrt(theta))
    assert heston_price == pytest.approx(bs_price, abs=2e-3)


def test_heston_gil_pelaez_matches_adaptive_quadrature():
    """Verificación independiente: Gauss-Legendre debe coincidir con quad adaptativo.

    Cruza el precio de Gil-Pelaez (cuadratura de Gauss-Legendre truncada) contra el mismo
    par de integrales evaluadas con ``scipy.integrate.quad`` (algoritmo adaptativo distinto).
    Coincidir a alta precisión valida que el truncamiento y el número de nodos son adecuados.
    """
    from scipy.integrate import quad

    S, K, r, tau = 100.0, 100.0, 0.0, 1.0
    params = HestonParams(kappa=2.0, theta=0.04, sigma=0.3, rho=-0.7, v0=0.04)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params)
    price_gl = gil_pelaez_call(cf, S, K, r, tau)

    m_neg_j = S * np.exp(r * tau)
    lnK = np.log(K)

    def integrand(phi, shift):
        m = cf(phi - 1j) / m_neg_j if shift else cf(phi)
        return np.real(np.exp(-1j * phi * lnK) / (1j * phi) * m)

    P1 = 0.5 + quad(integrand, 0, 400, args=(True,), limit=400)[0] / np.pi
    P2 = 0.5 + quad(integrand, 0, 400, args=(False,), limit=400)[0] / np.pi
    price_quad = np.exp(-r * tau) * (m_neg_j * P1 - K * P2)

    assert price_gl == pytest.approx(price_quad, abs=1e-4)


def test_heston_convergence_self_consistency():
    """La cuadratura por defecto ya está convergida (coincide con una mucho más fina)."""
    S, K, r, tau = 100.0, 100.0, 0.0, 1.0
    params = HestonParams(kappa=2.0, theta=0.04, sigma=0.3, rho=-0.7, v0=0.04)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params)
    price = gil_pelaez_call(cf, S, K, r, tau)
    price_fine = gil_pelaez_call(cf, S, K, r, tau, u_max=400.0, n_nodes=1024)
    assert price == pytest.approx(price_fine, abs=1e-4)


@pytest.mark.parametrize("q", [0.0, 0.02])
def test_multi_strike_matches_single(q):
    """gil_pelaez_calls (vectorizado) coincide con gil_pelaez_call strike por strike."""
    S, r, tau = 100.0, 0.04, 0.4
    params = HestonParams(kappa=3.0, theta=0.05, sigma=0.5, rho=-0.6, v0=0.04)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params, q=q)
    Ks = np.array([90.0, 95.0, 100.0, 105.0, 110.0])
    multi = gil_pelaez_calls(cf, S, Ks, r, tau, q=q)
    single = np.array([gil_pelaez_call(cf, S, K, r, tau, q=q) for K in Ks])
    assert np.allclose(multi, single, atol=1e-10)


def test_heston_put_call_parity():
    """El precio de Heston debe respetar la paridad put-call (put por parity)."""
    S, K, r, tau = 100.0, 95.0, 0.04, 0.5
    params = HestonParams(kappa=2.5, theta=0.05, sigma=0.4, rho=-0.6, v0=0.045)
    cf = make_heston_cf(S=S, tau=tau, r=r, params=params)
    call = gil_pelaez_call(cf, S, K, r, tau)
    # Put por paridad: P = C - S + K e^{-r tau}
    put = call - S + K * np.exp(-r * tau)
    # Debe ser no negativa y consistente (sanity de no arbitraje).
    assert put > 0
    assert call > max(S - K * np.exp(-r * tau), 0.0)
