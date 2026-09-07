"""
Deterministic Pharmaceutical Packaging Rules Engine
Enforces GDP (Good Distribution Practice) compliance rules for controlled storage zones.
"""
from typing import List, Dict, Any, Optional

class PharmaRulesEngine:
    @staticmethod
    def evaluate_rules(
        storage_zone: str,
        defects: List[Dict[str, Any]],
        ocr_data: Dict[str, Any],
        measured_temp_c: Optional[float] = None,
        gross_weight_kg: Optional[float] = None,
        void_ratio: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Runs deterministic rule checks against package attributes.
        Returns a list of rule violation objects.
        """
        violations: List[Dict[str, Any]] = []
        defect_types = {d["defect_type"] for d in defects}

        # Rule 1: Tamper-Evident Seal Integrity (Mandatory across all pharma zones)
        if "TAPE_BREACH" in defect_types:
            violations.append({
                "rule_code": "SOP-SEAL-01",
                "rule_name": "Tamper-Evident Seal Mandatory Integrity",
                "severity": "CRITICAL",
                "message": "Continuous tamper tape is breached or absent. Possible adulteration.",
                "required_corrective_action": "Repack in new carton and apply unbroken blue security tape."
            })

        # Rule 2: Corrugated Shipper Structural Integrity
        if "CRUSHED_CORNER" in defect_types:
            violations.append({
                "rule_code": "SOP-BOX-02",
                "rule_name": "Shipper Carton Structural Integrity",
                "severity": "HIGH",
                "message": "Corner crush exceeds 10mm deformation. Risk of internal vial breakage.",
                "required_corrective_action": "Transfer products into an undamaged secondary shipper box."
            })

        # Rule 3: Shipping Barcode Scannability
        if "LABEL_OBSCURED" in defect_types or not ocr_data.get("barcode_detected", False):
            violations.append({
                "rule_code": "SOP-LBL-01",
                "rule_name": "GS1-128 Machine-Readable Label Integrity",
                "severity": "HIGH",
                "message": "Shipping label obscured or unreadable by automated scanners.",
                "required_corrective_action": "Reprint dispatch label using thermal Zebra printer."
            })

        # Rule 4: Cold Chain Zone (2-8°C) Temperature & Coolant Verification
        if "2-8" in storage_zone:
            if "MISSING_ICE_PACK" in defect_types:
                violations.append({
                    "rule_code": "SOP-COLD-02",
                    "rule_name": "Phase-Change Refrigerant Pack Mandate",
                    "severity": "CRITICAL",
                    "message": "Cold chain package missing qualified refrigerant packs.",
                    "required_corrective_action": "Insert minimum 4 conditioned phase-change packs (-2°C to 0°C)."
                })
            
            if measured_temp_c is not None and (measured_temp_c < 2.0 or measured_temp_c > 8.0):
                violations.append({
                    "rule_code": "SOP-COLD-01",
                    "rule_name": "Cold Storage Temperature Compliance (2-8°C)",
                    "severity": "CRITICAL",
                    "message": f"Measured temperature {measured_temp_c}°C breaches 2-8°C limits.",
                    "required_corrective_action": "Quarantine package in cold room and notify QC supervisor."
                })

        # Rule 5: Dunnage Cushioning & Void Volume Check
        if void_ratio > 0.20:
            violations.append({
                "rule_code": "SOP-DUN-03",
                "rule_name": "Maximum Allowable Void Volume (<= 20%)",
                "severity": "MEDIUM",
                "message": f"Void volume ratio {int(void_ratio*100)}% exceeds 20% limit.",
                "required_corrective_action": "Add bubble cushioning or air pillows to immobilize contents."
            })

        return violations

rules_engine = PharmaRulesEngine()
