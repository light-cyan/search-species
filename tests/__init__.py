# pyright: strict

from pathlib import Path

PROJECT_TITLE = "search-species"


def getProjectRoot() -> Path:
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if parent.name == PROJECT_TITLE:
            return parent
    raise RuntimeError(
        f"Fatal Error: Project root directory '{PROJECT_TITLE}' not found"
    )


PROJECT_ROOT = getProjectRoot()
TEST_ROOT = PROJECT_ROOT / "tests"
TEST_CACHE = TEST_ROOT / "cache"
TEST_GALLERY = TEST_ROOT / "gallery"

TEST_CACHE.mkdir(parents=True, exist_ok=True)
TEST_GALLERY.mkdir(parents=True, exist_ok=True)
