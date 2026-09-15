"""Test-wide setup: point the app at an isolated throwaway SQLite DB so tests
never touch a real Postgres instance and are safe to run with no services up."""
import os
import sys
import pathlib

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_pytest.db")
os.environ.setdefault("LLM_PROVIDER", "ollama")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
