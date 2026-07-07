"""Funciones características para valoración por inversión de Fourier (Gil-Pelaez).

Implementa la función característica de ``y_T = ln S_T`` bajo el modelo de Heston (1993),
que en este proyecto sirve como referencia y como benchmark de calibración. El modelo de
Lin & He (2021) reutiliza estas mismas piezas (``d``, ``g``, ``D``, ``C``) y se implementa en
la Etapa 2.

Convención de notación (siguiendo el artículo): la unidad imaginaria se denota ``j`` en el
texto; aquí usamos ``1j`` de numpy. La función característica es ``m(phi) = E[exp(j*phi*y_T)]``.
Todas las funciones aceptan ``phi`` escalar o ndarray (posiblemente complejo, para evaluar
``m(phi - j)`` como exige la fórmula de Gil-Pelaez) y están vectorizadas.

Ecuaciones de referencia (Lin & He 2021):
    (2.13) ODEs de Riccati para D y C.
    (2.14) Solución cerrada de D(phi; tau).
    (2.15) Solución de C(phi; tau) (parte de Heston = C̄).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HestonParams:
    """Parámetros del modelo de Heston.

    Attributes:
        kappa: velocidad de reversión a la media (k en el artículo).
        theta: nivel de reversión de la varianza.
        sigma: volatilidad de la volatilidad.
        rho: correlación entre el subyacente y la varianza.
        v0: varianza instantánea inicial.
    """

    kappa: float
    theta: float
    sigma: float
    rho: float
    v0: float


def heston_core(phi, tau, kappa, theta, sigma, rho):
    """Cantidades base compartidas del ansatz afín de Heston.

    Devuelve ``(a, d, g, edt)`` donde ``a = j*phi*rho*sigma - k``, ``d`` es la raíz que aparece
    en la solución de la Riccati (2.14), ``g`` el cociente asociado y ``edt = exp(d*tau)``.
    Estas cantidades las reutilizan tanto ``D``/``C`` (Heston) como ``f`` (Lin & He, Etapa 2),
    de modo que la solución de la ODE se escribe en un solo lugar.
    """
    j = 1j
    a = j * phi * rho * sigma - kappa
    d = np.sqrt(a**2 + sigma**2 * (j * phi + phi**2))
    g = (a - d) / (a + d)
    edt = np.exp(d * tau)
    return a, d, g, edt


def heston_D(a, d, g, edt, sigma):
    """Coeficiente D(phi; tau) del ansatz afín (ec. 2.14)."""
    return (d - a) / sigma**2 * (1 - edt) / (1 - g * edt)


def heston_Cbar(a, d, g, edt, tau, kappa, theta, sigma):
    """Parte de Heston del coeficiente C (ec. 2.15), sin el término de deriva ``r*j*phi*tau``.

    El término de deriva se añade en la función característica para poder incorporar el
    rendimiento por dividendos (``r -> r - q``) sin tocar esta pieza.
    """
    return (kappa * theta / sigma**2) * ((d - a) * tau - 2.0 * np.log((1 - g * edt) / (1 - g)))


def heston_cf(phi, *, S, tau, r, params: HestonParams, q=0.0):
    """Función característica ``m(phi) = E[exp(j*phi*y_T)]`` bajo Heston.

    Args:
        phi: frecuencia (escalar o ndarray, posiblemente complejo).
        S: precio actual del subyacente.
        tau: tiempo al vencimiento (años).
        r: tasa libre de riesgo.
        params: parámetros de Heston.
        q: rendimiento por dividendos (0 por defecto).

    Returns:
        Valor(es) complejos de la función característica.

    Nota: la fórmula tiene singularidades removibles en ``phi = 0`` y ``phi = -j`` (allí
    ``a + d = 0`` y ``g`` diverge). El valuador de Gil-Pelaez evita evaluarla en esos puntos
    (usa nodos reales positivos y calcula ``m(-j) = S*e^{(r-q)*tau}`` analíticamente).
    """
    j = 1j
    a, d, g, edt = heston_core(phi, tau, params.kappa, params.theta, params.sigma, params.rho)
    D = heston_D(a, d, g, edt, params.sigma)
    Cbar = heston_Cbar(a, d, g, edt, tau, params.kappa, params.theta, params.sigma)
    y = np.log(S)
    drift = (r - q) * j * phi * tau
    return np.exp(Cbar + drift + D * params.v0 + j * phi * y)


def make_heston_cf(*, S, tau, r, params: HestonParams, q=0.0):
    """Devuelve una función característica de una sola variable ``phi`` con parámetros fijados.

    Útil para pasarla al valuador de Gil-Pelaez, que solo necesita ``m(phi)``.
    """
    return lambda phi: heston_cf(phi, S=S, tau=tau, r=r, params=params, q=q)


# --------------------------------------------------------------------------------------------
# Modelo de Lin & He (2021): Heston de dos factores con cambio de régimen
# --------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LinHeParams:
    """Parámetros del modelo de Lin & He (2021).

    Extiende Heston con el factor de cambio de régimen en la volatilidad de la volatilidad:
    una cadena de Markov de dos estados con niveles ``lambda1``, ``lambda2`` y tasas de
    transición ``lambda12`` (1->2) y ``lambda21`` (2->1).
    """

    kappa: float
    theta: float
    sigma: float
    rho: float
    v0: float
    lambda1: float
    lambda2: float
    lambda12: float
    lambda21: float

    def heston(self) -> HestonParams:
        """Parte de Heston del modelo (usada como benchmark y en la degeneración)."""
        return HestonParams(self.kappa, self.theta, self.sigma, self.rho, self.v0)


def linhe_f(a, d, g, edt, tau, sigma):
    """Función ``f(phi; tau)`` de la ec. 2.19.

    Es la forma cerrada de la integral ``∫_0^tau D(phi; u)^2 du`` (equivalente a
    ``∫_t^T D(phi; T-s)^2 ds``), que aparece en el término diagonal de la matriz M.
    """
    return (1.0 / sigma**4) * (
        (d - a) ** 2 * tau
        + 4.0 * a * np.log((1 - g * edt) / (1 - g))
        + 4.0 * d / (1 - g * edt)
        - 4.0 * d / (1 - g)
    )


def _expm_2x2(a, b, c, d):
    """Exponencial de la matriz 2x2 ``[[a, b], [c, d]]`` con entradas vectorizadas.

    Usa la fórmula cerrada ``e^M = e^{T/2}[cosh(s) I + (sinh(s)/s)(M - (T/2) I)]`` con
    ``T = a + d`` (traza) y ``s = sqrt(((a-d)/2)^2 + b c)``. Evita llamar a ``scipy.linalg.expm``
    una vez por cada frecuencia ``phi`` (serían cientos de llamadas por precio), lo que es
    esencial para la eficiencia de la calibración. Acepta arrays complejos.

    Devuelve las cuatro entradas ``(e11, e12, e21, e22)``.
    """
    T = a + d
    half = 0.5 * T
    delta = 0.5 * (a - d)  # = a - T/2
    s = np.sqrt(delta**2 + b * c)
    # sinh(s)/s con límite 1 cuando s -> 0 (evita 0/0).
    small = np.abs(s) < 1e-12
    s_safe = np.where(small, 1.0, s)
    sinhc = np.where(small, 1.0, np.sinh(s_safe) / s_safe)
    ch = np.cosh(s)
    e_half = np.exp(half)
    e11 = e_half * (ch + sinhc * delta)
    e12 = e_half * (sinhc * b)
    e21 = e_half * (sinhc * c)
    e22 = e_half * (ch - sinhc * delta)
    return e11, e12, e21, e22


def linhe_M_entries(f, tau, params: LinHeParams):
    """Entradas de la matriz ``M = A^T * tau + diag(1/2 lambda_i^2 f)`` (ec. 2.18).

    ``A`` es la matriz de tasas de transición de la cadena de Markov.

    Nota (errata del artículo): la forma explícita impresa de M tiene la entrada (2,2) como
    ``-lambda21 + ...`` sin el factor ``tau``; la derivación ``∫ A^T ds = A^T tau`` implica
    ``-lambda21*tau``, que es lo que se usa aquí. Se verifica numéricamente por degeneración
    a Heston y contra Monte Carlo (Etapa 3).
    """
    l12, l21 = params.lambda12, params.lambda21
    M11 = -l12 * tau + 0.5 * params.lambda1**2 * f
    M12 = l21 * tau
    M21 = l12 * tau
    M22 = -l21 * tau + 0.5 * params.lambda2**2 * f
    return M11, M12, M21, M22


def linhe_regime_factor(f, tau, params: LinHeParams, state):
    """Factor de cambio de régimen ``<e^M X_t, I>`` (ecs. 2.17-2.18).

    El factor es la suma de la columna de ``e^M`` correspondiente al estado actual
    (``state=1`` o ``state=2``), pues ``X_t`` es ``(1,0)^T`` o ``(0,1)^T``. Usa ``_expm_2x2``;
    es adecuado para argumentos moderados. La función característica ``linhe_cf`` usa en cambio
    una forma que combina este factor con el exponente de Heston para evitar desbordamientos
    (0*inf) en la cola de altas frecuencias.
    """
    M11, M12, M21, M22 = linhe_M_entries(f, tau, params)
    e11, e12, e21, e22 = _expm_2x2(M11, M12, M21, M22)
    if state == 1:
        return e11 + e21  # suma de la columna 1 (X_t = (1,0)^T)
    if state == 2:
        return e12 + e22  # suma de la columna 2 (X_t = (0,1)^T)
    raise ValueError(f"state debe ser 1 o 2, no {state!r}")


def linhe_cf(phi, *, S, tau, r, params: LinHeParams, state=1, q=0.0):
    """Función característica ``m(phi)`` bajo el modelo de Lin & He (ec. 2.20).

    ``m(phi) = exp(C̄ + D v0 + j phi y) * <e^M X_t, I>``, reutilizando las piezas de Heston
    (``C̄``, ``D``) y añadiendo el factor de cambio de régimen. Con ``lambda1 = lambda2 = 0``
    el factor de régimen vale 1 y se recupera exactamente la función característica de Heston.

    Implementación numéricamente estable: en vez de multiplicar ``exp(exponente_Heston)`` por
    el factor de régimen (que en la cola de altas frecuencias produce ``0*inf = nan`` al decaer
    Heston mientras el régimen explota), se descompone ``e^M`` en sus autovalores
    ``mu± = T/2 ± s`` y se combinan los exponentes en una sola exponencial por autovalor:

        m = 1/2 (1 + beta) exp(H + mu+) + 1/2 (1 - beta) exp(H + mu-),

    con ``H`` el exponente de Heston, ``s = sqrt(delta^2 + M12 M21)``, ``delta = (M11-M22)/2``
    y ``beta = (delta + M21)/s`` (estado 1) o ``beta = (M12 - delta)/s`` (estado 2).

    Args:
        phi: frecuencia (escalar o ndarray, posiblemente complejo).
        S, tau, r: subyacente, tiempo al vencimiento, tasa libre de riesgo.
        params: parámetros del modelo.
        state: estado actual de la cadena de Markov (1 o 2).
        q: rendimiento por dividendos.
    """
    j = 1j
    k, th, sig, rho = params.kappa, params.theta, params.sigma, params.rho
    a, d, g, edt = heston_core(phi, tau, k, th, sig, rho)
    D = heston_D(a, d, g, edt, sig)
    Cbar = heston_Cbar(a, d, g, edt, tau, k, th, sig)
    f = linhe_f(a, d, g, edt, tau, sig)

    M11, M12, M21, M22 = linhe_M_entries(f, tau, params)
    half_T = 0.5 * (M11 + M22)
    delta = 0.5 * (M11 - M22)
    s = np.sqrt(delta**2 + M12 * M21)
    num = (delta + M21) if state == 1 else (M12 - delta)

    y = np.log(S)
    H = Cbar + (r - q) * j * phi * tau + D * params.v0 + j * phi * y

    small = np.abs(s) < 1e-10
    s_safe = np.where(small, 1.0, s)
    beta = num / s_safe
    # Rama estable general (autovalores separados); en cada exp se combina H con mu±.
    # Los desbordamientos en la cola de altas frecuencias son esperados (la cf del modelo no
    # está acotada, ver D6) y se manejan por truncamiento adaptativo aguas arriba.
    with np.errstate(over="ignore", invalid="ignore"):
        m_main = 0.5 * (1 + beta) * np.exp(H + half_T + s) + 0.5 * (1 - beta) * np.exp(
            H + half_T - s
        )
        # Límite s -> 0: m = exp(H + T/2)(cosh(0) + num sinhc(0)) = exp(H + T/2)(1 + num).
        m_small = np.exp(H + half_T) * (1.0 + num)
    return np.where(small, m_small, m_main)


def make_linhe_cf(*, S, tau, r, params: LinHeParams, state=1, q=0.0):
    """Devuelve la función característica de Lin & He de una sola variable ``phi``."""
    return lambda phi: linhe_cf(phi, S=S, tau=tau, r=r, params=params, state=state, q=q)
