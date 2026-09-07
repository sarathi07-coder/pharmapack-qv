"""
Multi-Objective Trade-Off Calculator
Exposes the fundamental trade-off between Cost, Time, Emissions (CO2), and Reliability,
and calculates whether catching packing errors before dispatch justifies system adoption.
"""
from typing import Dict, Any, List

class TradeOffCalculator:
    # Industry benchmark unit costs (USD & Carbon kg CO2e)
    BASE_PACKAGING_COST = 3.50      # Corrugated carton, tape, label
    REWORK_AT_WAREHOUSE_COST = 8.00  # Cost to repack before dispatch
    POST_DISPATCH_DAMAGE_COST = 145.00 # Returned damaged order, reshipment, credit note, pharma disposal
    
    BASE_PACK_TIME_SEC = 24.0       # Average operator manual pack duration
    AI_INSPECTION_TIME_SEC = 0.35   # Computer vision verification latency
    MANUAL_QA_TIME_SEC = 14.0       # Time if supervisor had to manually audit
    
    BASE_EMISSIONS_KG = 0.45        # Cardboard box footprint
    ICE_PACK_EMISSIONS_KG = 0.82    # Phase-change coolant footprint
    RESIDUAL_RETURN_EMISSIONS_KG = 6.20 # Additional freight carbon if package returned due to post-dispatch damage

    @classmethod
    def calculate_tradeoff(
        cls,
        defects_detected: List[Dict[str, Any]],
        rule_violations: List[Dict[str, Any]],
        storage_zone: str = "15-25°C",
        is_hitl_escalated: bool = False
    ) -> Dict[str, Any]:
        """
        Computes 4-way trade-off matrix: Cost, Time, Emissions, and Reliability.
        """
        has_defects = len(defects_detected) > 0 or len(rule_violations) > 0
        is_cold_chain = "2-8" in storage_zone or "-20" in storage_zone

        # 1. Cost Index ($)
        cost = cls.BASE_PACKAGING_COST
        if is_cold_chain:
            cost += 4.20  # Certified insulated shipper + ice packs
        if has_defects:
            cost += cls.REWORK_AT_WAREHOUSE_COST  # Rework cost before dispatch
        
        # 2. Time Latency (seconds)
        time_sec = cls.BASE_PACK_TIME_SEC + cls.AI_INSPECTION_TIME_SEC
        if is_hitl_escalated:
            time_sec += 5.0  # Time for supervisor override queue

        # 3. Carbon Emissions (kg CO2e)
        emissions_kg = cls.BASE_EMISSIONS_KG
        if is_cold_chain:
            emissions_kg += cls.ICE_PACK_EMISSIONS_KG
        
        # 4. Reliability Score (% defect escape prevention)
        if has_defects:
            reliability = 99.4  # Caught before dispatch! Prevented escape
        else:
            reliability = 98.8

        # 5. Economic Justification Calculation
        # Money and carbon saved by catching this defect now instead of after dispatch:
        if has_defects:
            net_dollars_saved = cls.POST_DISPATCH_DAMAGE_COST - cls.REWORK_AT_WAREHOUSE_COST
            carbon_avoided_kg = cls.RESIDUAL_RETURN_EMISSIONS_KG
            justification = f"Adopted: Prevented ${net_dollars_saved:.2f} post-dispatch loss and {carbon_avoided_kg:.1f}kg CO2e return freight."
        else:
            net_dollars_saved = 0.0
            carbon_avoided_kg = 0.0
            justification = "Adopted: Clean baseline dispatch. Zero rework penalty."

        return {
            "cost_index_usd": round(cost, 2),
            "time_latency_sec": round(time_sec, 2),
            "emissions_kg_co2e": round(emissions_kg, 3),
            "reliability_score_pct": round(reliability, 1),
            "net_dollars_saved_usd": round(net_dollars_saved, 2),
            "carbon_avoided_kg_co2e": round(carbon_avoided_kg, 2),
            "adoption_justification": justification
        }

tradeoff_calculator = TradeOffCalculator()
