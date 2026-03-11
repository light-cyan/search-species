# pyright: strict

from pathlib import Path


PACKAGE_NAME = "search_species"


def getPackageRoot() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if parent.name == PACKAGE_NAME:
            return parent
    raise RuntimeError(
        f"Fatal Error: Package root directory '{PACKAGE_NAME}' not found"
    )


PACKAGE_ROOT = getPackageRoot()
