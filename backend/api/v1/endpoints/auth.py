"""
Authentication & Operator Session Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.db.session import sync_engine
from backend.models.operator import Operator
from backend.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    badge_number: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    badge_number: str
    full_name: str
    role: str
    fatigue_risk_score: float

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    with Session(sync_engine) as session:
        op = session.query(Operator).filter(Operator.badge_number == req.badge_number).first()
        if not op or not verify_password(req.password, op.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid badge number or password"
            )
        
        token = create_access_token(data={
            "sub": op.id,
            "badge": op.badge_number,
            "role": op.role,
            "name": op.full_name
        })

        return TokenResponse(
            access_token=token,
            badge_number=op.badge_number,
            full_name=op.full_name,
            role=op.role,
            fatigue_risk_score=op.fatigue_risk_score
        )
