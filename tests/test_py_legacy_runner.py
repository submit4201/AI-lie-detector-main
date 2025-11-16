import sys
import subprocess
from pathlib import Path
import pytest

# Discover legacy test scripts in the tests/ directory that start with 'test_'
# but are not pytest-style (we will execute them as standalone scripts).
ROOT = Path(__file__).parent.parent
TESTS_DIR = Path(__file__).parent
legacy_scripts = [p for p in TESTS_DIR.glob('test_*.py') if not p.name.startswith('test_py_')]

if not legacy_scripts:
    pytest.skip("No legacy test scripts found", allow_module_level=True)

ids = [p.name for p in legacy_scripts]

@pytest.mark.parametrize("script_path", legacy_scripts, ids=ids)
def test_legacy_script_runs(script_path):
    """Run a legacy test script as a subprocess and assert it exits with code 0."""
    # Run the script with the project root as cwd so imports using relative paths work.
    env = None
    try:
        import os
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
    except Exception:
        env = None

    proc = subprocess.run([sys.executable, str(script_path)], cwd=ROOT, capture_output=True, text=True, timeout=300, env=env)

    # Print captured output for debugging in pytest logs
    if proc.stdout:
        print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)

    assert proc.returncode == 0, f"Legacy script {script_path.name} exited with {proc.returncode}. See stdout/stderr above."
