"""
Inspection Session Model — Records packing quality verification sessions, AI verdicts, and metrics.
"""
from sqlalchemy import Column, String, Float, JSON, ForeignKey
from backend.models.base import Base, TimestampMixin

class Inspection(Base, TimestampMixin):
    __tablename__ = "inspections"

    order_number = Column(String(64), index=True, nullable=False)
    station_id = Column(String(32), index=True, nullable=False)
    operator_id = Column(String(36), ForeignKey("operators.id"), nullable=True)
    
    # Image storage reference
    image_url = Column(String(255), nullable=True)
    heatmap_url = Column(String(255), nullable=True)
    
    # Verification Decision
    verdict = Column(String(32), nullable=False)  # PASS, REJECT, ESCALATE_HITL
    overall_confidence = Column(Float, nullable=False)
    ai_certainty_level = Column(String(32), default="HIGH")  # HIGH, MEDIUM, LOW
    
    # Multi-attribute detection outcomes
    defects_detected = Column(JSON, default=list)  # List of defect objects
    ocr_extracted_data = Column(JSON, default=dict)  # Barcode, expiry, batch
    rule_check_results = Column(JSON, default=list)  # Deterministic rule evaluations
    
    # 4-Way Multi-Objective Trade-Off Metrics
    cost_index = Column(Float, default=0.0)         # Material & rework cost ($)
    time_seconds = Column(Float, default=0.0)       # Packaging & inspection time (s)
    emissions_kg_co2e = Column(Float, default=0.0)  # Carbon footprint (kg CO2e)
    reliability_score = Column(Float, default=0.0)  # Defect escape prevention (0-100%)
    
    # HITL status
    escalated_to_supervisor = Column(String(36), nullable=True)
    supervisor_verdict = Column(String(32), nullable=True)  # OVERRIDE_PASS, CONFIRM_REJECT
    supervisor_notes = Column(String(512), nullable=True)
