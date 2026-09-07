"""
Dispatch Order Model — Outbound pharmaceutical orders subject to controlled storage and packaging specs.
"""
from sqlalchemy import Column, String, Float, Boolean, JSON
from backend.models.base import Base, TimestampMixin

class DispatchOrder(Base, TimestampMixin):
    __tablename__ = "dispatch_orders"

    order_number = Column(String(64), unique=True, index=True, nullable=False)
    tracking_awb = Column(String(128), unique=True, index=True, nullable=False)
    destination_facility = Column(String(128), nullable=False)
    
    # Storage zone requirements
    storage_zone = Column(String(32), default="15-25°C", nullable=False)  # 2-8°C, 15-25°C, -20°C
    min_temp_c = Column(Float, default=15.0)
    max_temp_c = Column(Float, default=25.0)
    is_cold_chain = Column(Boolean, default=False)
    
    # Packaging requirements
    required_box_type = Column(String(64), default="STANDARD_CORRUGATED")
    requires_ice_packs = Column(Boolean, default=False)
    ice_pack_count = Column(Float, default=0)
    requires_tamper_tape = Column(Boolean, default=True)
    max_gross_weight_kg = Column(Float, default=5.0)
    item_attributes = Column(JSON, default=dict)  # Product list, vials, blister packs
    status = Column(String(32), default="PENDING_INSPECTION")  # PENDING, PASSED, FLAGGED, REJECTED, DISPATCHED
