"""
Pydantic Schemas for Packaging SOPs & Checklists
"""
from typing import List
from pydantic import BaseModel, Field

class SopChecklistItem(BaseModel):
    item_id: str
    category: str  # INSULATION, DUNNAGE, SEALING, LABELING
    title: str
    description: str
    is_mandatory: bool = True
    pass_condition: str

class SopRuleDefinition(BaseModel):
    rule_code: str
    zone: str  # 2-8°C, 15-25°C, -20°C
    title: str
    min_ice_packs: int = 0
    requires_thermal_bubble: bool = False
    requires_tamper_tape: bool = True
    max_dunnage_void_ratio: float = 0.20  # Max 20% empty space allowed
    checklists: List[SopChecklistItem] = []
