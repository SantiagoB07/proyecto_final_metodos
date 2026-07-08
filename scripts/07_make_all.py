"""Reproduce de principio a fin todas las figuras y tablas del análisis.

Ejecuta en orden los scripts de verificación, análisis numérico, datos y calibración.
El script de datos (05) reutiliza el snapshot crudo versionado en data/raw/ (no vuelve a
llamar a la API salvo que se pase --refresh-data).

Uso:
    uv run python scripts/07_make_all.py
    uv run python scripts/07_make_all.py --refresh-data   # redescarga el snapshot de mercado
"""

from __future__ import annotations

import importlib.util
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ORDER = [
    "01_verify_heston_limit",
    "02_verify_semimc",
    "03_figs_articulo",
    "04_numerical_analysis",
    "05_get_data",
    "06_calibrate",
    "08_get_panel",      # panel histórico de 6 meses (reutiliza el crudo versionado)
    "09_calibrate_panel",  # calibración por fecha (paralela) y resultados promediados
]


def _run(name, **kwargs):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    t0 = time.perf_counter()
    mod.main(**kwargs)
    print(f"  [{name}] listo en {time.perf_counter() - t0:.1f}s\n")


def main():
    refresh = "--refresh-data" in sys.argv
    print("== Reproducción completa de figuras y tablas ==\n")
    for name in ORDER:
        print(f">>> {name}")
        if name in ("05_get_data", "08_get_panel"):
            _run(name, force=refresh)
        else:
            _run(name)
    print("== Completado. Resultados en results/figures y results/tables. ==")


if __name__ == "__main__":
    main()
