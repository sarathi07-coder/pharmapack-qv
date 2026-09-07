"""
End-to-End Tests for LangGraph Inspection Pipeline
"""
from ml.dataset.synthetic_generator import PharmaPackageGenerator
from backend.pipeline.graph_builder import pipeline_executor
from backend.pipeline.state import InspectionGraphState

def test_pipeline_clean_package():
    generator = PharmaPackageGenerator()
    b64_img, _ = generator.generate_base64_image(defect_type="CLEAN", zone="15-25°C")

    initial_state: InspectionGraphState = {
        "inspection_id": "TEST-INSP-01",
        "order_number": "PH-ORD-9021",
        "station_id": "STATION-01",
        "operator_id": "OP-101",
        "storage_zone": "15-25°C",
        "target_temperature_c": 19.5,
        "gross_weight_kg": 3.8,
        "raw_image_base64": b64_img,
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

    final_state = pipeline_executor.run(initial_state)

    assert final_state["verdict"] == "PASS"
    assert len(final_state["detected_defects"]) == 0
    assert len(final_state["rule_violations"]) == 0
    assert "cost_index_usd" in final_state["tradeoff_matrix"]
    assert "reliability_score_pct" in final_state["tradeoff_matrix"]
    assert final_state["tradeoff_matrix"]["reliability_score_pct"] > 95.0

def test_pipeline_crushed_package():
    generator = PharmaPackageGenerator()
    b64_img, _ = generator.generate_base64_image(defect_type="CRUSHED_CORNER", zone="15-25°C")

    initial_state: InspectionGraphState = {
        "inspection_id": "TEST-INSP-02",
        "order_number": "PH-ORD-9022",
        "station_id": "STATION-01",
        "operator_id": "OP-101",
        "storage_zone": "15-25°C",
        "target_temperature_c": 20.0,
        "gross_weight_kg": 4.1,
        "raw_image_base64": b64_img,
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

    final_state = pipeline_executor.run(initial_state)

    assert final_state["verdict"] in ["REJECT", "ESCALATE_HITL"]
    assert len(final_state["detected_defects"]) > 0
    assert any(v["rule_code"] == "SOP-BOX-02" for v in final_state["rule_violations"])
    assert final_state["tradeoff_matrix"]["net_dollars_saved_usd"] > 100.0  # Proves pre-dispatch savings!
    assert ("CORRECTIVE ACTION" in final_state["capa_action"]) or ("Supervisor" in final_state["capa_action"])
