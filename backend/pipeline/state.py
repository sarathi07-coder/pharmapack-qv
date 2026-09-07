"""
State Definition for LangGraph Inspection Workflow
"""
from typing import TypedDict, List, Dict, Any, Optional

class InspectionGraphState(TypedDict):
    # Session metadata
    inspection_id: str
    order_number: str
    station_id: str
    operator_id: Optional[str]
    storage_zone: str
    target_temperature_c: Optional[float]
    gross_weight_kg: Optional[float]
    raw_image_base64: Optional[str]
    
    # Model & Feature outputs
    vision_results: Dict[str, Any]
    ocr_results: Dict[str, Any]
    detected_defects: List[Dict[str, Any]]
    rule_violations: List[Dict[str, Any]]
    sop_citations: List[Dict[str, Any]]
    
    # Decision metrics
    overall_confidence: float
    ai_certainty_level: str
    verdict: str  # PASS, REJECT, ESCALATE_HITL
    
    # 4-Way Multi-Objective Trade-Off
    tradeoff_matrix: Dict[str, float]
    
    # Corrective action recommendations
    capa_action: Optional[str]
    audit_hash: Optional[str]
    error_message: Optional[str]
