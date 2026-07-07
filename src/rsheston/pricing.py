"""Valoración de opciones europeas.

Contiene:
- Black-Scholes cerrado y volatilidad implícita (caso límite y utilidad de reporte).
- El valuador general por inversión de Gil-Pelaez, que toma cualquier función característica
  ``m(phi)`` y devuelve el precio de una call europea. Es la única ruta de cálculo de precios;
  la usan tanto la verificación como la calibración.

Fórmula de Gil-Pelaez (Lin & He 2021, ecs. 2.4-2.8):

    U = e^{-r*tau} [ m(-j) * P1 - K * P2 ]

    P2 = 1/2 + (1/pi) ∫_0^∞ Re[ e^{-j*phi*ln K} / (j*phi) * m(phi) ] dphi
    P1 = 1/2 + (1/pi) ∫_0^∞ Re[ e^{-j*phi*ln K} / (j*phi) * m(phi - j) / m(-j) ] dphi

donde ``m(-j) = E[S_T] = S*e^{(r-q)*tau}``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Callable

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm


@lru_cache(maxsize=32)
def _leggauss_cached(n_nodes):
    """Nodos y pesos de Gauss-Legendre en [-1, 1], cacheados (leggauss es O(n^2))."""
    return np.polynomial.legendre.leggauss(n_nodes)

# Configuración por defecto de la cuadratura de Gil-Pelaez. La Etapa 4 (análisis numérico)
# justifica estos valores estudiando convergencia frente al truncamiento y el número de nodos.
DEFAULT_U_MAX = 200.0
DEFAULT_N_NODES = 256
DEFAULT_TRUNC_TOL = 1e-12  # tolerancia para el truncamiento adaptativo (ver D6)


def black_scholes_call(S, K, r, tau, sigma, q=0.0):
    """Precio Black-Scholes de una call europea (con rendimiento por dividendos ``q``)."""
    if tau <= 0:
        return max(S - K, 0.0)
    if sigma <= 0:
        return max(S * np.exp(-q * tau) - K * np.exp(-r * tau), 0.0)
    sqrt_tau = np.sqrt(tau)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * tau) / (sigma * sqrt_tau)
    d2 = d1 - sigma * sqrt_tau
    return S * np.exp(-q * tau) * norm.cdf(d1) - K * np.exp(-r * tau) * norm.cdf(d2)


def black_scholes_put(S, K, r, tau, sigma, q=0.0):
    """Precio Black-Scholes de una put europea (por paridad put-call)."""
    call = black_scholes_call(S, K, r, tau, sigma, q)
    return call - S * np.exp(-q * tau) + K * np.exp(-r * tau)


def implied_vol(price, S, K, r, tau, q=0.0, is_call=True, tol=1e-8, max_sigma=5.0):
    """Volatilidad implícita Black-Scholes por búsqueda de raíz (Brent).

    Devuelve ``nan`` si el precio está fuera de los límites de no arbitraje (no hay solución).
    """
    intrinsic = (
        max(S * np.exp(-q * tau) - K * np.exp(-r * tau), 0.0)
        if is_call
        else max(K * np.exp(-r * tau) - S * np.exp(-q * tau), 0.0)
    )
    upper = S * np.exp(-q * tau) if is_call else K * np.exp(-r * tau)
    if not (intrinsic - tol <= price <= upper + tol):
        return np.nan

    price_fn = black_scholes_call if is_call else black_scholes_put

    def objective(sigma):
        return price_fn(S, K, r, tau, sigma, q) - price

    try:
        return brentq(objective, 1e-9, max_sigma, xtol=tol)
    except ValueError:
        return np.nan


def adaptive_truncation(cf: Callable, u_cap=DEFAULT_U_MAX, tol=DEFAULT_TRUNC_TOL, n_probe=300):
    """Elige un límite de truncamiento en la región de decaimiento de ``|m(phi)|`` (ver D6).

    La función característica del modelo de Lin & He no está acotada: decae a frecuencias
    moderadas pero crece en la cola (violación de Feller). Se sondea ``|m(phi)|`` en una malla
    y se trunca en el primer punto donde cae por debajo de ``tol``; si nunca lo hace (empieza a
    crecer antes), se trunca en el mínimo, evitando la región de explosión.

    Args:
        cf: función característica de una variable.
        u_cap: frecuencia máxima a considerar (tope del sondeo).
        tol: umbral de magnitud por debajo del cual el aporte es despreciable.
        n_probe: número de puntos de sondeo.

    Returns:
        Límite superior de truncamiento efectivo (float).
    """
    phi = np.linspace(u_cap / n_probe, u_cap, n_probe)
    with np.errstate(over="ignore", invalid="ignore"):
        mag = np.abs(cf(phi))
    finite = np.isfinite(mag)
    below = np.nonzero(finite & (mag < tol))[0]
    if below.size:
        return float(phi[below[0]])
    # No baja de tol antes de explotar: truncar en el mínimo de la región finita (fin del
    # decaimiento, antes de la explosión de la cola). Los valores no finitos se enmascaran.
    mag_masked = np.where(finite, mag, np.inf)
    return float(phi[np.argmin(mag_masked)])


def gil_pelaez_call(
    cf: Callable,
    S,
    K,
    r,
    tau,
    q=0.0,
    u_max=DEFAULT_U_MAX,
    n_nodes=DEFAULT_N_NODES,
    adaptive=True,
    tol=DEFAULT_TRUNC_TOL,
):
    """Precio de una call europea por inversión de Gil-Pelaez.

    Args:
        cf: función característica ``m(phi)`` de ``y_T = ln S_T``, vectorizada en ``phi`` y capaz
            de aceptar argumentos complejos (se evalúa en ``phi``, ``phi - j`` y ``-j``).
        S, K, r, tau: subyacente, strike, tasa y tiempo al vencimiento.
        q: rendimiento por dividendos.
        u_max: límite superior de truncamiento (tope del sondeo si ``adaptive=True``).
        n_nodes: número de nodos de la cuadratura de Gauss-Legendre.
        adaptive: si True, elige el truncamiento en la región de decaimiento (ver D6);
            si False, usa ``u_max`` fijo (útil para estudios de convergencia, Etapa 4).
        tol: tolerancia del truncamiento adaptativo.

    Returns:
        Precio de la call (float).
    """
    if adaptive:
        u_max = adaptive_truncation(cf, u_cap=u_max, tol=tol)

    # Nodos y pesos de Gauss-Legendre mapeados de [-1, 1] a [0, u_max]. Los nodos son
    # interiores, así que phi nunca es exactamente 0 y se evita la singularidad de 1/(j*phi).
    x, w = _leggauss_cached(n_nodes)
    phi = 0.5 * u_max * (x + 1.0)
    weights = 0.5 * u_max * w

    # m(-j) = E[S_T] = S*e^{(r-q)*tau} para cualquier modelo martingala. Se calcula
    # analíticamente en vez de evaluar cf(-j): la fórmula cerrada tiene una singularidad
    # removible en phi = -j (allí a + d = 0). Los nodos phi son reales positivos, así que
    # cf(phi) y cf(phi - j) sí son seguros.
    m_neg_j = S * np.exp((r - q) * tau)
    m_phi = cf(phi)
    m_phi_shift = cf(phi - 1j)

    kernel = np.exp(-1j * phi * np.log(K)) / (1j * phi)
    integrand_2 = np.real(kernel * m_phi)
    integrand_1 = np.real(kernel * m_phi_shift / m_neg_j)

    P2 = 0.5 + np.sum(weights * integrand_2) / np.pi
    P1 = 0.5 + np.sum(weights * integrand_1) / np.pi

    return float(np.real(np.exp(-r * tau) * (m_neg_j * P1 - K * P2)))


def gil_pelaez_calls(
    cf: Callable,
    S,
    Ks,
    r,
    tau,
    q=0.0,
    u_max=DEFAULT_U_MAX,
    n_nodes=DEFAULT_N_NODES,
    adaptive=True,
    tol=DEFAULT_TRUNC_TOL,
):
    """Precios de varias calls con el mismo (S, tau, r, q) en una sola pasada (vectorizado).

    La función característica ``m(phi)`` no depende del strike, así que se evalúa una sola vez y
    se reutiliza para todos los strikes; solo el núcleo ``e^{-j phi ln K}`` cambia con K. Es la
    ruta usada por la calibración (agrupa por vencimiento), mucho más rápida que valorar strike
    por strike.

    Args:
        Ks: arreglo de strikes.
        (resto igual que gil_pelaez_call).

    Returns:
        ndarray de precios, uno por strike.
    """
    Ks = np.atleast_1d(np.asarray(Ks, dtype=float))
    if adaptive:
        u_max = adaptive_truncation(cf, u_cap=u_max, tol=tol)

    x, w = _leggauss_cached(n_nodes)
    phi = 0.5 * u_max * (x + 1.0)
    weights = 0.5 * u_max * w

    m_neg_j = S * np.exp((r - q) * tau)
    m_phi = cf(phi)
    m_phi_shift = cf(phi - 1j)

    base = 1.0 / (1j * phi)  # (n_nodes,)
    kernel = np.exp(-1j * np.outer(np.log(Ks), phi)) * base[None, :]  # (nK, n_nodes)
    integrand_2 = np.real(kernel * m_phi[None, :])
    integrand_1 = np.real(kernel * (m_phi_shift / m_neg_j)[None, :])

    P2 = 0.5 + (integrand_2 @ weights) / np.pi
    P1 = 0.5 + (integrand_1 @ weights) / np.pi

    return np.real(np.exp(-r * tau) * (m_neg_j * P1 - Ks * P2))
