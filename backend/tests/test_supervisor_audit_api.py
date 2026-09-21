"""
Supervisor HITL and 21 CFR Part 11 Audit API Test Suite
Validates Human-in-the-Loop decision sign-offs, electronic signature workflows,
and full cryptographic SHA-256 blockchain audit chain traversal.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_supervisor_queue_retrieval(client):
    """Verifies that supervisor escalation queue returns valid records."""
    res = client.get("/api/v1/supervisor/queue")
    assert res.status_code == 200
    queue = res.json()
    assert isinstance(queue, list)
    if len(queue) > 0:
        item = queue[0]
        assert "inspection_id" in item
        assert "order_number" in item
        assert "verdict" in item
        assert "confidence" in item

def test_supervisor_override_pass_decision(client):
    """Verifies supervisor override decision with 21 CFR Part 11 e-signature."""
    payload = {
        "inspection_id": "TEST-INSP-HITL-01",
        "decision": "OVERRIDE_PASS",
        "root_cause_code": "ACCEPTABLE_PRINT_SHADOW",
        "justification_notes": "Visual inspection verified packaging structural integrity intact. Shadow artifact only.",
        "supervisor_badge": "SUP-QA-401",
        "electronic_signature": "E-SIG-21CFR11-SECURE-PIN-401"
    }
    res = client.post("/api/v1/supervisor/decide", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DECISION_COMMITTED"
    assert data["final_verdict"] == "PASS"
    assert data["supervisor"] == "SUP-QA-401"
    assert len(data["audit_block_hash"]) == 64  # Valid SHA-256

def test_supervisor_confirm_reject_decision(client):
    """Verifies supervisor reject confirmation with mandatory corrective notes."""
    payload = {
        "inspection_id": "TEST-INSP-HITL-02",
        "decision": "CONFIRM_REJECT",
        "root_cause_code": "SEVERE_FLUTING_DAMAGE",
        "justification_notes": "Carton fluting crushed exceeding ISTA-3A 10mm limit. Sent for repack.",
        "supervisor_badge": "SUP-QA-402",
        "electronic_signature": "E-SIG-21CFR11-SECURE-PIN-402"
    }
    res = client.post("/api/v1/supervisor/decide", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DECISION_COMMITTED"
    assert data["final_verdict"] == "REJECT"
    assert len(data["audit_block_hash"]) == 64

def test_audit_logs_endpoint(client):
    """Verifies chronological audit log retrieval with SHA-256 block hashes."""
    res = client.get("/api/v1/audit/logs?limit=10")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
    assert len(logs) > 0
    for log in logs:
        assert "action" in log
        assert "user_badge" in log
        assert "block_hash" in log
        assert len(log["block_hash"]) == 64

def test_audit_verify_cryptographic_chain(client):
    """Verifies complete SHA-256 hash pointer chain traversal from Genesis to Head."""
    res = client.get("/api/v1/audit/verify-chain")
    assert res.status_code == 200
    data = res.json()
    assert data["chain_intact"] is True
    assert data["chain_status"] in ["VERIFIED_VALID", "EMPTY"]
    assert data["total_blocks_verified"] >= 1
    assert "FDA 21 CFR Part 11" in data["compliance_standards"]
