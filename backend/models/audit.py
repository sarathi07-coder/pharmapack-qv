"""
21 CFR Part 11 Tamper-Proof Audit Trail Model
Cryptographically links each audit record with the previous record's SHA-256 hash.
"""
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, DateTime, Integer
from backend.models.base import Base

def compute_sha256_hash(prev_hash: str, action: str, user_badge: str, entity_id: str, data: dict, timestamp_iso: str) -> str:
    raw_payload = f"{prev_hash}|{action}|{user_badge}|{entity_id}|{json.dumps(data, sort_keys=True)}|{timestamp_iso}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    action = Column(String(64), nullable=False)          # INSPECTION_CREATED, VERDICT_OVERRIDDEN, CAPA_FILED
    user_badge = Column(String(50), nullable=False)       # Operator or Supervisor Badge ID
    user_role = Column(String(50), nullable=False)        # OPERATOR, SUPERVISOR, QA_AUDITOR
    entity_type = Column(String(64), nullable=False)      # Inspection, DispatchOrder, SOPRule
    entity_id = Column(String(64), nullable=False)        # ID of affected entity
    
    # Cryptographic SHA-256 Hash Chain
    previous_block_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), nullable=False, unique=True)
    
    # Audit Payload (immutable snapshot of before/after or inspection verdict)
    details = Column(JSON, default=dict)
    digital_signature = Column(String(255), nullable=True) # e-Signature token
