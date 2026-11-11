"""
Multi-Camera Industrial RTSP / MJPEG Streaming & Dual-Stage Capture Endpoints
Streams Stage 1 Open-Box Overhead (`CAM-01-OVERHEAD`) and Stage 2 Sealed Conveyor
(`CAM-02-CONVEYOR`) feeds, supports live snapshot/sample pinning, and triggers
full LangGraph dual-camera verification with 21 CFR Part 11 audit chaining.
"""
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from edge.camera_capture.rtsp_client import rtsp_stream_manager
from backend.db.session import sync_engine
from backend.models.dispatch import DispatchOrder
from backend.models.inspection import Inspection
from backend.pipeline.graph_builder import pipeline_executor
from backend.services.audit_helper import append_chained_audit_log
from backend.api.v1.websockets.operator_ws import ws_manager

router = APIRouter(prefix="/streams", tags=["Multi-Camera RTSP Streaming"])


class SelectSampleRequest(BaseModel):
    sample_filename: Optional[str] = None


class DualCaptureInspectRequest(BaseModel):
    order_number: str = "PH-ORD-9021"
    station_id: str = "ST-04"
    operator_id: str = "OP-101"
    storage_zone: str = "2-8°C"
    gross_weight_kg: float = 3.42


@router.get("/cameras")
def list_camera_channels():
    """Returns status and telemetry for all industrial RTSP channels."""
    return {
        "cameras": rtsp_stream_manager.get_all_channel_status(),
        "sync_protocol": "Dual-Channel Stage-1/Stage-2 Genlock",
    }


@router.post("/{camera_id}/select-sample")
def select_camera_sample(camera_id: str, req: SelectSampleRequest):
    """Pins a deterministic conveyor preset or resumes auto-cycling when null."""
    ok = rtsp_stream_manager.set_channel_sample(camera_id, req.sample_filename)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Camera channel '{camera_id}' not found")
    return {
        "camera_id": camera_id,
        "pinned_sample": req.sample_filename,
        "cameras": rtsp_stream_manager.get_all_channel_status(),
    }


@router.get("/{camera_id}/snapshot")
def get_camera_snapshot(camera_id: str):
    """Captures single JPEG frame from the requested industrial RTSP channel."""
    try:
        jpeg_bytes, meta = rtsp_stream_manager.grab_frame_jpeg(camera_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={
            "X-Camera-Id": meta["camera_id"],
            "X-Camera-Stage": meta["stage"],
            "X-Frame-Seq": str(meta["frame_number"]),
            "X-Camera-Mode": meta["mode"],
            "Cache-Control": "no-store",
        },
    )


@router.get("/{camera_id}/mjpeg")
def stream_camera_mjpeg(
    camera_id: str,
    fps: int = Query(default=8, ge=1, le=30),
    max_frames: Optional[int] = Query(default=None, ge=1, le=500),
):
    """Streams live multipart/x-mixed-replace MJPEG video feed for browsers & VMS."""
    if camera_id not in rtsp_stream_manager.channels:
        raise HTTPException(status_code=404, detail=f"Camera channel '{camera_id}' not found")

    return StreamingResponse(
        rtsp_stream_manager.mjpeg_stream_generator(camera_id, fps=fps, max_frames=max_frames),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.post("/dual-capture-inspect")
async def trigger_dual_capture_inspection(req: Optional[DualCaptureInspectRequest] = None):
    """
    Synchronizes CAM-01-OVERHEAD + CAM-02-CONVEYOR frames, executes the
    LangGraph 6-Node Verification Pipeline, records chained 21 CFR Part 11 logs,
    and broadcasts live station telemetry over WebSocket.
    """
    payload = req or DualCaptureInspectRequest()
    dual = rtsp_stream_manager.grab_synchronized_dual_frames()
    stage1_meta = dual["stage_1_overhead"]["meta"]
    stage2_meta = dual["stage_2_conveyor"]["meta"]

    # Inspect faulty feed if Stage 1 shows a defect while Stage 2 is clean nominal
    use_stage1 = (
        stage2_meta.get("source") == "sample_clean.jpg"
        and stage1_meta.get("source") not in ("sample_clean.jpg", "sample_inside_pack.jpg")
    )
    primary_feed = dual["stage_1_overhead"] if use_stage1 else dual["stage_2_conveyor"]

    with Session(sync_engine) as session:
        order = session.query(DispatchOrder).filter(
            DispatchOrder.order_number == payload.order_number
        ).first()
        zone = order.storage_zone if order else payload.storage_zone
        if order and order.min_temp_c is not None and order.max_temp_c is not None:
            target_temp = round((float(order.min_temp_c) + float(order.max_temp_c)) / 2.0, 2)
        elif "-20" in zone:
            target_temp = -20.0
        elif "2-8" in zone:
            target_temp = 4.2
        else:
            target_temp = 21.0

        insp_id = f"RTSP-{uuid.uuid4().hex[:8].upper()}"
        final_state = pipeline_executor.run({
            "inspection_id": insp_id,
            "order_number": payload.order_number,
            "station_id": payload.station_id,
            "operator_id": payload.operator_id,
            "storage_zone": zone,
            "target_temperature_c": target_temp,
            "gross_weight_kg": payload.gross_weight_kg,
            "raw_image_base64": primary_feed["base64"],
        })

        verdict = final_state.get("verdict", "ESCALATE_HITL")
        defects = final_state.get("detected_defects", [])
        violations = final_state.get("rule_violations", [])
        tradeoff = final_state.get("tradeoff_matrix", {})
        confidence = float(final_state.get("overall_confidence", 0.0))

        audit_entry = append_chained_audit_log(
            session=session,
            action="RTSP_DUAL_CAM_INSPECTION",
            user_badge=payload.operator_id,
            user_role="OPERATOR",
            entity_type="Inspection",
            entity_id=insp_id,
            details={
                "order_number": payload.order_number,
                "verdict": verdict,
                "confidence": confidence,
                "cam_01_source": stage1_meta.get("source"),
                "cam_02_source": stage2_meta.get("source"),
                "defects_count": len(defects),
                "rule_violations_count": len(violations),
            },
        )

        record = Inspection(
            order_number=payload.order_number,
            station_id=payload.station_id,
            operator_id=payload.operator_id,
            image_url=f"/api/v1/streams/{primary_feed['meta']['camera_id']}/snapshot",
            verdict=verdict,
            overall_confidence=confidence,
            ai_certainty_level=final_state.get("ai_certainty_level", "HIGH"),
            defects_detected=defects,
            ocr_extracted_data=final_state.get("ocr_results", {}),
            rule_check_results=violations,
            cost_index=tradeoff.get("cost_usd", 0.0),
            time_seconds=tradeoff.get("time_seconds", 0.0),
            emissions_kg_co2e=tradeoff.get("emissions_kg_co2e", 0.0),
            reliability_score=tradeoff.get("reliability_score", 0.0),
            escalated_to_supervisor=(verdict == "ESCALATE_HITL"),
        )
        audit_hash = audit_entry.block_hash
        session.add(record)
        session.commit()

    await ws_manager.broadcast_to_station(
        payload.station_id,
        {
            "event": "RTSP_DUAL_INSPECTION_COMPLETED",
            "inspection_id": insp_id,
            "order_number": payload.order_number,
            "verdict": verdict,
            "confidence": confidence,
            "audit_hash": audit_hash,
        },
    )

    return {
        "inspection_id": insp_id,
        "order_number": payload.order_number,
        "station_id": payload.station_id,
        "storage_zone": zone,
        "verdict": verdict,
        "overall_confidence": confidence,
        "ai_certainty_level": final_state.get("ai_certainty_level", "HIGH"),
        "detected_defects": defects,
        "rule_violations": violations,
        "sop_citations": final_state.get("sop_citations", []),
        "tradeoff_matrix": tradeoff,
        "capa_action": final_state.get("capa_action", ""),
        "audit_hash": audit_hash,
        "vision_telemetry": {
            "source": final_state.get("vision_results", {}).get("source"),
            "latency_ms": final_state.get("vision_results", {}).get("latency_ms"),
            "neural_edge": final_state.get("vision_results", {}).get("neural_edge"),
        },
        "stage_1_camera": {
            **stage1_meta,
            "image_base64": dual["stage_1_overhead"]["base64"],
        },
        "stage_2_camera": {
            **stage2_meta,
            "image_base64": dual["stage_2_conveyor"]["base64"],
        },
    }
