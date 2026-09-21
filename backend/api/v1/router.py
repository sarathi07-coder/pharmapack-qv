"""
API v1 Router Aggregator
"""
from fastapi import APIRouter
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.inspections import router as inspections_router
from backend.api.v1.endpoints.supervisor import router as supervisor_router
from backend.api.v1.endpoints.audit import router as audit_router
from backend.api.v1.websockets.operator_ws import router as ws_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(inspections_router)
api_router.include_router(supervisor_router)
api_router.include_router(audit_router)
api_router.include_router(ws_router)
