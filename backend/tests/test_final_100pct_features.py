"""
Integration & Verification Tests for PharmaPack QV 75% -> 100% Capstone Features:
1. Sub-15ms INT8 Edge Neural Engine + HybridVisionClient Fusion
2. Dual-Camera Industrial RTSP Snapshots, MJPEG Streaming & Dual Capture Pipeline
3. Enterprise ERP/WMS HMAC-SHA256 Webhook Sync & Offline Retry Replay
4. Zebra ZPL II Label Generation Gating (200 PASS / 403 REJECT)
5. Operator Ergonomics Shift Guardrail & Executive Analytics Endpoints
6. 21 CFR Part 11 Audit CSV/JSON Export + SHA-256 Hash Chain Integrity
"""
import pytest
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app
from backend.integrations.wms_connector import wms_connector
from ml.export.tensorrt_optimizer import EdgeNeuralInferenceEngine
from ml.models.hybrid_vision_client import HybridVisionClient

client = TestClient(app)
SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "samples"


def test_int8_edge_neural_engine_sub_15ms():
    engine = EdgeNeuralInferenceEngine()
    assert engine.is_ready() is True
    assert engine.engine_mode == "INT8_QNNPACK"

    sample_path = SAMPLES_DIR / "sample_crushed.jpg"
    img = Image.open(sample_path).convert("RGB")
    pred = engine.predict(img)
    assert pred["available"] is True
    assert pred["latency_ms"] < 15.0
    assert pred["predicted_class"] in {
        "CLEAN",
        "CRUSHED_CORNER",
        "TAPE_BREACH",
        "LABEL_OBSCURED",
        "MISSING_ICE_PACK",
    }
    assert abs(sum(pred["probabilities"].values()) - 1.0) < 0.02

    vision = HybridVisionClient(api_key=None)
    vision.force_offline(True)
    res = vision.predict(img)
    assert res["source"] == "OFFLINE_EDGE_FALLBACK"
    assert res["neural_edge"]["available"] is True
    assert vision.get_telemetry()["sub_15ms_int8_ready"] is True


def test_rtsp_dual_camera_endpoints_and_mjpeg():
    cams_resp = client.get("/api/v1/streams/cameras")
    assert cams_resp.status_code == 200
    cam_ids = [c["camera_id"] for c in cams_resp.json()["cameras"]]
    assert "CAM-01-OVERHEAD" in cam_ids
    assert "CAM-02-CONVEYOR" in cam_ids

    snap = client.get("/api/v1/streams/CAM-01-OVERHEAD/snapshot")
    assert snap.status_code == 200
    assert snap.headers["content-type"] == "image/jpeg"
    assert len(snap.content) > 5000

    mjpeg = client.get("/api/v1/streams/CAM-02-CONVEYOR/mjpeg?fps=25&max_frames=2")
    assert mjpeg.status_code == 200
    assert "multipart/x-mixed-replace" in mjpeg.headers["content-type"]
    assert b"--frame" in mjpeg.content
    assert b"Content-Type: image/jpeg" in mjpeg.content

    pin = client.post(
        "/api/v1/streams/CAM-02-CONVEYOR/select-sample",
        json={"sample_filename": "sample_crushed.jpg"},
    )
    assert pin.status_code == 200

    try:
        dual = client.post(
            "/api/v1/streams/dual-capture-inspect",
            json={
                "order_number": "PH-ORD-9021",
                "station_id": "ST-04",
                "operator_id": "OP-101",
                "storage_zone": "2-8°C",
                "gross_weight_kg": 3.42,
            },
        )
        assert dual.status_code == 200
        body = dual.json()
        assert body["verdict"] in ("REJECT", "ESCALATE_HITL")
        assert len(body["audit_hash"]) == 64
        assert "stage_1_camera" in body and "stage_2_camera" in body
    finally:
        client.post(
            "/api/v1/streams/CAM-02-CONVEYOR/select-sample",
            json={"sample_filename": None},
        )


def test_wms_hmac_signing_offline_queue_and_replay():
    payload = {"event_id": "TEST-1", "verdict": "PASS"}
    sig = wms_connector.sign_payload(payload)
    assert wms_connector.verify_signature(payload, sig) is True
    assert wms_connector.verify_signature({"event_id": "TAMPERED"}, sig) is False

    queued = client.post(
        "/api/v1/enterprise/wms/sync",
        json={
            "erp_target": "SAP_EWM",
            "order_number": "PH-ORD-9021",
            "inspection_id": "INSP-WMS-TEST",
            "verdict": "PASS",
            "storage_zone": "2-8°C",
            "simulate_erp_offline": True,
        },
    )
    assert queued.status_code == 200
    assert queued.json()["status"] == "QUEUED_RETRY"

    status_before = client.get("/api/v1/enterprise/wms/status").json()
    assert status_before["queued_retries"] >= 1

    replayed = client.post("/api/v1/enterprise/wms/replay-queue")
    assert replayed.status_code == 200
    assert replayed.json()["replayed_count"] >= 1
    assert replayed.json()["status_summary"]["queued_retries"] == 0


def test_zebra_zpl_gdp_gate_pass_and_reject_block():
    ok_resp = client.post(
        "/api/v1/enterprise/zpl/generate",
        json={
            "order_number": "PH-ORD-9021",
            "awb": "AWB-88412-US",
            "storage_zone": "2-8°C",
            "verdict": "PASS",
        },
    )
    assert ok_resp.status_code == 200
    zpl_data = ok_resp.json()
    assert zpl_data["printer_protocol"] == "ZPL-II"
    assert zpl_data["zpl_command"].startswith("^XA")
    assert zpl_data["zpl_command"].endswith("^XZ")

    blocked_resp = client.post(
        "/api/v1/enterprise/zpl/generate",
        json={
            "order_number": "PH-ORD-9021",
            "awb": "AWB-88412-US",
            "storage_zone": "2-8°C",
            "verdict": "REJECT",
        },
    )
    assert blocked_resp.status_code == 403


def test_ergonomics_guardrails_and_executive_analytics():
    ergo = client.get("/api/v1/enterprise/ergonomics/status")
    assert ergo.status_code == 200
    ergo_data = ergo.json()
    assert ergo_data["alerts_active"] >= 1
    op_map = {op["badge_number"]: op for op in ergo_data["operators"]}
    assert op_map["OP-102"]["guardrail_state"] == "MANDATORY_BREAK_REQUIRED"

    exec_resp = client.get("/api/v1/analytics/executive")
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["completion_percentage"] == 100
    assert exec_data["edge_quantization_benchmark"]["sub_15ms_sla_met"] is True
    assert exec_data["live_database_kpis"]["total_inspections"] >= 1


def test_audit_export_csv_json_and_chain_integrity():
    csv_resp = client.get("/api/v1/audit/export?format=csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
    assert "id,timestamp,action,user_badge" in csv_resp.text

    json_resp = client.get("/api/v1/audit/export?format=json")
    assert json_resp.status_code == 200
    assert json_resp.json()["total_records"] >= 1

    verify = client.get("/api/v1/audit/verify-chain")
    assert verify.status_code == 200
    v_data = verify.json()
    assert v_data["chain_intact"] is True
    assert v_data["tampered_blocks_count"] == 0

