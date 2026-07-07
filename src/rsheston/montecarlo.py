"""Verificación por simulación Monte Carlo del modelo de Lin & He.

Dos métodos, con distinto propósito de verificación:

- ``mc_euler_call_price``: simulación de Euler conjunta de (S, v, cadena de Markov). Es una
  verificación TOTALMENTE INDEPENDIENTE de la fórmula cerrada (no reutiliza la función
  característica), a costa de mayor varianza. Valida toda la derivación de una vez.

- ``semi_mc_call_price``: la semi-simulación del artículo (Liu et al. 2006). Simula solo la
  trayectoria de la cadena de Markov; dado el camino, ``lambda_t`` es determinista y el precio
  condicional se obtiene con la función característica condicional (Gil-Pelaez). Promedia los
  precios condicionales sobre caminos. Tiene mucha menor varianza y valida específicamente el
  paso de la esperanza matricial de Elliott-Lian (ec. 2.17), que es el más propenso a error.

Ambos usan un generador con semilla fija para reproducibilidad (requisito de la rúbrica).
"""

from __future__ import annotations

import numpy as np

from .charfn import (
    HestonParams,
    LinHeParams,
    heston_Cbar,
    heston_D,
    heston_core,
    linhe_f,
)
from .pricing import gil_pelaez_call


def mc_euler_call_price(
    S, K, r, tau, params: LinHeParams, state=1, q=0.0,
    n_paths=200_000, n_steps=200, seed=12345, return_stderr=False,
):
    """Precio de una call europea por simulación de Euler completa (verificación independiente).

    Simula el sistema acoplado bajo la medida neutral al riesgo:
        dy = (r - q - v/2) dt + sqrt(v) dW1
        dv = k(theta - v) dt + sigma sqrt(v) dW2 + lambda_{X_t} dB
    con corr(W1, W2) = rho y B independiente. Como el modelo viola la condición de Feller, se
    usa truncamiento completo (max(v, 0)) en los términos con sqrt(v). La cadena de Markov se
    simula por pasos con probabilidad de transición 1 - exp(-rate * dt).

    Args:
        S, K, r, tau: subyacente, strike, tasa, tiempo al vencimiento.
        params: parámetros del modelo.
        state: estado inicial de la cadena (1 o 2).
        q: rendimiento por dividendos.
        n_paths, n_steps: número de trayectorias y de pasos temporales.
        seed: semilla del generador (reproducibilidad).
        return_stderr: si True, devuelve (precio, error_estandar).

    Returns:
        Precio de la call (float), o (precio, stderr) si return_stderr.
    """
    rng = np.random.default_rng(seed)
    dt = tau / n_steps
    sqrt_dt = np.sqrt(dt)
    rho = params.rho
    sqrt_1mrho2 = np.sqrt(1.0 - rho**2)

    y = np.full(n_paths, np.log(S))
    v = np.full(n_paths, params.v0)
    st = np.full(n_paths, state, dtype=np.int8)

    # Probabilidades de transición por paso (cadena de dos estados).
    p_12 = 1.0 - np.exp(-params.lambda12 * dt)  # 1 -> 2
    p_21 = 1.0 - np.exp(-params.lambda21 * dt)  # 2 -> 1

    for _ in range(n_steps):
        z1 = rng.standard_normal(n_paths)
        z2 = rng.standard_normal(n_paths)
        z3 = rng.standard_normal(n_paths)
        dW1 = sqrt_dt * z1
        dW2 = sqrt_dt * (rho * z1 + sqrt_1mrho2 * z2)
        dB = sqrt_dt * z3

        v_pos = np.maximum(v, 0.0)
        sqrt_v = np.sqrt(v_pos)
        lam = np.where(st == 1, params.lambda1, params.lambda2)

        y += (r - q - 0.5 * v_pos) * dt + sqrt_v * dW1
        v += params.kappa * (params.theta - v) * dt + params.sigma * sqrt_v * dW2 + lam * dB

        # Transición de la cadena de Markov.
        u = rng.random(n_paths)
        switch_12 = (st == 1) & (u < p_12)
        switch_21 = (st == 2) & (u < p_21)
        st = np.where(switch_12, np.int8(2), st)
        st = np.where(switch_21, np.int8(1), st)

    payoff = np.exp(-r * tau) * np.maximum(np.exp(y) - K, 0.0)
    price = float(np.mean(payoff))
    if return_stderr:
        return price, float(np.std(payoff, ddof=1) / np.sqrt(n_paths))
    return price


def simulate_chain_segments(tau, lambda12, lambda21, initial_state, rng):
    """Simula la trayectoria de la cadena de Markov de dos estados en [0, tau].

    Usa tiempos de permanencia exponenciales (simulación exacta en tiempo continuo).

    Returns:
        Lista de segmentos ``(t_inicio, t_fin, estado)`` que cubren [0, tau].
    """
    segments = []
    t = 0.0
    state = initial_state
    while t < tau:
        rate = lambda12 if state == 1 else lambda21
        holding = rng.exponential(1.0 / rate) if rate > 0 else np.inf
        t_end = min(t + holding, tau)
        segments.append((t, t_end, state))
        t = t_end
        state = 2 if state == 1 else 1
    return segments


def _conditional_regime_exponent(phi, tau, params: LinHeParams, segments):
    """Término de régimen del exponente de la cf condicional para un camino de la cadena.

    Dado un camino (lambda_s determinista a trozos), el término es
        1/2 * sum_segmentos lambda_seg^2 * [f(phi; tau - s_ini) - f(phi; tau - s_fin)],
    usando la forma cerrada f(phi; u) = integral_0^u D(phi; w)^2 dw.
    """
    total = np.zeros_like(np.asarray(phi, dtype=complex))
    for (s0, s1, seg_state) in segments:
        lam = params.lambda1 if seg_state == 1 else params.lambda2
        if lam == 0.0:
            continue
        f_hi = _f_at(phi, tau - s0, params)
        f_lo = _f_at(phi, tau - s1, params)
        total += 0.5 * lam**2 * (f_hi - f_lo)
    return total


def _f_at(phi, u, params: LinHeParams):
    """Evalúa f(phi; u) reconstruyendo las cantidades base de Heston en el horizonte u."""
    a, d, g, edt = heston_core(phi, u, params.kappa, params.theta, params.sigma, params.rho)
    return linhe_f(a, d, g, edt, u, params.sigma)


def semi_mc_call_price(
    S, K, r, tau, params: LinHeParams, state=1, q=0.0,
    n_paths=20_000, seed=12345, u_max=200.0, n_nodes=256,
):
    """Precio por semi-Monte-Carlo (método del artículo, Liu et al. 2006).

    Para cada camino de la cadena de Markov se construye la función característica CONDICIONAL
    (Heston + término de régimen determinista del camino) y se valora por Gil-Pelaez; luego se
    promedian los precios condicionales. Verifica el paso de la esperanza matricial (ec. 2.17):
    el promedio de ``exp(1/2 integral lambda_s^2 D^2 ds)`` sobre caminos debe igualar
    ``<e^M X_t, I>``.

    Returns:
        (precio, error_estandar).
    """
    rng = np.random.default_rng(seed)
    hp = params.heston()

    # Trunca una sola vez usando la cf incondicional: todas las cf condicionales decaen de
    # forma similar, así se evita el sondeo adaptativo (costoso) en cada uno de los N caminos.
    from .charfn import make_linhe_cf
    from .pricing import adaptive_truncation

    u_trunc = adaptive_truncation(
        make_linhe_cf(S=S, tau=tau, r=r, params=params, state=state, q=q), u_cap=u_max
    )

    # Parte de Heston del exponente (común a todos los caminos), evaluada en los nodos.
    def conditional_cf_factory(segments):
        def cf(phi):
            a, d, g, edt = heston_core(phi, tau, hp.kappa, hp.theta, hp.sigma, hp.rho)
            D = heston_D(a, d, g, edt, hp.sigma)
            Cbar = heston_Cbar(a, d, g, edt, tau, hp.kappa, hp.theta, hp.sigma)
            y = np.log(S)
            H = Cbar + (r - q) * 1j * phi * tau + D * hp.v0 + 1j * phi * y
            regime = _conditional_regime_exponent(phi, tau, params, segments)
            return np.exp(H + regime)
        return cf

    prices = np.empty(n_paths)
    for i in range(n_paths):
        segments = simulate_chain_segments(tau, params.lambda12, params.lambda21, state, rng)
        cf = conditional_cf_factory(segments)
        prices[i] = gil_pelaez_call(
            cf, S, K, r, tau, u_max=u_trunc, n_nodes=n_nodes, adaptive=False
        )

    return float(np.mean(prices)), float(np.std(prices, ddof=1) / np.sqrt(n_paths))
