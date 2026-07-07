"""Utilidades compartidas por los scripts: estilo de figuras y backend headless."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend no interactivo (headless)

import matplotlib.pyplot as plt  # noqa: E402


def setup_style():
    """Estilo consistente para todas las figuras del documento."""
    plt.rcParams.update(
        {
            "figure.figsize": (6.0, 4.0),
            "figure.dpi": 130,
            "font.size": 10,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "lines.linewidth": 1.6,
            "legend.frameon": False,
        }
    )
