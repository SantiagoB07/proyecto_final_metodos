// Trabajo escrito — Proyecto final Métodos Numéricos en Finanzas
// Compilar: typst compile --root . paper/main.typ paper/main.pdf
// Vista previa en vivo: typst watch paper/main.typ

#set page(paper: "us-letter", numbering: "1", margin: 2.5cm)
#set text(size: 11pt, lang: "es", font: "New Computer Modern")
#set par(justify: true)
#set math.equation(numbering: "(1)")
#set heading(numbering: "1.")
#show link: set text(fill: blue)

// Helper para incluir una tabla desde un CSV de results/tables.
#let csv_table(path, header) = {
  let data = csv(path)
  table(
    columns: data.at(0).len(),
    ..header.map(h => strong(h)),
    ..data.slice(1).flatten(),
  )
}

#align(center)[
  #text(17pt, weight: "bold")[
    Valoración analítica de opciones europeas bajo un modelo Heston de dos
    factores con cambio de régimen
  ]

  #v(0.4em)
  #text(12pt)[Implementación, verificación y calibración a datos de mercado]

  #v(0.8em)
  Proyecto final · Métodos Numéricos en Finanzas \
  Maestría en Actuaría y Finanzas · Universidad Nacional de Colombia · 2026-I
]

#v(0.6em)

#align(center)[
  #box(width: 88%)[
    #set text(size: 10pt)
    #align(left)[
      *Resumen.* Implementamos, verificamos y calibramos el modelo de volatilidad estocástica
      de dos factores con cambio de régimen de #cite(<LinHe2021>, form: "prose"), que introduce
      una cadena de Markov en la volatilidad de la volatilidad del modelo de Heston preservando
      una fórmula cerrada para opciones europeas. Reconstruimos la función característica por el
      procedimiento en dos etapas del artículo (función característica condicional vía
      Feynman–Kac y ansatz afín, seguida de la esperanza sobre la cadena de Markov mediante una
      exponencial matricial) y valoramos por inversión de Gil-Pelaez. Verificamos la
      implementación en tres niveles: degeneración exacta al modelo de Heston, validación de la
      integral $integral D^2$ contra cuadratura numérica, y comparación con dos simulaciones
      Monte Carlo independientes (Euler completo y semi-Monte-Carlo), con error relativo máximo
      inferior al 0.7% reportado por el artículo. Analizamos numéricamente la cuadratura de
      inversión y documentamos una propiedad clave: la función característica del modelo no está
      acotada a altas frecuencias (consecuencia de la violación de la condición de Feller), lo
      que exige un truncamiento cuidadoso. Finalmente calibramos el modelo y el de Heston a
      opciones del S&P 500 (SPY) y comparamos su ajuste dentro y fuera de muestra.

      *Palabras clave:* volatilidad estocástica · dos factores · cambio de régimen ·
      función característica · Gil-Pelaez · calibración.
    ]
  ]
]

= Introducción

La valoración de opciones bajo el modelo de #cite(<BlackScholes1973>, form: "prose") supone
volatilidad constante, hipótesis desmentida por la _sonrisa de volatilidad_ observada en los
mercados. Los modelos de volatilidad estocástica corrigen esta deficiencia; el de
#cite(<Heston1993>, form: "prose") es el más popular porque, pese a introducir un segundo factor
aleatorio, admite una fórmula semianalítica para opciones europeas vía su función característica.
Sin embargo, con parámetros constantes el modelo de Heston ajusta imperfectamente los datos de
mercado, y existe amplia evidencia empírica de que la volatilidad cambia de _régimen_ con los
ciclos económicos.

Cuando la dinámica del subyacente admite una función característica en forma cerrada, el precio
de una opción europea se obtiene por inversión de Fourier. Existen varias familias de métodos
semianalíticos para esta inversión: la transformada rápida de Fourier de Carr–Madan, el método
COS de Fang–Oosterlee, la cuadratura directa y la fórmula de inversión de Gil-Pelaez. En este
trabajo usamos la inversión de Gil-Pelaez con cuadratura de Gauss-Legendre, por ser la forma en
que el artículo base plantea el precio y por su transparencia numérica; los aspectos de
convergencia y truncamiento se estudian en detalle en la Sección 6, siguiendo el enfoque de
métodos de transformada del curso #cite(<Hirsa2024>).

Este trabajo implementa el modelo de #cite(<LinHe2021>, form: "prose"), que incorpora un factor
de cambio de régimen —gobernado por una cadena de Markov— en la volatilidad de la volatilidad
del modelo de Heston, preservando una fórmula cerrada exacta para opciones europeas. Nuestro
aporte es una implementación reproducible y verificada del método, un análisis numérico de la
cuadratura de inversión (que el artículo no detalla) y una calibración a datos de mercado
reales, comparando el ajuste con el modelo de Heston. El código y los detalles de reproducción
acompañan a este documento.

= El artículo base

#cite(<LinHe2021>, form: "prose") parten de la observación de que
#cite(<Heston1993>, form: "prose") logra una fórmula cerrada gracias a la estructura afín de su
función característica, y de que trabajos previos que introducen cambio de régimen en la
volatilidad de la volatilidad —notablemente He y Zhu (2016)— solo obtienen fórmulas
_aproximadas_ válidas para vencimientos cortos. El objetivo del artículo es construir un modelo
con volatilidad de volatilidad de régimen cambiante que admita una solución cerrada _exacta_.

La dificultad central es que la introducción de la cadena de Markov hace intratable la
derivación directa de la función característica. La solución es un procedimiento en dos etapas
(regla de la torre): primero se obtiene la función característica _condicional_ a la trayectoria
de la cadena, y luego se toma la esperanza sobre la cadena. El resultado principal es una
fórmula cerrada para el precio de la call europea (ec. 2.8 del artículo), con la que la
calibración a datos de mercado resulta computacionalmente eficiente.

= Marco teórico y método

== El modelo

Bajo la medida neutral al riesgo, el precio del subyacente $S_t$ y la varianza $v_t$ siguen

$ (d S_t) / S_t = r thin d t + sqrt(v_t) thin d W_t^1, $

$ d v = k(theta - v) thin d t + sigma sqrt(v) thin d W_t^2 + lambda_(X_t) thin d B_t, $

donde $W^1, W^2$ son brownianos con correlación $rho$, $B_t$ es un browniano independiente, y
$X_t$ es una cadena de Markov de dos estados, independiente de los brownianos, con tasas de
transición $lambda_(12), lambda_(21)$. El nivel de volatilidad de la volatilidad de régimen
$lambda_(X_t)$ toma el valor $lambda_1$ o $lambda_2$ según el estado. Cuando
$lambda_1 = lambda_2 = 0$ el modelo se reduce exactamente al de Heston, propiedad que usamos
como prueba de verificación.

Como reconocen los autores, el término $lambda_(X_t) d B_t$ rompe la condición de Feller: la
varianza puede volverse negativa. Esto se acepta a cambio de tratabilidad analítica y mejor
ajuste, al igual que en otros modelos conocidos (Stein–Stein, rough Heston). Retomamos esta
propiedad en el análisis numérico (Sección 6), pues tiene una consecuencia práctica importante
sobre la fórmula de inversión.

== Valoración por inversión de Gil-Pelaez

Con $y_t = ln S_t$ y $tau = T - t$, el precio de la call europea se expresa mediante el teorema
de Gil-Pelaez #cite(<GilPelaez1951>) como

$ U = e^(-r tau) [ m(-j) thin P_1 - K thin P_2 ], $ <eq-price>

$ P_2 = 1/2 + 1/pi integral_0^(infinity) "Re" [ (e^(-j phi ln K)) / (j phi) m(phi) ] thin d phi,
quad
P_1 = 1/2 + 1/pi integral_0^(infinity) "Re" [ (e^(-j phi ln K)) / (j phi)
(m(phi - j)) / (m(-j)) ] thin d phi, $

donde $m(phi) = EE[e^(j phi y_T)]$ es la función característica de $y_T$ y
$m(-j) = EE[S_T] = S e^((r-q) tau)$. Incorporamos el rendimiento por dividendos $q$ sustituyendo
$r arrow r - q$ en la deriva (extensión respecto del artículo original, justificada en la
Sección 5).

== Función característica en dos etapas

*Etapa 1 (condicional).* Condicionando en la trayectoria de la cadena de Markov, $lambda_(X_t)$
es una función determinista del tiempo $lambda_t$, de modo que no se acopla un sistema de EDPs.
La función característica condicional $h(phi|X_T) = e^(C(phi;tau) + D(phi;tau) v + j phi y)$
satisface, por el teorema de Feynman–Kac, la EDP

$ (partial h) / (partial t) + 1/2 v (partial^2 h) / (partial y^2)
+ 1/2 (sigma^2 v + lambda_t^2) (partial^2 h) / (partial v^2)
+ rho sigma v (partial^2 h) / (partial v partial y)
+ (r - 1/2 v) (partial h) / (partial y) + k(theta - v) (partial h) / (partial v) = 0, $

con condición terminal $h|_(t=T) = e^(j phi y_T)$. Sustituyendo el ansatz afín y agrupando
términos en $v$ se obtienen dos EDOs:

$ (partial D) / (partial tau) = 1/2 sigma^2 D^2 + (j phi rho sigma - k) D - 1/2 (j phi + phi^2),
quad
(partial C) / (partial tau) = 1/2 lambda_t^2 D^2 + k theta D + r j phi. $ <eq-odes>

La ecuación para $D$ es una Riccati de coeficientes constantes con solución cerrada

$ D = (d - a) / sigma^2 (1 - e^(d tau)) / (1 - g thin e^(d tau)), quad
a = j phi rho sigma - k, quad
d = sqrt(a^2 + sigma^2 (j phi + phi^2)), quad
g = (a - d) / (a + d). $ <eq-D>

Integrando la EDO de $C$ (sin el término de régimen) se obtiene la parte de Heston

$ overline(C) = r j phi tau + (k theta) / sigma^2
{ [d - a] tau - 2 ln [ (1 - g e^(d tau)) / (1 - g) ] }. $ <eq-Cbar>

La componente de régimen de $C$ es $1/2 integral_t^T lambda_s^2 D^2(phi; T-s) thin d s$, cuya
forma cerrada se expresa mediante

$ f(phi; tau) = integral_0^tau D(phi; u)^2 thin d u
= 1/sigma^4 { [d-a]^2 tau + 4 a ln[(1 - g e^(d tau)) / (1-g)]
+ (4 d) / (1 - g e^(d tau)) - (4 d) / (1 - g) }. $ <eq-f>

*Etapa 2 (incondicional).* La esperanza sobre la cadena de Markov del término exponencial de
régimen se calcula, siguiendo a #cite(<ElliottLian2013>, form: "prose"), como una exponencial
matricial: $EE[e^(1/2 integral_t^T ⟨lambda_s^2 D^2, X_s⟩ d s) | X_t] = ⟨ e^M X_t, I ⟩$, donde
$I = (1,1)^T$, $X_t in {(1,0)^T, (0,1)^T}$ y

$ M = A^T tau + "diag"(1/2 lambda_1^2 f, thin 1/2 lambda_2^2 f), quad
A = mat(-lambda_(12), lambda_(12); lambda_(21), -lambda_(21)). $ <eq-M>

La función característica final es $m(phi) = e^(overline(C) + D v + j phi y)
⟨ e^M X_t, I ⟩$ (ec. 2.20). El factor de régimen es la suma de la columna de $e^M$
correspondiente al estado actual. En la implementación calculamos $e^M$ para la matriz
$2 times 2$ en forma cerrada por descomposición espectral, y combinamos su exponente con el de
Heston en una sola exponencial por autovalor; esto evita el desbordamiento $0 times infinity$
que aparece en la cola de altas frecuencias (donde el factor de Heston decae mientras el de
régimen crece), problema al que volvemos en la Sección 6.

#block(fill: luma(245), inset: 8pt, radius: 3pt, width: 100%)[
  *Nota sobre erratas del artículo.* Al transcribir las fórmulas detectamos y verificamos
  numéricamente dos erratas tipográficas del texto original: (i) la entrada $(2,2)$ de la matriz
  explícita $M$ aparece como $-lambda_(21)$ sin el factor $tau$, cuando la derivación
  $integral A^T d s = A^T tau$ implica $-lambda_(21) tau$ (usamos esta última); (ii) las
  ecuaciones (2.16) y (2.20) escriben la unidad imaginaria como $i$ en vez de $j$. Ninguna
  afecta la implementación una vez corregidas.
]

= Datos

Calibramos a opciones sobre el S&P 500. El artículo usa opciones europeas del índice (SPX) de
2011; su fuente comercial exacta no es replicable públicamente. Utilizamos en cambio un snapshot
público reciente obtenido con `yfinance`.

*Elección del subyacente.* Un snapshot de opciones del índice `^SPX` tomado fuera del horario de
mercado presenta cotizaciones bid/ask válidas casi exclusivamente para calls dentro del dinero,
lo que impide una calibración representativa. Optamos por opciones de *SPY* (el ETF del S&P 500),
con liquidez amplia en todo el rango de moneyness. La contrapartida es que las opciones de SPY
son americanas; para calls de corto plazo (30–90 días) sobre un subyacente de bajo rendimiento
por dividendos, la prima de ejercicio anticipado es despreciable y la valoración europea es una
buena aproximación (limitación que señalamos en la discusión).

*Filtros* (siguiendo al artículo, Sección 4.1): vencimientos entre 30 y 90 días; moneyness
$|S - K| / K < 10%$; precio de mercado igual al punto medio bid-ask; se descartan cotizaciones
vacías. La tasa libre de riesgo es el T-Bill a 13 semanas (`^IRX`), análogo al T-Bill de 3 meses
del artículo.

*Dividendos.* Estimamos el rendimiento por dividendos $q$ por vencimiento a partir de la paridad
put-call (forward implícito $F$ del par call-put más cercano a ATM, y $q = r - ln(F/S) / tau$).
Este enfoque es autocontenido y consistente con los precios observados.

#figure(
  csv_table("../results/tables/05_resumen_datos.csv", ("Métrica", "Valor")),
  caption: [Resumen del conjunto de datos de mercado (SPY) tras aplicar los filtros del artículo.],
) <tab-datos>

La @fig-sonrisa muestra la superficie de volatilidad implícita del conjunto limpio. Se observa el
_skew_ característico de los índices de renta variable: la volatilidad implícita decrece con el
strike (mayor para opciones dentro del dinero, es decir, con $K$ bajo) y el nivel general varía
con el vencimiento. Esta estructura —que Black–Scholes no puede reproducir con una única
volatilidad— es precisamente la que los modelos de volatilidad estocástica buscan capturar, y por
tanto un banco de prueba adecuado para la calibración.

#figure(
  image("../results/figures/05_sonrisa_volatilidad.png", width: 72%),
  caption: [Volatilidad implícita frente al moneyness $K/S$ por vencimiento (SPY, datos limpios).
    El _skew_ decreciente en el strike es la firma que los modelos de volatilidad estocástica
    pretenden ajustar.],
) <fig-sonrisa>

= Implementación, verificación y calibración

== Implementación

La implementación está en Python (biblioteca `rsheston`), con separación entre la lógica de
valoración (funciones características y cuadratura de Gil-Pelaez), la simulación Monte Carlo, el
pipeline de datos y la calibración. La integral de inversión se evalúa por cuadratura de
Gauss-Legendre truncada. La exponencial de la matriz $2 times 2$ se calcula en forma cerrada
(descomposición espectral) y vectorizada sobre las frecuencias, evitando cientos de llamadas a
una rutina genérica de exponencial matricial por cada precio, lo que es esencial para la
eficiencia de la calibración.

== Verificación

Verificamos la implementación en múltiples niveles independientes:

+ *Degeneración a Heston.* Con $lambda_1 = lambda_2 = 0$, el precio del modelo coincide con el
  de Heston hasta el error de cuadratura, y con $sigma arrow 0$, $v_0 = theta$, el de Heston
  coincide con Black–Scholes. La @fig-degeneracion muestra la transición al variar un factor de
  escala $z$ sobre $lambda_1, lambda_2$.

+ *Validación de $f(phi; tau)$.* La forma cerrada de $integral_0^tau D^2$ (ec. 2.19) coincide
  con su integración numérica directa a tolerancia $10^(-8)$.

+ *Monte Carlo.* Comparamos la fórmula cerrada contra dos simulaciones independientes. La primera
  es una simulación de Euler completa del sistema acoplado $(S, v, X_t)$ bajo truncamiento de la
  varianza en cero (necesario porque el modelo viola Feller); es una verificación totalmente
  independiente de la fórmula, a costa de mayor varianza. La segunda es la _semi-Monte-Carlo_ del
  artículo: se simula únicamente la trayectoria de la cadena de Markov (con tiempos de permanencia
  exponenciales) y, dado el camino, el precio condicional se obtiene con la función característica
  condicional por Gil-Pelaez; el precio final es el promedio de los precios condicionales sobre
  los caminos. Este segundo método tiene varianza mucho menor y valida específicamente el paso de
  la esperanza matricial de Elliott–Lian (ec. 2.17), que es el más propenso a error. La
  @fig-montecarlo y la @tab-mc resumen el acuerdo: el error relativo máximo respecto de la
  semi-Monte-Carlo es del orden de $10^(-3)%$, holgadamente inferior al 0.7% del artículo.

#figure(
  image("../results/figures/01_degeneracion_heston.png", width: 78%),
  caption: [Degeneración al modelo de Heston: al escalar $lambda_1 = 0.3 z$, $lambda_2 = 0.2 z$,
    el precio del modelo se acerca al de Heston y coincide exactamente en $z = 0$.],
) <fig-degeneracion>

#figure(
  image("../results/figures/02_formula_vs_montecarlo.png", width: 100%),
  caption: [Fórmula cerrada frente a Monte Carlo (semi-MC y Euler completo) a lo largo del
    precio del subyacente, y error relativo frente a la cota del 0.7% del artículo.],
) <fig-montecarlo>

#figure(
  csv_table("../results/tables/02_errores_montecarlo.csv",
    ("S", "Fórmula", "semi-MC", "err.est.", "Euler-MC", "err.rel.(%)")),
  caption: [Precios de la fórmula cerrada vs Monte Carlo y error relativo (parámetros de la
    Fig. 1 del artículo).],
) <tab-mc>

== Calibración

Calibramos minimizando el error cuadrático medio en dólares entre precios de mercado y de modelo
(ec. 4.1 del artículo),
$ "MSE" = 1/N sum_(i=1)^N (C_i^"mercado" - C_i^"modelo")^2, $
con optimización global (`scipy.optimize.dual_annealing`, análogo abierto al _adaptive simulated
annealing_ del artículo), pues el objetivo no es convexo. Calibramos con datos in-sample y
evaluamos también fuera de muestra. Las cotas de los parámetros, la semilla y el optimizador se
reportan en el código para reproducibilidad.

La @tab-parametros presenta los parámetros estimados; la @tab-errores, los errores dentro y fuera
de muestra; y la @tab-moneyness, el desglose por moneyness (análogos a las Tablas 1–3 del
artículo).

#figure(
  csv_table("../results/tables/06_parametros.csv", ("Parámetro", "Heston", "Lin & He")),
  caption: [Parámetros estimados (in-sample) para ambos modelos.],
) <tab-parametros>

#figure(
  csv_table("../results/tables/06_errores.csv", ("Modelo", "MSE in-sample", "MSE out-of-sample")),
  caption: [Errores cuadráticos medios dentro y fuera de muestra.],
) <tab-errores>

#figure(
  csv_table("../results/tables/06_errores_moneyness.csv", ("Modelo", "OTM", "ATM", "ITM")),
  caption: [Errores fuera de muestra por moneyness.],
) <tab-moneyness>

#figure(
  image("../results/figures/06_ajuste_calibracion.png", width: 78%),
  caption: [Ajuste de la calibración: precios de mercado vs precios de ambos modelos calibrados
    para el vencimiento más corto (in-sample). Las curvas de Heston y Lin & He se superponen.],
) <fig-ajuste>

= Discusión: análisis numérico y comparación

== Convergencia y truncamiento de la cuadratura

La cuadratura de Gauss-Legendre converge rápidamente en el número de nodos (@fig-nodos). El
aspecto más delicado es el truncamiento superior de la integral. A diferencia de una función
característica genuina, acotada por $1$ en módulo, la función característica _formal_ de este
modelo no está acotada: como consecuencia de la violación de la condición de Feller, el término
de régimen $1/2 lambda^2 f(phi;tau)$ crece cuadráticamente en $phi$ y, aunque el módulo
$|m(phi)|$ decae a frecuencias moderadas, eventualmente _explota_ en la cola (@fig-integrando).
En consecuencia, un truncamiento fijo demasiado grande contamina el precio (@fig-truncamiento).

Resolvemos esto con un truncamiento _adaptativo_ que ubica el límite superior en la región de
decaimiento, antes de la explosión. Para los parámetros calibrados (con $lambda$ pequeño) la
explosión ocurre a frecuencias tan altas que el módulo ya es despreciable, y el precio es estable
para cualquier truncamiento razonable; el fenómeno solo es relevante para valores grandes de
$lambda$. Este comportamiento, que el artículo no discute, es una limitación numérica inherente
al modelo y está directamente ligado a la violación de Feller.

#figure(
  image("../results/figures/04_convergencia_nodos.png", width: 70%),
  caption: [Convergencia del precio frente al número de nodos de Gauss-Legendre.],
) <fig-nodos>

#figure(
  grid(columns: 2, gutter: 6pt,
    image("../results/figures/04_integrando.png"),
    image("../results/figures/04_truncamiento_y_cola.png"),
  ),
  caption: [Izquierda: $|m(phi)|$ decae y luego explota en la cola (violación de Feller).
    Derecha: el precio es estable en una meseta de truncamiento y se corrompe si se trunca en la
    región de explosión; el truncamiento adaptativo lo evita.],
) <fig-integrando>
#figure([], caption: []) <fig-truncamiento>

== Costo computacional

La disponibilidad de la fórmula cerrada hace la valoración órdenes de magnitud más rápida que la
simulación, lo que es esencial para la calibración (miles de evaluaciones del objetivo). El costo
por precio se reporta en `results/tables/04_costo_computacional.csv`.

== Comparación con el artículo

Los parámetros de Heston que estimamos (@tab-parametros) son del mismo orden que los del artículo
(su Tabla 1): reversión $k approx 5.1$ (artículo $8.7$), nivel $theta approx 0.048$ (artículo
$0.082$), volatilidad de volatilidad $sigma approx 1.26$ (artículo $1.41$) y correlación
$rho approx -0.62$ (artículo $-0.31$). Las diferencias son esperables: usamos SPY en 2026 en vez
de SPX en 2011, un único corte transversal en lugar de seis meses de datos, y un optimizador
distinto.

El resultado más relevante es que, en nuestra calibración, *el modelo de Lin & He no mejora al de
Heston*: el optimizador lleva $lambda_1, lambda_2 arrow 0$, con lo que el modelo se reduce
exactamente a Heston y ambos alcanzan el mismo MSE (@tab-errores), con curvas de precio
indistinguibles (@fig-ajuste). Esto contrasta con el artículo, donde el modelo de Lin & He reduce
el MSE en torno a un 45% respecto de Heston.

La explicación es metodológica y, entendemos, instructiva. El artículo calibra un *único* conjunto
de parámetros a un *panel* de seis meses de cotizaciones (miércoles para estimar, jueves para
validar). En ese contexto, un solo Heston debe servir a muchos estados de mercado distintos a lo
largo del tiempo, y el factor de cambio de régimen aporta la flexibilidad para capturar esa
variación temporal. En cambio, nuestra calibración usa un *solo corte transversal* (la superficie
de un día): un único Heston ya ajusta bien esa sonrisa (MSE in-sample de 0.043 sobre 325
opciones), y no hay variación de régimen entre fechas que capturar, de modo que el segundo factor
es innecesario y no está identificado. En otras palabras, la ventaja del cambio de régimen es un
fenómeno de *serie temporal*, no de *corte transversal*, y nuestra limitación de datos (un solo
snapshot) impide reproducir la mejora reportada.

= Conclusiones

Implementamos y verificamos la fórmula cerrada de #cite(<LinHe2021>, form: "prose") para
opciones europeas bajo un modelo de Heston de dos factores con cambio de régimen, y la calibramos
a datos de mercado. Las verificaciones (degeneración a Heston, validación de la integral, y dos
Monte Carlo independientes) confirman la corrección de la implementación. El principal hallazgo
numérico propio es que la función característica del modelo no está acotada a altas frecuencias
—consecuencia directa de la violación de la condición de Feller— lo que exige un truncamiento
cuidadoso de la integral de inversión, aspecto no discutido en el artículo original.

En el estudio empírico, sobre un único corte transversal de opciones de SPY el modelo de Lin & He
se reduce a Heston ($lambda arrow 0$) y no mejora el ajuste, a diferencia del artículo. Atribuimos
esto a que la ventaja del cambio de régimen se manifiesta a lo largo del tiempo (en un panel
multi-fecha) y no dentro de una sola superficie. Las extensiones naturales son, por tanto:
calibrar a un *panel* de varias fechas (que requeriría una fuente de datos históricos de opciones,
no disponible vía la API en vivo usada aquí); calibrar además el modelo de Elliott–Lian como
tercer competidor, como en el artículo; y tratar explícitamente el ejercicio americano de las
opciones de SPY. Estas direcciones permitirían una comparación más fiel con los resultados
originales.

#block(fill: luma(245), inset: 8pt, radius: 3pt, width: 100%)[
  *Declaración de uso de IA.* Este trabajo se apoyó en herramientas de IA (asistente de
  programación) para la implementación, la depuración y la redacción. La responsabilidad
  intelectual y la comprensión de los resultados son de los autores.
]

#bibliography("refs.bib", title: "Referencias", style: "american-psychological-association")

#pagebreak()

= Anexo A: fragmentos de código clave <anexo>

Extractos del paquete `rsheston` (implementación completa reproducible en el repositorio; ver
`README.md` para el mapa script → figura/tabla).

*Función característica del modelo (forma estable, `charfn.py`).*

```python
def linhe_cf(phi, *, S, tau, r, params, state=1, q=0.0):
    a, d, g, edt = heston_core(phi, tau, params.kappa, params.theta,
                               params.sigma, params.rho)
    D = heston_D(a, d, g, edt, params.sigma)
    Cbar = heston_Cbar(a, d, g, edt, tau, params.kappa, params.theta, params.sigma)
    f = linhe_f(a, d, g, edt, tau, params.sigma)
    M11, M12, M21, M22 = linhe_M_entries(f, tau, params)
    half_T = 0.5 * (M11 + M22); delta = 0.5 * (M11 - M22)
    s = np.sqrt(delta**2 + M12 * M21)          # autovalores mu± = T/2 ± s
    num = (delta + M21) if state == 1 else (M12 - delta)
    H = Cbar + (r - q) * 1j * phi * tau + D * params.v0 + 1j * phi * np.log(S)
    beta = num / s
    # Combinación estable (evita 0*inf en la cola): un exp por autovalor.
    return 0.5*(1+beta)*np.exp(H + half_T + s) + 0.5*(1-beta)*np.exp(H + half_T - s)
```

*Inversión de Gil-Pelaez con truncamiento adaptativo (`pricing.py`).*

```python
def gil_pelaez_call(cf, S, K, r, tau, q=0.0, u_max=200.0, n_nodes=256, adaptive=True):
    if adaptive:
        u_max = adaptive_truncation(cf, u_cap=u_max)   # trunca en la región de decaimiento
    x, w = _leggauss_cached(n_nodes)
    phi = 0.5 * u_max * (x + 1.0); weights = 0.5 * u_max * w
    m_neg_j = S * np.exp((r - q) * tau)                # = E[S_T], evita la singularidad en -j
    kernel = np.exp(-1j * phi * np.log(K)) / (1j * phi)
    P2 = 0.5 + np.sum(weights * np.real(kernel * cf(phi))) / np.pi
    P1 = 0.5 + np.sum(weights * np.real(kernel * cf(phi - 1j) / m_neg_j)) / np.pi
    return float(np.real(np.exp(-r * tau) * (m_neg_j * P1 - K * P2)))
```
