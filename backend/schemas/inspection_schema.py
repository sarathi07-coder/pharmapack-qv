"""
Pydantic v2 Schemas for Inspection Sessions, Defects, and Trade-Off Metrics
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x: float = Field(..., description="Top-left x coordinate normalized [0, 1]")
    y: float = Field(..., description="Top-left y coordinate normalized [0, 1]")
    width: float = Field(..., description="Box width normalized [0, 1]")
    height: float = Field(..., description="Box height normalized [0, 1]")

class DefectItem(BaseModel):
    defect_type: str = Field(..., description="Class name e.g. CRUSHED_CORNER, TAPE_BREACH, MISSING_ICE_PACK")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    severity: str = Field(default="MEDIUM", description="CRITICAL, HIGH, MEDIUM, LOW")
    bbox: Optional[BoundingBox] = None
    description: str = Field(..., description="Human-readable defect description")

class RuleViolation(BaseModel):
    rule_code: str = Field(..., description="e.g. SOP-COLD-01, SOP-DUM-04")
    rule_name: str = Field(..., description="Name of rule breached")
    severity: str = Field(default="CRITICAL")
    message: str = Field(..., description="Detailed explanation of failure")
    required_corrective_action: str = Field(..., description="Immediate packer fix")

class TradeOffMatrix(BaseModel):
    cost_index_usd: float = Field(..., description="Packaging material & rework cost ($)")
    time_latency_sec: float = Field(..., description="Total packing & inspection duration (s)")
    emissions_kg_co2e: float = Field(..., description="Estimated carbon emissions (kg CO2e)")
    reliability_score_pct: float = Field(..., ge=0.0, le=100.0, description="Defect escape prevention (%)")

class InspectionSubmitRequest(BaseModel):
    order_number: str = Field(..., description="Tracking order number or AWB")
    station_id: str = Field(..., description="Packing station identifier e.g. PACK-01")
    operator_id: Optional[str] = Field(None, description="Logged in operator ID")
    storage_zone: str = Field(default="15-25°C", description="Controlled storage zone: 2-8°C, 15-25°C, -20°C")
    target_temperature_c: Optional[float] = Field(None, description="Actual zone/probe temperature reading")
    gross_weight_kg: Optional[float] = Field(None, description="Measured package weight from IoT scale")
    image_base64: Optional[str] = Field(None, description="Base64 encoded packing photo (optional if file uploaded)")

class InspectionResponse(BaseModel):
    id: str
    order_number: str
    station_id: str
    verdict: str  # PASS, REJECT, ESCALATE_HITL
    overall_confidence: float
    ai_certainty_level: str
    defects: List[DefectItem] = []
    rule_violations: List[RuleViolation] = []
    ocr_data: Dict[str, Any] = {}
    tradeoff: TradeOffMatrix
    heatmap_url: Optional[str] = None
    image_url: Optional[str] = None
    audit_hash: str
    timestamp: str
    capa_recommendation: Optional[str] = None

class SupervisorDecisionRequest(BaseModel):
    decision: str = Field(..., description="OVERRIDE_PASS or CONFIRM_REJECT")
    reason_code: str = Field(..., description="e.g. FALSE_POSITIVE_SHADOW, OPERATOR_CORRECTED")
    supervisor_notes: str = Field(..., description="Mandatory sign-off notes")
    e_signature_pin: str = Field(..., description="21 CFR Part 11 electronic signature credential")
