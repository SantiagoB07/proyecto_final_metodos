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
