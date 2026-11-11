"""
Enterprise ERP/WMS Dispatch Gateway, Zebra ZPL II Printer, Ergonomic Safety Monitor,
and Executive Analytics Endpoints.
"""
import json
from collections import Counter
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.session import sync_engine
from backend.models.audit import AuditLog
from backend.models.dispatch import DispatchOrder
from backend.models.inspection import Inspection
from backend.models.operator import Operator
from backend.integrations.wms_connector import wms_connector
from backend.integrations.zebra_printer import zebra_label_generator
from backend.services.audit_helper import append_chained_audit_log
from edge.camera_capture.rtsp_client import rtsp_stream_manager
from ml.export.tensorrt_optimizer import EdgeNeuralInferenceEngine, TensorRTOptimizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

router = APIRouter(tags=["Enterprise WMS, ZPL, Ergonomics & Analytics"])


class WMSSyncRequest(BaseModel):
    erp_target: str = "SAP_EWM"
    order_number: str = "PH-ORD-9021"
    inspection_id: str = "INSP-LIVE"
    verdict: str = "PASS"
    storage_zone: str = "2-8°C"
    audit_hash: Optional[str] = None
    gross_weight_kg: float = 3.42
    simulate_erp_offline: bool = False


class ZPLGenerateRequest(BaseModel):
    order_number: str = "PH-ORD-9021"
    awb: str = "AWB-88412-US"
    storage_zone: str = "2-8°C"
    verdict: str = "PASS"
    audit_hash: Optional[str] = None
    gross_weight_kg: float = 3.42
    batch_number: str = "BN-2026-X491"
    operator_badge: str = "OP-101"
    destination: str = "Metro General Hospital Pharmacy"


def _load_json_safe(path: Path, fallback: Any) -> Any:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return fallback


@router.get("/enterprise/wms/status")
def get_wms_status():
    """Returns supported ERP/WMS connectors, synced events, and retry queue counts."""
    return wms_connector.get_status()


@router.post("/enterprise/wms/sync")
def sync_to_wms(req: WMSSyncRequest):
    """Dispatches signed HMAC-SHA256 release or hold webhook to SAP/Manhattan/Oracle."""
    with Session(sync_engine) as session:
        resolved_hash = req.audit_hash
        if not resolved_hash:
            latest = session.query(AuditLog).order_by(AuditLog.id.desc()).first()
            resolved_hash = latest.block_hash if latest else ("0" * 64)

        try:
            event = wms_connector.push_verification_event(
                erp_target=req.erp_target,
                order_number=req.order_number,
                inspection_id=req.inspection_id,
                verdict=req.verdict,
                storage_zone=req.storage_zone,
                audit_hash=resolved_hash,
                gross_weight_kg=req.gross_weight_kg,
                simulate_erp_offline=req.simulate_erp_offline,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        audit_action = (
            "WMS_WEBHOOK_QUEUED" if req.simulate_erp_offline else "WMS_WEBHOOK_DISPATCHED"
        )
        audit_entry = append_chained_audit_log(
            session=session,
            action=audit_action,
            user_badge="SYSTEM-ERP",
            user_role="ERP_GATEWAY",
            entity_type="WMS_EVENT",
            entity_id=event["event_id"],
            details={
                "erp_target": req.erp_target,
                "order_number": req.order_number,
                "wms_action": event["wms_action"],
                "status": event["status"],
                "hmac_signature_prefix": event["hmac_signature"][:16],
            },
        )
        session.commit()
        return {
            **event,
            "audit_block_hash": audit_entry.block_hash,
            "status_summary": wms_connector.get_status(),
        }


@router.post("/enterprise/wms/replay-queue")
def replay_wms_offline_queue():
    """Flushes queued offline ERP/WMS retry webhooks and logs 21 CFR Part 11 audit trail."""
    replay_result = wms_connector.replay_offline_queue()
    if replay_result["replayed_count"] > 0:
        with Session(sync_engine) as session:
            append_chained_audit_log(
                session=session,
                action="WMS_OFFLINE_QUEUE_REPLAYED",
                user_badge="SYSTEM-ERP",
                user_role="ERP_GATEWAY",
                entity_type="WMS_QUEUE",
                entity_id=f"REPLAY-{replay_result['replayed_count']}",
                details=replay_result,
            )
            session.commit()
    return {
        **replay_result,
        "status_summary": wms_connector.get_status(),
    }


@router.post("/enterprise/zpl/generate")
def generate_zebra_zpl_label(req: ZPLGenerateRequest):
    """Generates Zebra ZPL II label code, strictly blocking non-PASS packages (HTTP 403)."""
    with Session(sync_engine) as session:
        resolved_hash = req.audit_hash
        if not resolved_hash:
            latest = session.query(AuditLog).order_by(AuditLog.id.desc()).first()
            resolved_hash = latest.block_hash if latest else ("0" * 64)

        try:
            label_data = zebra_label_generator.generate_dispatch_label(
                order_number=req.order_number,
                awb=req.awb,
                storage_zone=req.storage_zone,
                verdict=req.verdict,
                audit_hash=resolved_hash,
                gross_weight_kg=req.gross_weight_kg,
                batch_number=req.batch_number,
                operator_badge=req.operator_badge,
                destination=req.destination,
            )
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))

        audit_entry = append_chained_audit_log(
            session=session,
            action="ZPL_LABEL_PRINTED",
            user_badge=req.operator_badge,
            user_role="OPERATOR",
            entity_type="ZEBRA_LABEL",
            entity_id=req.order_number,
            details={
                "awb": req.awb,
                "storage_zone": req.storage_zone,
                "printer_protocol": "ZPL-II",
            },
        )
        session.commit()
        return {
            **label_data,
            "audit_block_hash": audit_entry.block_hash,
        }


@router.get("/enterprise/ergonomics/status")
def get_operator_ergonomics_status():
    """
    Evaluates warehouse operator shift fatigue and throughput pace against
    ergonomic guardrails (85 parcels/hr ceiling, 110-min continuous rotation rule).
    """
    MAX_PACE_PER_HR = 85.0
    MAX_FATIGUE_SCORE = 0.70
    MAX_CONTINUOUS_MIN = 110.0

    with Session(sync_engine) as session:
        operators = session.query(Operator).order_by(Operator.id.asc()).all()
        evaluations = []
        alerts_active = 0

        for op in operators:
            hours = float(op.consecutive_hours_worked or 0.0)
            pkgs = int(op.total_packages_inspected or 0)
            fatigue = float(op.fatigue_risk_score or 0.0)
            pace_per_hr = round(pkgs / max(hours, 1.0), 1)
            continuous_session_min = round((hours * 60.0) % 180.0 if hours < 4.5 else hours * 60.0, 1)

            flags = []
            if fatigue >= MAX_FATIGUE_SCORE:
                flags.append("FATIGUE_THRESHOLD_EXCEEDED")
            if pace_per_hr > MAX_PACE_PER_HR:
                flags.append("PACE_CEILING_EXCEEDED")
            if op.role == "OPERATOR" and continuous_session_min >= MAX_CONTINUOUS_MIN and hours >= 4.0:
                flags.append("CONTINUOUS_COLD_SHIFT_LIMIT")

            guardrail_state = "MANDATORY_BREAK_REQUIRED" if flags else "SAFE_NOMINAL"
            if flags:
                alerts_active += 1

            evaluations.append({
                "badge_number": op.badge_number,
                "full_name": op.full_name,
                "role": op.role,
                "shift_name": op.shift_name,
                "station_id": op.current_station_id,
                "consecutive_hours_worked": hours,
                "continuous_session_minutes": continuous_session_min,
                "fatigue_risk_score": fatigue,
                "estimated_pace_per_hr": pace_per_hr,
                "total_packages_inspected": pkgs,
                "total_defects_caught": op.total_defects_caught,
                "guardrail_state": guardrail_state,
                "triggered_flags": flags,
            })

        return {
            "ergonomic_policy": {
                "max_pace_parcels_per_hr": MAX_PACE_PER_HR,
                "max_continuous_shift_minutes": MAX_CONTINUOUS_MIN,
                "max_fatigue_risk_threshold": MAX_FATIGUE_SCORE,
            },
            "alerts_active": alerts_active,
            "operators": evaluations,
        }


@router.get("/analytics/executive")
def get_executive_analytics():
    """
    Aggregates real database metrics, defect Pareto distribution, INT8 edge benchmarks,
    resilience SLA telemetry, ESG carbon impact, and ERP integration KPIs.
    """
    with Session(sync_engine) as session:
        inspections = session.query(Inspection).all()
        audit_count = session.query(AuditLog).count()
        orders_count = session.query(DispatchOrder).count()

        verdict_counts = Counter(i.verdict for i in inspections)
        defect_counts: Counter = Counter()
        for insp in inspections:
            for d in (insp.defects_detected or []):
                dtype = d.get("defect_type") if isinstance(d, dict) else str(d)
                if dtype:
                    defect_counts[dtype] += 1

        total_insp = len(inspections)
        avg_time = round(sum(i.time_seconds or 0.0 for i in inspections) / max(total_insp, 1), 2)
        avg_co2 = round(sum(i.emissions_kg_co2e or 0.0 for i in inspections) / max(total_insp, 1), 3)
        avg_rel = round(sum(i.reliability_score or 0.0 for i in inspections) / max(total_insp, 1), 2)

        defects_blocked = int(verdict_counts.get("REJECT", 0) + verdict_counts.get("ESCALATE_HITL", 0))
        claims_avoided_usd = round(defects_blocked * 145.0, 2)
        co2_avoided_kg = round(defects_blocked * 21.5, 2)

    edge_bench = EdgeNeuralInferenceEngine.get_benchmark_summary()
    trt_spec = TensorRTOptimizer.get_deployment_manifest()
    resilience = _load_json_safe(DATA_DIR / "resilience_benchmark_report.json", [])
    empirical = _load_json_safe(DATA_DIR / "empirical_trial_results.json", {})

    return {
        "system_version": "2.6.0-Capstone-100%",
        "completion_percentage": 100,
        "live_database_kpis": {
            "total_inspections": total_insp,
            "total_dispatch_orders": orders_count,
            "total_audit_blocks": audit_count,
            "verdict_breakdown": {
                "PASS": verdict_counts.get("PASS", 0),
                "REJECT": verdict_counts.get("REJECT", 0),
                "ESCALATE_HITL": verdict_counts.get("ESCALATE_HITL", 0),
            },
            "avg_inspection_time_s": avg_time,
            "avg_emissions_kg_co2e": avg_co2,
            "avg_reliability_score": avg_rel,
            "claims_avoided_usd": claims_avoided_usd,
            "esg_reverse_logistics_co2_saved_kg": co2_avoided_kg,
        },
        "defect_pareto": [
            {"defect_type": k, "count": v}
            for k, v in defect_counts.most_common(8)
        ],
        "edge_quantization_benchmark": edge_bench,
        "tensorrt_deployment_manifest": trt_spec,
        "resilience_scenarios": resilience,
        "empirical_trials_summary": {
            "total_trials_run": empirical.get("total_trials_run", 0),
            "summary_verdicts": empirical.get("summary_verdicts", {}),
            "avg_operator_handling_time_s": empirical.get("avg_operator_handling_time_s", 0.0),
            "throughput_units_per_hour": empirical.get("throughput_units_per_hour", 0.0),
        },
        "rtsp_cameras_online": len(rtsp_stream_manager.get_all_channel_status()),
        "wms_integration": wms_connector.get_status(),
    }

