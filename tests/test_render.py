# pyright: strict
import glob
import subprocess
import os
from .__init__ import TEST_ROOT, TEST_GALLERY


def test_render_help():
    result = subprocess.run(["render", "--help"],
                            capture_output=True, text=True)
    assert result.returncode == 0
    assert "Render species candidate cards" in result.stdout


def test_render():
    initial_files = set(glob.glob(os.path.join(TEST_GALLERY, "*.png")))

    result = subprocess.run(
        ["render", "-o", TEST_GALLERY],
        capture_output=True,
        text=True,
        check=True,
        cwd=TEST_ROOT
    )

    assert "rendered ->" in result.stdout
    final_files = set(glob.glob(os.path.join(TEST_GALLERY, "*.png")))
    new_files = final_files - initial_files
    assert len(new_files) > 0
