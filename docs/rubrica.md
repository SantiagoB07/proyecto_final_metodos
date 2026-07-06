Métodos Numéricos en Finanzas

Proyecto Final de Aplicación

# Proyecto Final de Aplicación

## Métodos Numéricos en Finanzas

Maestría en Actuaría y Finanzas (MAF)

Departamento de Matemáticas — Facultad de Ciencias

Universidad Nacional de Colombia, Sede Bogotá

Prof. Oscar Javier López Alfonso · 2026-I

**Síntesis.** En grupos, los estudiantes leerán, comprenderán e **implementarán** un artículo de investigación que proponga un **modelo de valoración de opciones con solución semianalítica** (típicamente vía función característica, transformada de Fourier/FFT, método COS, cuadratura numérica o expansiones en serie), **implementándolo y calibrándolo a datos de mercado reales**. El proyecto consta de cuatro entregables: (i) un trabajo escrito tipo artículo de investigación, (ii) el código reproducible, (iii) las diapositivas y (iv) una exposición oral.

### 1. Objetivos del proyecto

**Objetivo general.** Desarrollar la capacidad de leer críticamente, comprender en profundidad e implementar computacionalmente un artículo de investigación en métodos numéricos para finanzas, articulando la formulación del modelo, su solución semianalítica, la calibración a datos reales y la comunicación de resultados.

#### Objetivos específicos.

- Reconstruir el marco teórico del artículo asignado: dinámica del subyacente, problema de valoración y la **solución semianalítica** (función característica, fórmula de inversión de Fourier, FFT, método COS, cuadratura, etc.).
- Implementar el método de valoración de forma reproducible y **verificar su corrección** (p. ej. contra Black-Scholes en el caso límite, contra precios de referencia o por convergencia).
- **Calibrar el modelo a datos de mercado reales** (superficie de volatilidad implícita o precios de opciones cotizadas) y evaluar la calidad del ajuste.
- Analizar los aspectos **numéricos** del método: convergencia, estabilidad, elección de parámetros (rango de truncamiento, número de términos/nodos, factor de amortiguación) y costo computacional.
- Comunicar los hallazgos por escrito (formato artículo) y oralmente (exposición con diapositivas) con rigor y claridad.

### 2. Modalidad y conformación de grupos

El trabajo es **grupal**. Los grupos ya están conformados y a cada uno ya se le asignó un artículo distinto, calibrado por dificultad según el tamaño del grupo.

Página 1 de 5

Métodos Numéricos en Finanzas

Proyecto Final de Aplicación

**Confirmación de la asignación (acción requerida).** Para dejar el registro formal de la asignación, cada grupo debe publicar en Google Classroom, a más tardar el viernes 19 de junio de 2026, un aviso que **recuerde al profesor el artículo que le fue asignado**, indicando:

1. Integrantes del grupo (nombres completos).
2. Artículo asignado: **autores, año, título, revista/fuente y DOI**.
3. Fuente de datos de mercado que se usará para la calibración.

Cualquier ajuste del artículo o de la fuente de datos debe acordarse con el profesor en el mismo plazo.

Para referencia, una vez recibidos los avisos la asignación quedará registrada así:

|  Grupo | Int. | Artículo asignado (reportado por el grupo) | Datos de calibración  |
| --- | --- | --- | --- |
|  G1 | — |  |   |
|  G2 | — |  |   |
|  G3 | — |  |   |
|  G4 | — |  |   |
|  G5 | — |  |   |

### 3. Entregables

Cada grupo entrega **cuatro** componentes. Todos deben subirse al espacio del curso en Google Classroom en los plazos indicados (Sección 4).

#### 3.1. Trabajo escrito (formato artículo de investigación)

Documento autocontenido, escrito preferentemente en $\LaTeX$, que reporte la implementación y la calibración. Estructura sugerida:

1. **Resumen** (150–250 palabras) y palabras clave.
2. **Introducción:** contexto de los métodos numéricos en valoración de opciones, motivación y aporte del artículo base.
3. **El artículo base:** modelo, problema de valoración, hipótesis y resultado principal (la solución semianalítica).
4. **Marco teórico y método:** formalización de la dinámica del subyacente, función característica y fórmula de valoración (inversión de Fourier/FFT, COS, cuadratura...), con la notación necesaria.
5. **Datos:** descripción de los **datos de mercado** (fuente pública, fecha de cotización, subyacente, *strikes* y vencimientos, tasa libre de riesgo y dividendos, limpieza), incluyendo justificación de por qué son adecuados.
6. **Implementación, verificación y calibración:** detalles de cómputo, verificación de la implementación, **calibración** a los datos de mercado, tablas y figuras (ajuste de la superficie, errores de precios o de volatilidad implícita).

Página 2 de 5

Métodos Numéricos en Finanzas

Proyecto Final de Aplicación

7. **Discusión:** análisis numérico (convergencia, estabilidad, costo), comparación crítica con los resultados del artículo original; sensibilidad y limitaciones.
8. **Conclusiones** y posibles extensiones.
9. **Referencias** (estilo consistente; se sugiere BIBTEX).
10. **Anexos:** fragmentos de código clave y resultados complementarios.

**Especificaciones.** Extensión: **12–20 páginas** (sin contar anexos). Formato: Carta, fuente 11–12pt, ecuaciones numeradas, figuras y tablas con leyenda y referencia en el texto. Entrega en **PDF**; se valora la entrega adicional de las fuentes LaTeX.

### 3.2. Código

Repositorio o carpeta con todo el código necesario para **reproducir de principio a fin** las tablas y figuras del trabajo. Requisitos:

- Lenguaje libre (**Python** o **R** recomendados); estructura ordenada y comentada.
- Archivo **README** con: descripción, dependencias/versiones, instrucciones de ejecución y mapa “script → figura/tabla del documento”.
- Script o instrucciones para **obtener los datos de mercado** (o los datos incluidos si su licencia lo permite).
- Reproducibilidad: fijar semillas aleatorias cuando aplique; reportar el optimizador y los valores iniciales de la calibración; evitar rutas absolutas.
- Si se reutiliza código o paquetes de terceros (p. ej. **numpy/scipy**, **QuantLib**, rutinas de FFT o de calibración), debe citarse, y el grupo debe **comprender y poder explicar** el núcleo del método, no solo invocar la función.

### 3.3. Diapositivas

Material de apoyo para la exposición (se sugiere **BEAMER** u otra herramienta). Orientativo: **15–20** diapositivas que cubran motivación, modelo y método, datos, resultados de la calibración, comparación con el original y conclusiones. Entrega en **PDF**.

### 3.4. Exposición oral

Presentación grupal de **20 minutos por grupo**, seguida de preguntas. **Todos** los integrantes deben intervenir. Se evaluará el dominio del tema, la claridad y la capacidad de responder preguntas conceptuales y de implementación.

Página 3 de 5

Métodos Numéricos en Finanzas

Proyecto Final de Aplicación

#### 4. Cronograma

|  Hito | Fecha  |
| --- | --- |
|  Confirmación de integrantes y reporte del artículo asignado (aviso en Classroom) | viernes 19 de junio de 2026  |
|  Avance intermedio (datos de mercado listos + valoración implementada y verificada) | miércoles 1 de julio de 2026  |
|  Entrega de trabajo escrito, código y diapositivas | martes 7 de julio de 2026  |
|  Exposiciones orales | miércoles 8 de julio de 2026 (horario de clase)  |

El **avance intermedio** es breve (1–2 páginas o correo estructurado): fuente de datos confirmada, valoración implementada y verificada (aún sin calibrar o con calibración preliminar) y dificultades encontradas. Su objetivo es detectar a tiempo bloqueos de datos o de método.

#### 5. Evaluación

La nota del proyecto se distribuye así (los porcentajes pueden ajustarse a criterio del profesor):

|  Criterio | Peso  |
| --- | --- |
|  Trabajo escrito (rigor, claridad, estructura, discusión crítica) | 35 %  |
|  Código y reproducibilidad (corre de principio a fin; documentación) | 20 %  |
|  Corrección de la implementación y calibración (valoración fiel del método y ajuste a datos reales) | 20 %  |
|  Exposición y diapositivas (claridad, manejo del tiempo, calidad visual) | 15 %  |
|  Comprensión teórica (respuestas a preguntas; dominio individual) | 10 %  |
|  **Total** | **100 %**  |

La nota es mayoritariamente grupal, pero el profesor podrá **modular la nota individual** con base en el desempeño en la exposición y en las preguntas, para reflejar la contribución de cada integrante.

#### 6. Normas de integridad académica

- Todo material de terceros (texto, código, datos, figuras) debe **citarse** apropiadamente. La reproducción no atribuida de texto o código constituye plagio.
- Se permite el uso de bibliotecas y código público, siempre que se cite y el grupo comprenda y pueda explicar su funcionamiento.

Página 4 de 5

Métodos Numéricos en Finanzas

Proyecto Final de Aplicación

- Si se emplean herramientas de IA como apoyo (depuración, redacción), debe declararse su uso de forma breve en una nota; la responsabilidad intelectual y la comprensión de los resultados son del grupo.
- Los datos utilizados deben respetar las licencias de uso de su fuente.

Página 5 de 5
