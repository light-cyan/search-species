# pyright: strict
import glob
import subprocess
import os
from .__init__ import TEST_ROOT, TEST_CACHE


def test_search_help():
    result = subprocess.run(["search", "--help"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "Search chemical species" in result.stdout


def verify_search_positive(engine: str, query: str, nCands: int):
    initial_files = set(glob.glob(os.path.join(TEST_CACHE, "*.json")))

    result = subprocess.run(
        ["search", engine, query, str(nCands), "-o", TEST_CACHE],
        capture_output=True,
        text=True,
        check=True,
        cwd=TEST_ROOT
    )

    assert "written ->" in result.stdout
    final_files = set(glob.glob(os.path.join(TEST_CACHE, "*.json")))
    new_files = final_files - initial_files
    assert len(new_files) > 0


def verify_search_negative(engine: str, query: str, nCands: int):
    initial_files = set(glob.glob(os.path.join(TEST_CACHE, "*.json")))

    result = subprocess.run(
        ["search", engine, query, str(nCands), "-o", TEST_CACHE],
        capture_output=True,
        text=True,
        check=True,
        cwd=TEST_ROOT
    )

    assert "RequestError(" in result.stderr
    final_files = set(glob.glob(os.path.join(TEST_CACHE, "*.json")))
    new_files = final_files - initial_files
    assert len(new_files) == 0
