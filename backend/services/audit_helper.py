"""
Shared 21 CFR Part 11 Cryptographic Audit Chaining Helper
Ensures every inspection, supervisor override, ERP webhook, and ZPL print
appends a contiguous SHA-256 linked AuditLog record with zero chain breaks.
"""
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.models.audit import AuditLog, compute_sha256_hash


def append_chained_audit_log(
    session: Session,
    action: str,
    user_badge: str,
    user_role: str,
    entity_type: str,
    entity_id: str,
    details: Dict[str, Any],
) -> AuditLog:
    """Computes linked SHA-256 hash from head block and stages a new AuditLog row."""
    latest = session.query(AuditLog).order_by(AuditLog.id.desc()).first()
    prev_hash = latest.block_hash if latest else ("0" * 64)
    ts_utc = datetime.now(timezone.utc)
    block_hash = compute_sha256_hash(
        prev_hash,
        action,
        user_badge,
        entity_id,
        details,
        ts_utc.isoformat(),
    )

    entry = AuditLog(
        timestamp=ts_utc,
        action=action,
        user_badge=user_badge,
        user_role=user_role,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_block_hash=prev_hash,
        block_hash=block_hash,
        digital_signature=f"SIG-21CFR11-{block_hash[:16]}",
        details=details,
    )
    session.add(entry)
    session.flush()
    return entry

