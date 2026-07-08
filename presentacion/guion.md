# Guion de exposición — Valoración de opciones con modelo Heston de dos factores y cambio de régimen

**Artículo base:** Lin & He (2021), *Analytically Pricing European Options under a New Two-Factor Heston Model with Regime Switching*, Computational Economics.

**Formato:** 20 minutos + preguntas. Los tres integrantes intervienen. 14 diapositivas (`slides/index.html`).

**Idea rectriz del guion:** contar la historia, no derivar las fórmulas. Cada vez que aparece una ecuación en pantalla, la mencionamos como "una fórmula cerrada" o "esta cuenta" y explicamos *qué hace* y *por qué importa*, no cómo se deduce. Guardamos el detalle técnico para las preguntas.

---

## Reparto y tiempos

| Bloque | Diapositivas | Quién | Tiempo |
| --- | --- | --- | --- |
| Motivación y modelo | 1–5 | **Santiago** | ~6 min |
| Método y verificación | 6–10 | **Julián** | ~7 min |
| Datos, calibración y resultados | 11–14 | **Juan Diego** | ~7 min |

> Regla de oro: si una diapositiva te toma más de 1 minuto y medio, estás entrando en demasiado detalle. Avanza.

---

## BLOQUE 1 — Santiago (diapositivas 1–5, ~6 min)

### Diapositiva 1 — Portada (~30 s)
> "Buenas. Somos Santiago, Julián y Juan Diego. Nuestro proyecto fue implementar, verificar y calibrar a datos reales el modelo de valoración de opciones de Lin y He, de 2021. Es una extensión del modelo clásico de Heston que le agrega la idea de que el mercado cambia de 'régimen'. Voy a empezar por la motivación: por qué hace falta un modelo así."

### Diapositiva 2 — Motivación: la sonrisa de volatilidad (~1:15)
Mensaje central: **el modelo más simple (Black–Scholes) no cuadra con lo que se ve en el mercado.**
> "El modelo de referencia para valorar opciones es Black–Scholes. Tiene un supuesto cómodo: que la volatilidad del activo es constante. El problema es que, cuando uno mira los precios reales del mercado y despeja qué volatilidad estaban implicando, no sale un número plano: sale esta curva —la llamada *sonrisa de volatilidad*. La volatilidad implícita depende del precio de ejercicio."
>
> "En la gráfica se ve justo eso, con datos reales del S&P 500. Esto nos dice que necesitamos un modelo donde la volatilidad no sea fija, sino que se mueva. Ahí entra Heston."

*No entrar en:* qué es volatilidad implícita formalmente, ni cómo se invierte Black–Scholes. Basta con "el número de volatilidad que el mercado le está poniendo a cada opción".

### Diapositiva 3 — De Heston al cambio de régimen (~1:15)
Mensaje central: **la historia en tres pasos — Heston mejora, pero todavía se queda corto; el régimen es el siguiente paso.**
> "Heston fue un gran avance: deja que la volatilidad sea aleatoria y aun así permite una fórmula de precios. Pero Heston con parámetros fijos sigue ajustando de forma imperfecta, porque en la vida real el mercado pasa por etapas: momentos de calma y momentos de crisis. A eso le decimos *cambio de régimen*."
>
> "Ya había intentos de meter esto —He y Zhu en 2016— pero solo lograban una fórmula aproximada. El aporte de Lin y He es lograrlo con una fórmula **cerrada y exacta**. Eso es importante en la práctica porque calibrar el modelo exige valorar miles de opciones; con fórmula cerrada es rápido, con métodos numéricos puros sería lentísimo."

### Diapositiva 4 — El modelo (~1:15)
Mensaje central: **traducir las dos ecuaciones a palabras. No leer símbolo por símbolo.**
> "Sin entrar en el detalle de las ecuaciones, el modelo tiene dos partes. La primera describe cómo se mueve el precio del activo. La segunda describe cómo se mueve la volatilidad, y tiene dos motores: uno es el de Heston de siempre —la volatilidad tiende a volver a un promedio—, y el otro es nuevo: un término, lambda, que **cambia de valor según el régimen** en que esté la economía, controlado por una cadena de Markov de dos estados."
>
> "Dos consecuencias que sí vale la pena resaltar: primero, si apagamos ese término nuevo (lambda igual a cero), recuperamos exactamente el Heston clásico —el modelo lo contiene como caso particular. Y segundo, ese término tiene un costo teórico: rompe una condición técnica (la de Feller) que garantizaba que la volatilidad nunca fuera negativa. Los autores lo asumen a cambio de mejor ajuste, y nosotros tuvimos que lidiar con eso en el código."

*No entrar en:* la forma exacta de la cadena de Markov ni la condición de Feller. Si preguntan, está en preguntas.md.

### Diapositiva 5 — El reto: función característica en dos etapas (~1:15)
Mensaje central: **por qué el problema es difícil y cuál es el truco.**
> "¿Por qué es difícil resolver esto? Porque tenemos dos fuentes de aleatoriedad mezcladas: la volatilidad y, encima, un régimen que salta al azar. Atacarlo de frente es intratable."
>
> "El truco de los autores —y esto es el corazón del artículo— es separar el problema en dos etapas. Primero congelan el régimen: 'supongamos que ya sabemos cómo saltó la economía'. Con eso el problema se vuelve manejable. Y después promedian sobre todas las formas posibles en que pudo saltar el régimen. Julián va a explicar cada una de esas dos etapas."

**Transición:** *"Te dejo con la parte del método, Julián."*

---

## BLOQUE 2 — Julián (diapositivas 6–10, ~7 min)

> Aviso para este bloque: son las diapositivas más técnicas. La meta **no** es que el público siga el álgebra, sino que entienda *qué se resuelve en cada etapa* y que *nosotros lo implementamos y verificamos*. Habla de las fórmulas como "el resultado de esta etapa es una expresión cerrada que sí programamos".

### Diapositiva 6 — Etapa 1: función característica condicional (~1:15)
> "Gracias, Santiago. Primera etapa: con el régimen ya fijado, usamos una herramienta estándar en finanzas para llegar a una ecuación que sabemos resolver —una ecuación de tipo Riccati. Lo importante: tiene **solución cerrada**. No hay que integrar numéricamente esta parte; queda una fórmula explícita. Esa fórmula es la que describe el comportamiento del precio dentro de un régimen dado."

*No entrar en:* Feynman–Kac, el ansatz exponencial ni cómo se resuelve la Riccati. Es "una ecuación clásica con solución conocida".

### Diapositiva 7 — Etapa 2: esperanza sobre la cadena (~1:30)
> "Segunda etapa: ahora sí promediamos sobre todos los caminos posibles del régimen. Aquí usamos un resultado de Elliott y Lian que convierte ese promedio —que suena imposible— en algo muy compacto: una **exponencial de una matriz de 2×2**. Es decir, todo el efecto de que el mercado salte entre dos estados se resume en una operación con una matriz pequeña."
>
> "En la implementación esto lo resolvimos en forma cerrada usando los autovalores de esa matriz, y tuvimos cuidado numérico para que no se desbordaran los números al combinarlo con la parte de Heston. Ese fue uno de los puntos finos del código."

### Diapositiva 8 — Precio por inversión de Gil-Pelaez (~1:15)
Mensaje central: **de la función característica al precio de la opción.**
> "Con las dos etapas ya tenemos lo que se llama la *función característica*, que es como una huella digital de la distribución del precio futuro. El último paso es recuperar el precio de la opción a partir de esa huella. Eso se hace con una fórmula de inversión —la de Gil-Pelaez— que en la práctica es una integral que resolvemos numéricamente con cuadratura de Gauss."
>
> "Un detalle que manejamos con cuidado: esa integral tiene una singularidad en el origen, y la resolvimos usando un valor analítico exacto en ese punto en lugar de dejar que el computador tropezara ahí."

*No entrar en:* la deducción de P1 y P2. "Dos probabilidades que salen de la misma integral."

### Diapositiva 9 — Verificación (1): degeneración a Heston (~1:15)
Mensaje central: **primera prueba de que el código está bien.**
> "Ahora, ¿cómo sabemos que lo implementamos bien? Hicimos dos verificaciones. La primera: si apagamos el término de régimen, el modelo *tiene* que dar exactamente lo mismo que Heston. Y si además apagamos la volatilidad estocástica, tiene que dar Black–Scholes. La gráfica muestra que efectivamente convergen: las curvas se pegan. Eso confirma que los casos límite están correctos."

### Diapositiva 10 — Verificación (2): Monte Carlo (~1:30)
Mensaje central: **segunda prueba, independiente de la fórmula.**
> "La segunda verificación es más fuerte: comparar contra una simulación de Monte Carlo, que no usa nuestra fórmula para nada. Simulamos miles de trayectorias del precio y promediamos. Si la fórmula cerrada y la simulación coinciden, es muy improbable que ambas estén mal de la misma manera."
>
> "Y coinciden muy bien: nuestro error relativo máximo fue del orden de milésimas de por ciento, incluso mejor que el 0.7% que reporta el artículo. Con esto quedamos seguros de que la implementación es fiel. Juan Diego sigue con la parte de datos reales."

**Transición:** *"Con el modelo ya verificado, te paso a los datos, Juan Diego."*

---

## BLOQUE 3 — Juan Diego (diapositivas 11–14, ~7 min)

### Diapositiva 11 — Datos de mercado: panel de 6 meses (~1:30)
Mensaje central: **qué datos usamos y por qué, siendo honestos con las diferencias frente al artículo.**
> "Gracias, Julián. Para calibrar con datos reales usamos opciones sobre el S&P 500. El artículo usa el índice directamente; nosotros usamos el ETF SPY, porque el índice fuera del horario de mercado solo nos daba datos poco útiles."
>
> "Y algo importante: no calibramos un solo día, sino un **panel de seis meses**, tal como en el artículo. Elegimos los miércoles para calibrar y los jueves siguientes para probar fuera de muestra. Aplicamos los mismos filtros del artículo: opciones entre 30 y 90 días, cercanas al precio actual, y precio medio entre compra y venta. Terminamos con unas 40 opciones por fecha."
>
> "Una limitación que reconocemos: las opciones de SPY son americanas, no europeas, pero en plazos cortos se comportan casi igual, así que la aproximación es razonable."

### Diapositiva 12 — Calibración (~1:15)
Mensaje central: **qué significa calibrar, sin tecnicismos de optimización.**
> "Calibrar significa buscar los parámetros del modelo que hacen que sus precios se parezcan lo más posible a los precios reales del mercado. Medimos ese parecido con el error cuadrático medio y lo minimizamos con un optimizador global."
>
> "Un detalle de diseño: arrancamos la calibración del modelo completo desde la solución de Heston. Eso garantiza que el modelo nuevo nunca puede ajustar peor que Heston —en el peor caso, apaga el término de régimen y los iguala. Así la comparación es justa."

### Diapositiva 13 — Resultados del panel (~1:30)
Mensaje central: **el resultado principal — el modelo con régimen gana, aunque por poco.**
> "Estos son los resultados. En muestra, el modelo de Lin y He ajusta mejor que Heston: un error menor, alrededor de un 4% mejor en promedio, y gana en el 52% de las fechas. El parámetro de régimen sale positivo, con el mismo signo que reporta el artículo. Fuera de muestra también queda ligeramente adelante."
>
> "O sea: reproducimos el resultado del artículo en la **dirección** —el régimen sí aporta—, aunque la magnitud de la mejora es menor en nuestro caso. En la última diapositiva explico por qué."

### Diapositiva 14 — Discusión: comparación con el artículo (~1:30)
Mensaje central: **cierre honesto — por qué nuestra mejora es más pequeña, y qué aprendimos.**
> "¿Por qué nosotros vemos una mejora del 4% y el artículo del 45%? La razón principal es el período. El artículo usa datos de 2011, con la crisis europea de por medio: mucho cambio de régimen, justo donde este modelo brilla. Nosotros usamos 2026, un período mucho más calmo, con menos régimen que capturar. También tuvimos menos opciones por fecha."
>
> "Un hallazgo que nos pareció valioso: en un solo día, la calibración lleva el término de régimen casi a cero y el modelo se reduce a Heston. La ventaja del régimen **solo aparece cuando se mira el panel completo de fechas** —es un fenómeno entre fechas, no de un día aislado. Por eso el diseño de panel del artículo es esencial."
>
> "En resumen: implementamos el modelo desde cero, lo verificamos por dos vías independientes, lo calibramos a datos reales y confirmamos su aporte de forma honesta. Muchas gracias; quedamos atentos a sus preguntas."

---

## Cierre y manejo de preguntas
- Cualquiera puede responder, pero idealmente responde quien expuso ese bloque.
- Si una pregunta se va a lo muy técnico (Feller, Riccati, Gil-Pelaez, erratas del artículo), ver `preguntas.md`.
- Si no sabemos algo, ser honestos: "no lo verificamos, pero lo esperable sería…".

## Chequeo final antes de exponer
- [ ] Ensayar una vez completo con cronómetro (meta: 18–19 min para dejar margen).
- [ ] Confirmar que las gráficas se ven bien en el proyector (contraste, tamaño de letra).
- [ ] Tener el PDF `slides/slides.pdf` como respaldo por si falla internet (las fórmulas cargan de un CDN).
- [ ] Declarar el uso de IA y la división del trabajo (lo pide la rúbrica).
