# MÉTODOS NUMÉRICOS EN FINANZAS

Código: 2026377

Primer semestre de 2026

![img-0.jpeg](img-0.jpeg)

**Oscar Javier López Alfonso**

ojlopeza@unal.edu.co

**Horario de clase:** lunes y miércoles de 5:00 p.m. a 7:00 p.m.

**Salón:** 216 sala de cómputo matemáticas – edificio 405.

**Atención a estudiantes:** Únicamente con cita previa concertada por correo electrónico.

## Descripción del curso

Este curso ofrece una formación avanzada en los principales **métodos numéricos utilizados en la valoración de instrumentos financieros derivados**, con énfasis en la formulación de modelos bajo la medida neutral al riesgo y en la implementación computacional de algoritmos de valoración. A partir de un repaso estructurado de procesos estocásticos y modelos financieros fundamentales, el curso desarrolla de manera progresiva técnicas discretas y continuas para la solución de problemas de valoración, incluyendo árboles binomiales, simulación Monte Carlo, métodos basados en transformadas, ecuaciones diferenciales parciales (PDE) y ecuaciones integro-diferenciales parciales (PIDE).

El curso se apoya principalmente en el libro *Computational Methods in Finance* de Ali Hirsa y en los trabajos de investigación del profesor, complementándolo con contenidos no cubiertos explícitamente en el texto —como los modelos de árboles binomiales— y con extensiones contemporáneas basadas en simulación avanzada y redes neuronales. A lo largo del semestre, los estudiantes integran teoría y práctica mediante la programación de algoritmos en lenguajes de alto nivel (Python, MATLAB o R), el análisis crítico de resultados numéricos y la comparación entre distintos enfoques de valoración.

Al finalizar el curso, el estudiante estará en capacidad de seleccionar, implementar y evaluar críticamente métodos numéricos apropiados para distintos tipos de derivados y modelos financieros, entendiendo tanto sus fundamentos matemáticos como sus limitaciones computacionales y de modelación.

## Propósitos de formación del curso

Al finalizar el curso, el estudiante estará en capacidad de:

1. **Comprender y aplicar los fundamentos de la valoración neutral al riesgo**, reconociendo el papel de los procesos estocásticos y del cambio de medida en la modelación financiera.

2. **Formular problemas de valoración de derivados** bajo distintos modelos de precios de activos y tasas de interés.
3. **Implementar métodos numéricos discretos y continuos** para la valoración de instrumentos financieros, incluyendo árboles, simulación Monte Carlo, métodos de transformadas y esquemas de diferencias finitas.
4. **Resolver ecuaciones diferenciales parciales e integro-diferenciales** asociadas a problemas de valoración, analizando estabilidad, convergencia y precisión numérica.
5. **Comparar críticamente distintos métodos de valoración**, identificando ventajas, limitaciones y contextos de aplicación.
6. **Desarrollar habilidades computacionales avanzadas**, integrando teoría financiera, métodos numéricos y programación científica.
7. **Explorar metodologías modernas de valoración**, como técnicas basadas en aprendizaje automático, y evaluar su desempeño frente a métodos tradicionales.
8. **Comunicar de forma clara y rigurosa resultados numéricos**, tanto en informes escritos como en presentaciones técnicas.

## Prerrequisitos

Para un adecuado aprovechamiento del curso, se espera que el estudiante cuente con:

- Conocimientos de **cálculo diferencial e integral**, incluyendo derivadas parciales.
- Conocimientos básicos de **álgebra lineal**, en particular sistemas de ecuaciones y operaciones matriciales.
- Fundamentos de **probabilidad y estadística**, incluyendo variables aleatorias, distribuciones y esperanza matemática.
- Conocimientos introductorios de **finanzas cuantitativas**, especialmente valoración básica de opciones y nociones de tasas de interés.
- Habilidad de **programación en un lenguaje de alto nivel** (Python, MATLAB o R), incluyendo manejo de arreglos, funciones y visualización de resultados.

## Contenidos generales

### A. Fundamentos de modelación financiera y procesos estocásticos

- Revisión de procesos estocásticos relevantes en finanzas.
- Movimiento browniano, procesos de Poisson y procesos con saltos.
- Modelos clásicos de precios de activos.
- Medida neutral al riesgo y principios de valoración sin arbitraje.
- Clasificación general de métodos de valoración de derivados.

### B. Métodos discretos de valoración

- Árboles binomiales y su relación con modelos continuos.
- Valoración de opciones europeas y americanas mediante árboles.
- Convergencia de modelos discretos a modelos continuos.
- Comparación entre métodos discretos y analíticos.

### C. Simulación Monte Carlo para valoración de derivados

- Fundamentos de simulación y generación de números aleatorios.
- Valoración de opciones europeas mediante Monte Carlo.
- Error de simulación y análisis estadístico de resultados.
- Extensiones a opciones dependientes de la trayectoria.
- Introducción a técnicas de reducción de varianza.

### D. Métodos basados en transformadas

- Funciones características y su uso en valoración.
- Transformada de Fourier y Fast Fourier Transform (FFT).
- Métodos de valoración basados en transformadas.
- Aplicaciones a modelos con saltos y procesos de Lévy.

### E. Valoración mediante ecuaciones diferenciales parciales

- Derivación de ecuaciones PDE en finanzas.
- Métodos de diferencias finitas:
  - esquemas explícitos,
  - implícitos,
  - Crank–Nicolson.
- Condiciones de frontera y estabilidad numérica.
- Valoración de opciones americanas y exóticas.

### F. Valoración mediante ecuaciones integro-diferenciales parciales

- Motivación de las PIDEs en modelos con saltos.
- Estructura general de una PIDE de valoración.
- Discretización del término integral.
- Ejemplos de modelos de salto-difusión.

### G. Métodos avanzados y enfoques modernos

- Simulación avanzada de ecuaciones diferenciales estocásticas.
- Métodos de regresión para opciones americanas.
- Redes neuronales para valoración de derivados.
- Comparación entre métodos tradicionales y basados en aprendizaje automático.

### H. Calibración y extensiones

- Introducción a la calibración de modelos financieros.
- Formulación de problemas de calibración.
- Discusión sobre riesgo de modelo.
- Integración de métodos y aplicaciones prácticas.

## Metodología y Evaluación

### Metodología

El curso se desarrollará bajo un **enfoque teórico–práctico**, combinando exposiciones conceptuales con sesiones de laboratorio orientadas a la implementación computacional de métodos numéricos para la valoración de derivados financieros. Los ejemplos y casos de estudio se basarán

principalmente en el texto de Hirsa y en literatura académica reciente. Se promoverá el trabajo colaborativo mediante talleres y un proyecto final integrador.

### Evaluación

La evaluación será **continua y acumulativa**, y contemplará la comprensión teórica, la implementación computacional y el análisis crítico de los métodos estudiados. Los componentes y ponderaciones serán:

|  Componente | Peso  |
| --- | --- |
|  Talleres computacionales (3) | 30%  |
|  Evaluación intermedia (teórico–práctica) | 20%  |
|  Proyecto final | 40%  |
|  Participación académica | 10%  |
|  **Total** | **100%**  |

### Nota final y recomendaciones para el éxito en el curso

Una vez publicada, **la nota final es definitiva**. Solo se aceptarán reclamaciones por errores estrictamente numéricos en el registro de calificaciones. Solicitudes de reconsideración basadas en apreciaciones personales o situaciones no académicas no serán atendidas.

Cualquier duda o solicitud relacionada con las calificaciones deberá ser enviada exclusivamente por **correo electrónico**, de forma clara, respetuosa y debidamente sustentada. Peticiones sin justificación académica, que busquen “alternativas” para mejorar la nota obtenida sin el respaldo de un trabajo riguroso durante el semestre, serán consideradas improcedentes.

#### La verdadera fórmula del éxito en este curso:

- Participar activamente en las sesiones presenciales.
- Preparar con seriedad el material asignado (videos, lecturas, casos, etc.).
- Realizar los ejercicios y tareas con disciplina y compromiso.
- Estudiar al menos **8 horas semanales** por fuera del aula.
- Asumir la responsabilidad personal del proceso de aprendizaje y de los resultados obtenidos.
- Comprender que en este curso **no existen atajos**: solo se logra un buen desempeño con esfuerzo, constancia y dedicación durante TODO el semestre.

### Otros aspectos

#### Puntualidad:

Las clases presenciales comenzarán puntualmente. En caso de fuerza mayor que impida al profesor dictar una sesión, esta será reprogramada en un horario diferente, de común acuerdo con los estudiantes.

#### Fechas importantes para tener en cuenta

- Cancelación de asignaturas con pérdida de créditos: Desde el 16 febrero 2026 hasta el 27 marzo 2026. (*A través del portal académico del SIA.*)

- Finalización de clases: 30 de mayo de 2026 (Resolución 1231 de 2025 de Rectoría).
- Reporte del 100% de calificaciones al SIA: Hasta las 8:00 p.m. del 9 de junio de 2026 (Resolución 1231 de 2025 Rectoría).

# Finalización del semestre

El semestre culmina oficialmente cuando la nota final del curso sea registrada en el SIA, a más tardar el 9 de junio de 2026, siempre y cuando todo transcurra con normalidad. Los estudiantes no deben programar vacaciones ni compromisos académicos o laborales antes de esta fecha, ya que el profesor podrá utilizar este periodo para programar evaluaciones, entregas de talleres, exposiciones o cualquier otra actividad pendiente.

# Bibliografía básica y complementaria

# Básica:

- Ali Hirsa. Computational Methods in Finance. 2. ed. Boca Raton, FL: CRC Press (Taylor & Francis Group), 2024.

# Complementaria:

- Paolo Brandimarte. Numerical Methods in Finance and Economics: A MATLAB-Based Introduction. 2. ed. Hoboken, NJ: John Wiley & Sons, Inc., 2006.
- Daniel J. Duffy. Numerical Methods in Computational Finance: A PDE/FDM Approach. Chichester, UK: John Wiley & Sons Ltd., 2022.
- Rituparna Sen y Sourish Das. Computational Finance with R. Indian Statistical Institute Series. Singapore: Springer Nature Singapore Pte Ltd., 2023.
- Artículos y trabajos de investigación recientes (p. ej., métodos para opciones con barreras y modelos de saltos).

# Cursos en línea recomendados

- Coursera – Financial Engineering and Computational Methods
