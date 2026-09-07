"""
Unit Tests for 21 CFR Part 11 Cryptographic Audit Trail
"""
from datetime import datetime, timezone
from backend.models.audit import compute_sha256_hash

def test_audit_hash_computation():
    """Verify deterministic hash computation"""
    ts = datetime.now(timezone.utc).isoformat()
    prev_hash = "GENESIS_HASH_0000000000000000000000000000000000000000000000000000000"
    payload = {"verdict": "PASS", "confidence": 0.98}
    
    hash1 = compute_sha256_hash(prev_hash, "INSPECTION_CREATED", "OP-042", "INSP-101", payload, ts)
    hash2 = compute_sha256_hash(prev_hash, "INSPECTION_CREATED", "OP-042", "INSP-101", payload, ts)
    
    assert len(hash1) == 64
    assert hash1 == hash2

def test_audit_tamper_detection():
    """Verify that any modification to payload alters the block hash and breaks the chain"""
    ts = datetime.now(timezone.utc).isoformat()
    prev_hash = "GENESIS_HASH"
    legit_payload = {"verdict": "PASS", "score": 95}
    tampered_payload = {"verdict": "REJECT", "score": 95}
    
    legit_hash = compute_sha256_hash(prev_hash, "ACTION", "OP-1", "ID-1", legit_payload, ts)
    tampered_hash = compute_sha256_hash(prev_hash, "ACTION", "OP-1", "ID-1", tampered_payload, ts)
    
    assert legit_hash != tampered_hash
