// Trabajo escrito — Proyecto final Métodos Numéricos en Finanzas
// Compilar: typst compile paper/main.typ paper/main.pdf
// Vista previa en vivo: typst watch paper/main.typ

#set page(paper: "us-letter", numbering: "1", margin: 2.5cm)
#set text(size: 11pt, lang: "es", font: "New Computer Modern")
#set par(justify: true)
#set math.equation(numbering: "(1)")
#set heading(numbering: "1.")

#align(center)[
  #text(17pt, weight: "bold")[
    Valoración analítica de opciones europeas bajo un modelo Heston de dos
    factores con cambio de régimen
  ]

  #v(0.5em)
  #text(12pt)[Implementación, verificación y calibración a datos de mercado]

  #v(1em)
  Proyecto final · Métodos Numéricos en Finanzas \
  Maestría en Actuaría y Finanzas · Universidad Nacional de Colombia · 2026-I
]

#v(1em)

#align(center)[
  #box(width: 85%)[
    #set text(size: 10pt)
    #align(left)[
      *Resumen.* // TODO (150-250 palabras): modelo, método semianalítico,
      // verificación, calibración y hallazgo principal.

      *Palabras clave:* volatilidad estocástica · dos factores · cambio de régimen ·
      función característica · Gil-Pelaez · calibración.
    ]
  ]
]

= Introducción
// TODO: contexto de métodos numéricos en valoración, motivación, aporte del artículo base.

= El artículo base
// TODO: modelo, problema de valoración, hipótesis, resultado principal (Lin & He 2021).

= Marco teórico y método
// TODO: dinámica del subyacente, función característica, fórmula de Gil-Pelaez.

= Datos
// TODO: fuente (yfinance ^SPX), fecha, strikes/vencimientos, tasa, dividendos, limpieza.

= Implementación, verificación y calibración
// TODO: detalles de cómputo, verificación (degeneración a Heston, semi-MC), calibración.

= Discusión
// TODO: análisis numérico (convergencia, estabilidad, costo), comparación con el original.

= Conclusiones
// TODO: hallazgos y extensiones posibles.

// Declaración de uso de IA: este trabajo se apoyó en herramientas de IA para depuración y
// redacción; la responsabilidad intelectual y la comprensión de los resultados son del grupo.

#bibliography("refs.bib", title: "Referencias", style: "apa")
