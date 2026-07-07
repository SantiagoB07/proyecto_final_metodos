"""Rutas del proyecto relativas a la raíz del repositorio (sin rutas absolutas).

Localiza la raíz del repositorio subiendo por el árbol de directorios hasta encontrar
``pyproject.toml``, y expone las carpetas de datos y resultados. Los scripts las usan para
leer/escribir sin depender del directorio de trabajo ni de rutas absolutas (requisito de la
rúbrica).
"""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Devuelve la raíz del repositorio (directorio que contiene pyproject.toml)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("No se encontró la raíz del repositorio (pyproject.toml).")


ROOT = repo_root()
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
RESULTS_FIGURES = ROOT / "results" / "figures"
RESULTS_TABLES = ROOT / "results" / "tables"


def ensure_dirs() -> None:
    """Crea las carpetas de datos y resultados si no existen."""
    for d in (DATA_RAW, DATA_PROCESSED, RESULTS_FIGURES, RESULTS_TABLES):
        d.mkdir(parents=True, exist_ok=True)
