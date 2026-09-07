"""
Pytest Configuration & Fixtures for PharmaPack QV Test Suite
"""
import os
import pytest

@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch):
    """
    Ensures unit test suite runs deterministically with local edge heuristics
    without making slow external network calls to third-party APIs.
    """
    monkeypatch.setenv("ROBOFLOW_API_KEY", "")
    monkeypatch.setenv("ENVIRONMENT", "testing")
