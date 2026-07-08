"""Verificación de la función característica del modelo Lin & He.

Estrategia de verificación (no confiar en la transcripción del artículo):
1. La exponencial de matriz 2x2 en forma cerrada coincide con scipy.linalg.expm.
2. f(phi; tau) coincide con la integral numérica de D(phi; u)^2 (valida la ec. 2.19).
3. Con lambda1=lambda2=0 el factor de régimen vale 1 y m(phi) == función característica de
   Heston; y el precio Lin-He == precio Heston (degeneración exacta).
4. El factor de régimen es 1 cuando no hay cambio de régimen efectivo.
"""

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

from rsheston.charfn import (
    HestonParams,
    LinHeParams,
    _expm_2x2,
    heston_D,
    heston_cf,
    heston_core,
    linhe_cf,
    linhe_f,
    linhe_regime_factor,
    make_heston_cf,
    make_linhe_cf,
)
from rsheston.pricing import gil_pelaez_call


def _params(lambda1=0.05, lambda2=0.03):
    return LinHeParams(
        kappa=10.0, theta=0.08, sigma=0.1, rho=-0.5, v0=0.03,
        lambda1=lambda1, lambda2=lambda2, lambda12=10.0, lambda21=20.0,
    )


@pytest.mark.parametrize("phi", [0.5, 2.0, 10.0, 1.0 - 1j])
def test_expm_2x2_matches_scipy(phi):
    """La exponencial de matriz 2x2 en forma cerrada coincide con scipy.linalg.expm."""
    M = np.array([[0.3 + 0.2j, -1.5], [2.0, -0.7 + 0.1j]])
    e11, e12, e21, e22 = _expm_2x2(M[0, 0], M[0, 1], M[1, 0], M[1, 1])
    ref = expm(M)
    got = np.array([[e11, e12], [e21, e22]])
    assert np.allclose(got, ref, atol=1e-12)


def test_expm_2x2_small_s_limit():
    """El caso s->0 (matriz casi múltiplo de la identidad) no produce nan."""
    e11, e12, e21, e22 = _expm_2x2(2.0, 0.0, 0.0, 2.0)
    assert e11 == pytest.approx(np.exp(2.0))
    assert e22 == pytest.approx(np.exp(2.0))
    assert e12 == pytest.approx(0.0)
    assert e21 == pytest.approx(0.0)


@pytest.mark.parametrize("phi", [0.7, 3.0, 8.0, 2.0 - 1j])
def test_linhe_f_matches_numerical_integral(phi):
    """f(phi; tau) (ec. 2.19) coincide con la integral numérica de D(phi; u)^2 en [0, tau].

    Verificación independiente de la fórmula cerrada: f = ∫_0^tau D(phi; u)^2 du.
    """
    p = _params()
    tau = 0.5
    a, d, g, edt = heston_core(phi, tau, p.kappa, p.theta, p.sigma, p.rho)
    f_closed = linhe_f(a, d, g, edt, tau, p.sigma)

    def D_squared(u, part):
        au, du, gu, edtu = heston_core(phi, u, p.kappa, p.theta, p.sigma, p.rho)
        D = heston_D(au, du, gu, edtu, p.sigma)
        return D.real**2 - D.imag**2 if part == "re" else 2 * D.real * D.imag

    f_re = quad(D_squared, 0, tau, args=("re",))[0]
    f_im = quad(D_squared, 0, tau, args=("im",))[0]
    f_numeric = f_re + 1j * f_im
    assert f_closed == pytest.approx(f_numeric, abs=1e-8)


def test_regime_factor_is_one_when_no_regime_effect():
    """Con lambda1=lambda2=0, el factor <e^M X_t, I> vale 1 en ambos estados."""
    p = _params(lambda1=0.0, lambda2=0.0)
    # f arbitrario: no importa porque lambda_i^2 f = 0.
    f = 3.14 + 2.0j
    assert linhe_regime_factor(f, 0.5, p, state=1) == pytest.approx(1.0, abs=1e-12)
    assert linhe_regime_factor(f, 0.5, p, state=2) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("phi", [0.5, 2.0, 5.0, 1.5 - 1j])
def test_linhe_cf_degenerates_to_heston(phi):
    """Con lambda1=lambda2=0, la función característica de Lin-He == la de Heston."""
    p = _params(lambda1=0.0, lambda2=0.0)
    S, tau, r = 10.0, 0.5, 0.05
    m_linhe = linhe_cf(phi, S=S, tau=tau, r=r, params=p, state=1)
    m_heston = heston_cf(phi, S=S, tau=tau, r=r, params=p.heston())
    assert m_linhe == pytest.approx(m_heston, abs=1e-12)


def test_linhe_price_degenerates_to_heston():
    """Con lambda1=lambda2=0, el precio Lin-He == el precio Heston (degeneración exacta).

    Es la verificación más fuerte y barata del pricer del modelo (rúbrica, objetivo 2).
    """
    p = _params(lambda1=0.0, lambda2=0.0)
    S, r, tau = 10.0, 0.05, 0.5
    for K in [8.0, 9.0, 10.0, 11.0, 12.0]:
        cf_linhe = make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1)
        cf_heston = make_heston_cf(S=S, tau=tau, r=r, params=p.heston())
        price_linhe = gil_pelaez_call(cf_linhe, S, K, r, tau)
        price_heston = gil_pelaez_call(cf_heston, S, K, r, tau)
        assert price_linhe == pytest.approx(price_heston, abs=1e-8)


def test_linhe_cf_normalization():
    """m(0)=1 (como límite) bajo el modelo Lin-He."""
    p = _params()
    cf = make_linhe_cf(S=10.0, tau=0.5, r=0.05, params=p, state=1)
    assert cf(1e-7) == pytest.approx(1.0, abs=1e-5)


def test_linhe_price_differs_from_heston_with_regime():
    """Con lambda>0 el precio difiere del de Heston (el segundo factor tiene efecto)."""
    p = _params(lambda1=0.1, lambda2=0.08)
    S, K, r, tau = 10.0, 10.0, 0.05, 0.5
    cf_linhe = make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1)
    cf_heston = make_heston_cf(S=S, tau=tau, r=r, params=p.heston())
    price_linhe = gil_pelaez_call(cf_linhe, S, K, r, tau)
    price_heston = gil_pelaez_call(cf_heston, S, K, r, tau)
    assert abs(price_linhe - price_heston) > 1e-4
    assert 0 < price_linhe < S  # precio válido


def test_adaptive_truncation_handles_tail_blowup():
    """El truncamiento adaptativo da un precio estable pese a que |m| explota en la cola.

    Con los parámetros de la Fig. 1 del artículo (lambda1=0.01, lambda2=0.05, T=0.5) la cf
    decae hasta phi~120 y luego crece; un u_max fijo grande da basura, pero el modo adaptativo
    trunca en la región de decaimiento y coincide con truncamientos fijos seguros.
    """
    p = _params(lambda1=0.01, lambda2=0.05)
    S, K, r, tau = 10.0, 10.0, 0.05, 0.5
    cf = make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1)
    price_adaptive = gil_pelaez_call(cf, S, K, r, tau)  # adaptive=True por defecto
    price_safe = gil_pelaez_call(cf, S, K, r, tau, u_max=100.0, adaptive=False, n_nodes=512)
    assert price_adaptive == pytest.approx(price_safe, abs=1e-5)
    assert 0 < price_adaptive < S


def test_fixed_truncation_too_large_is_corrupted():
    """Documenta el fallo esperado: con u_max fijo demasiado grande el precio se corrompe."""
    p = _params(lambda1=0.01, lambda2=0.05)
    S, K, r, tau = 10.0, 10.0, 0.05, 0.5
    cf = make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1)
    price_bad = gil_pelaez_call(cf, S, K, r, tau, u_max=250.0, adaptive=False, n_nodes=512)
    # El truncamiento en la región de explosión produce un precio absurdo (no en [0, S]).
    assert not (0 < price_bad < S)


def test_linhe_price_increases_with_underlying():
    """El precio de la call es creciente en el subyacente (intuición financiera, Fig. 1a)."""
    p = _params(lambda1=0.01, lambda2=0.05)
    r, tau, K = 0.05, 0.5, 10.0
    prices = [
        gil_pelaez_call(make_linhe_cf(S=S, tau=tau, r=r, params=p, state=1), S, K, r, tau)
        for S in [8, 9, 10, 11, 12]
    ]
    assert all(x < y for x, y in zip(prices, prices[1:]))
