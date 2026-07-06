"""rsheston — Valoración y calibración del modelo Heston de dos factores con cambio de régimen.

Implementa el modelo de Lin & He (2021): un modelo de volatilidad estocástica de dos factores
que introduce un factor de cambio de régimen (cadena de Markov) en la volatilidad de la
volatilidad del modelo de Heston, con fórmula cerrada para opciones europeas vía inversión de
Gil-Pelaez.

Módulos:
    charfn       Funciones características (Heston, Lin-He) y sus componentes (D, C, f, M).
    pricing      Valoración por Gil-Pelaez, Black-Scholes y volatilidad implícita.
    montecarlo   Verificación por simulación (semi-Monte-Carlo y Euler completo).
    calibration  Calibración a datos de mercado (objetivo MSE, optimización global).
    market_data  Descarga y limpieza de datos de mercado (yfinance).
"""

__version__ = "0.1.0"
