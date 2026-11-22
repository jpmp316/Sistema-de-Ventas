import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("url", [
    "postgresql+psycopg://user:fake@localhost/development",
    "sqlite+pysqlite:///development.db",
])
def test_suite_refuses_non_memory_database_before_importing_app(url):
    # Isolate conftest evaluation from the pytest process and its imported modules.
    env = {**os.environ, "TEST_DATABASE_URL": url}
    conftest = Path(__file__).with_name("conftest.py")
    result = subprocess.run(
        [sys.executable, str(conftest)], env=env,
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode != 0
    assert "RuntimeError" in result.stderr
    assert "SQLite en memoria" in result.stderr
