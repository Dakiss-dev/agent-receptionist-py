import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def fresh_store(tmp_path, monkeypatch):
    """Each test runs against a throwaway copy of the calendar store."""
    store = tmp_path / "calendar_store.json"
    shutil.copy(ROOT / "calendar_store.json", store)
    monkeypatch.setenv("CALENDAR_STORE", str(store))
    yield store
