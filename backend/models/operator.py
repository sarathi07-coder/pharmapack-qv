"""
Operator Model — Tracks warehouse operators, roles, shifts, and fatigue metrics.
"""
from sqlalchemy import Column, String, Float, Integer, Boolean
from backend.models.base import Base, TimestampMixin

class Operator(Base, TimestampMixin):
    __tablename__ = "operators"

    badge_number = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), default="OPERATOR")  # OPERATOR, SUPERVISOR, QA_AUDITOR, ADMIN
    hashed_password = Column(String(255), nullable=False)
    shift_name = Column(String(50), default="Morning Shift")
    current_station_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Fatigue and safety monitoring limits (prevent unsafe assignment)
    consecutive_hours_worked = Column(Float, default=0.0)
    fatigue_risk_score = Column(Float, default=0.1)  # 0.0 (fresh) to 1.0 (exhausted)
    total_packages_inspected = Column(Integer, default=0)
    total_defects_caught = Column(Integer, default=0)
    compliance_rating = Column(Float, default=98.5)
