"""
LangGraph Workflow Nodes
Functional state transition nodes executing multi-modal inspection, rules, RAG, and trade-off calculation.
"""
import io
import base64
from typing import Dict, Any
from PIL import Image
from backend.pipeline.state import InspectionGraphState
from ml.models.vision_service import vision_service
from backend.rules.pharma_rules_engine import rules_engine
from backend.ai.rag.sop_retriever import sop_retriever
from backend.services.tradeoff_calculator import tradeoff_calculator
from backend.core.config import settings

def vision_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Decodes image and runs vision + OCR pipeline"""
    raw_b64 = state.get("raw_image_base64")
    if raw_b64:
        image_bytes = base64.b64decode(raw_b64)
        img = Image.open(io.BytesIO(image_bytes))
    else:
        # Load sample fallback image
        sample_path = settings.SAMPLES_DIR / "sample_clean.jpg"
        img = Image.open(sample_path)

    vision_out = vision_service.process_image(img, order_hint=state.get("order_number", ""))
    
    return {
        "vision_results": vision_out,
        "ocr_results": vision_out.get("ocr_data", {}),
        "detected_defects": vision_out.get("defects", []),
        "overall_confidence": vision_out.get("overall_vision_confidence", 0.95)
    }

def rules_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Runs deterministic rule checks against vision outputs and storage zone constraints"""
    storage_zone = state.get("storage_zone", "15-25°C")
    defects = state.get("detected_defects", [])
    ocr_data = state.get("ocr_results", {})
    temp = state.get("target_temperature_c")
    weight = state.get("gross_weight_kg")
    
    void_metrics = state.get("vision_results", {}).get("void_metrics", {})
    void_ratio = void_metrics.get("void_ratio", 0.15)

    violations = rules_engine.evaluate_rules(
        storage_zone=storage_zone,
        defects=defects,
        ocr_data=ocr_data,
        measured_temp_c=temp,
        gross_weight_kg=weight,
        void_ratio=void_ratio
    )
    return {"rule_violations": violations}

def rag_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Retrieves relevant GDP & WHO standard clauses"""
    defects = [d["defect_type"] for d in state.get("detected_defects", [])]
    zone = state.get("storage_zone", "15-25°C")
    sop_citations = sop_retriever.retrieve_relevant_sop(defects, zone)
    return {"sop_citations": sop_citations}

def tradeoff_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Computes Cost, Time, Emissions (CO2), and Reliability metrics"""
    defects = state.get("detected_defects", [])
    violations = state.get("rule_violations", [])
    zone = state.get("storage_zone", "15-25°C")
    
    matrix = tradeoff_calculator.calculate_tradeoff(
        defects_detected=defects,
        rule_violations=violations,
        storage_zone=zone,
        is_hitl_escalated=False
    )
    return {"tradeoff_matrix": matrix}

def verdict_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Determines PASS, REJECT, or ESCALATE_HITL based on severity and confidence thresholds"""
    defects = state.get("detected_defects", [])
    violations = state.get("rule_violations", [])
    conf = state.get("overall_confidence", 0.95)

    has_critical = any(v.get("severity") == "CRITICAL" for v in violations) or \
                   any(d.get("severity") == "CRITICAL" for d in defects)

    if has_critical:
        verdict = "REJECT"
        certainty = "HIGH"
    elif violations or defects:
        # If defects detected but confidence is ambiguous (e.g. 0.60 to 0.85) -> Escalate to supervisor!
        if conf < settings.CONFIDENCE_AUTO_PASS_MIN and conf >= settings.CONFIDENCE_HITL_ESCALATION_MIN:
            verdict = "ESCALATE_HITL"
            certainty = "MEDIUM"
        else:
            verdict = "REJECT"
            certainty = "HIGH"
    else:
        verdict = "PASS"
        certainty = "HIGH"

    return {
        "verdict": verdict,
        "ai_certainty_level": certainty
    }

def capa_node(state: InspectionGraphState) -> Dict[str, Any]:
    """Generates automated corrective action recommendations for the packing operator"""
    verdict = state.get("verdict", "PASS")
    violations = state.get("rule_violations", [])
    
    if verdict == "PASS":
        capa = "All quality parameters verified compliant with WHO GDP standards. Clear to seal and attach shipping manifest."
    elif verdict == "ESCALATE_HITL":
        capa = "Marginal defect detected. Package routed to Floor Supervisor exception queue for visual sign-off."
    else:
        # Compile specific fixes from rule violations
        actions = [v.get("required_corrective_action") for v in violations if v.get("required_corrective_action")]
        capa = "CORRECTIVE ACTION REQUIRED: " + " | ".join(actions) if actions else "Re-inspect carton packaging and replace damaged materials."

    return {"capa_action": capa}
