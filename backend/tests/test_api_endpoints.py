"""
Full API Integration Test Suite
Tests FastAPI endpoints with HTTPX TestClient
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_root_endpoint(client):
    res = client.get("/api/info")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert "21 CFR Part 11" in data["standard"]

def test_frontend_ui_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "PHARMAPACK" in res.text
    assert "Operator Station" in res.text

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["rules_engine"] == "ACTIVE"

def test_auth_login(client):
    res = client.post("/api/v1/auth/login", json={
        "badge_number": "OP-101",
        "password": "packer123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "OPERATOR"
    assert data["badge_number"] == "OP-101"

def test_submit_clean_inspection(client):
    res = client.post("/api/v1/inspections/submit", json={
        "order_number": "PH-ORD-9021",
        "station_id": "STATION-01",
        "operator_id": "OP-101",
        "storage_zone": "2-8°C",
        "target_temperature_c": 4.5,
        "gross_weight_kg": 3.2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] == "PASS"
    assert len(data["audit_hash"]) == 64  # SHA-256 length
    assert "tradeoff" in data
    assert data["tradeoff"]["reliability_score_pct"] > 90.0

def test_inspection_history(client):
    res = client.get("/api/v1/inspections/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
