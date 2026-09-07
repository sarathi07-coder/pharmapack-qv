"""
Inspection Quality Verification Endpoints
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import sync_engine
from backend.models.inspection import Inspection
from backend.models.audit import AuditLog, compute_sha256_hash
from backend.schemas.inspection_schema import (
    InspectionSubmitRequest,
    InspectionResponse,
    TradeOffMatrix,
    DefectItem,
    RuleViolation
)
from backend.pipeline.graph_builder import pipeline_executor
from backend.pipeline.state import InspectionGraphState

router = APIRouter(prefix="/inspections", tags=["Inspections"])

@router.post("/submit", response_model=InspectionResponse)
def submit_inspection(req: InspectionSubmitRequest):
    """
    Primary packing verification endpoint. Runs LangGraph stateful analysis:
    Vision -> Rules -> RAG -> Trade-off -> Verdict -> Tamper-Proof Audit
    """
    inspection_id = str(uuid.uuid4())
    
    # 1. Initialize Pipeline State
    init_state: InspectionGraphState = {
        "inspection_id": inspection_id,
        "order_number": req.order_number,
        "station_id": req.station_id,
        "operator_id": req.operator_id,
        "storage_zone": req.storage_zone,
        "target_temperature_c": req.target_temperature_c,
        "gross_weight_kg": req.gross_weight_kg,
        "raw_image_base64": req.image_base64,
        "vision_results": {},
        "ocr_results": {},
        "detected_defects": [],
        "rule_violations": [],
        "sop_citations": [],
        "overall_confidence": 0.0,
        "ai_certainty_level": "",
        "verdict": "",
        "tradeoff_matrix": {},
        "capa_action": None,
        "audit_hash": None,
        "error_message": None
    }

    # 2. Execute Stateful Decision Pipeline
    final_state = pipeline_executor.run(init_state)

    # 3. Commit 21 CFR Part 11 Tamper-Proof Audit Record
    timestamp_iso = datetime.now(timezone.utc).isoformat()
    
    with Session(sync_engine) as session:
        # Get latest block hash for cryptographic chaining
        last_audit = session.query(AuditLog).order_by(AuditLog.id.desc()).first()
        prev_hash = last_audit.block_hash if last_audit else ("0" * 64)

        audit_payload = {
            "order_number": req.order_number,
            "station_id": req.station_id,
            "verdict": final_state["verdict"],
            "confidence": final_state["overall_confidence"],
            "defects_count": len(final_state["detected_defects"]),
            "violations_count": len(final_state["rule_violations"]),
            "tradeoff": final_state["tradeoff_matrix"]
        }

        block_hash = compute_sha256_hash(
            prev_hash=prev_hash,
            action="INSPECTION_COMPLETED",
            user_badge=req.operator_id or "ANONYMOUS_PACKER",
            entity_id=inspection_id,
            data=audit_payload,
            timestamp_iso=timestamp_iso
        )

        audit_record = AuditLog(
            action="INSPECTION_COMPLETED",
            user_badge=req.operator_id or "ANONYMOUS_PACKER",
            user_role="OPERATOR",
            entity_type="Inspection",
            entity_id=inspection_id,
            previous_block_hash=prev_hash,
            block_hash=block_hash,
            details=audit_payload,
            digital_signature=f"SIG_{block_hash[:16]}"
        )
        session.add(audit_record)

        # 4. Save Inspection Record
        inspection = Inspection(
            id=inspection_id,
            order_number=req.order_number,
            station_id=req.station_id,
            operator_id=req.operator_id,
            verdict=final_state["verdict"],
            overall_confidence=final_state["overall_confidence"],
            ai_certainty_level=final_state["ai_certainty_level"],
            defects_detected=final_state["detected_defects"],
            ocr_extracted_data=final_state["ocr_results"],
            rule_check_results=final_state["rule_violations"],
            cost_index=final_state["tradeoff_matrix"].get("cost_index_usd", 0.0),
            time_seconds=final_state["tradeoff_matrix"].get("time_latency_sec", 0.0),
            emissions_kg_co2e=final_state["tradeoff_matrix"].get("emissions_kg_co2e", 0.0),
            reliability_score=final_state["tradeoff_matrix"].get("reliability_score_pct", 0.0)
        )
        session.add(inspection)
        session.commit()

    # 5. Build Response
    defects_model = [DefectItem(**d) for d in final_state["detected_defects"]]
    violations_model = [RuleViolation(**v) for v in final_state["rule_violations"]]
    tradeoff_model = TradeOffMatrix(
        cost_index_usd=final_state["tradeoff_matrix"]["cost_index_usd"],
        time_latency_sec=final_state["tradeoff_matrix"]["time_latency_sec"],
        emissions_kg_co2e=final_state["tradeoff_matrix"]["emissions_kg_co2e"],
        reliability_score_pct=final_state["tradeoff_matrix"]["reliability_score_pct"]
    )

    return InspectionResponse(
        id=inspection_id,
        order_number=req.order_number,
        station_id=req.station_id,
        verdict=final_state["verdict"],
        overall_confidence=final_state["overall_confidence"],
        ai_certainty_level=final_state["ai_certainty_level"],
        defects=defects_model,
        rule_violations=violations_model,
        ocr_data=final_state["ocr_results"],
        tradeoff=tradeoff_model,
        heatmap_url=final_state["vision_results"].get("heatmap_base64"),
        audit_hash=block_hash,
        timestamp=timestamp_iso,
        capa_recommendation=final_state["capa_action"]
    )

@router.get("/history")
def get_inspection_history(limit: int = 20):
    with Session(sync_engine) as session:
        records = session.query(Inspection).order_by(Inspection.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "order_number": r.order_number,
                "station_id": r.station_id,
                "verdict": r.verdict,
                "confidence": r.overall_confidence,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "reliability_score": r.reliability_score
            }
            for r in records
        ]
