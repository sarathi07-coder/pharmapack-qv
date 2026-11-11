"""
Zebra Thermal ZPL II Label Protocol Generator
Generates industrial ZPL II shipping & cold-chain verification labels strictly
after PharmaPack QV validates compliance under WHO Annex 5 & FDA 21 CFR Part 11.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class ZebraZPLGenerator:
    """Constructs valid ZPL II commands for Zebra ZT411 / ZT610 warehouse printers."""

    @staticmethod
    def generate_dispatch_label(
        order_number: str,
        awb: str,
        storage_zone: str,
        verdict: str,
        audit_hash: str,
        gross_weight_kg: float = 3.42,
        batch_number: str = "BN-2026-X491",
        operator_badge: str = "OP-101",
        destination: str = "Metro General Hospital Pharmacy",
    ) -> Dict[str, Any]:
        if verdict != "PASS":
            raise PermissionError(
                f"ZPL Label generation BLOCKED: Order {order_number} verdict is {verdict}. "
                "Zero-Tolerance GDP policy prevents label printing on unverified or rejected cartons."
            )

        ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
        zone_banner = "COLD CHAIN 2-8C" if "2-8" in storage_zone else ("DEEP FROZEN -20C" if "-20" in storage_zone else "CRT 15-25C")
        short_hash = audit_hash[:24] if audit_hash else "000000000000000000000000"

        zpl_payload = "\n".join([
            "^XA",
            "^PW812",
            "^LL1218",
            "^FO30,30^GB752,1158,3^FS",
            "^FO30,30^GB752,95,95^FS",
            f"^FO50,55^A0N,42,42^FR^FDPHARMAPACK QV - VERIFIED ({zone_banner})^FS",
            f"^FO50,150^A0N,30,30^FDORDER: {order_number}^FS",
            f"^FO450,150^A0N,30,30^FDAWB: {awb}^FS",
            f"^FO50,195^A0N,26,26^FDDEST: {destination[:42]}^FS",
            f"^FO50,235^A0N,26,26^FDBATCH: {batch_number}   WT: {gross_weight_kg:.2f} KG^FS",
            f"^FO50,275^A0N,24,24^FDOPERATOR: {operator_badge}   VERDICT: PASS (WHO GDP)^FS",
            "^FO50,320^GB712,2,2^FS",
            "^FO70,350^BY3,2,140^BCN,140,Y,N,N",
            f"^FD>;{order_number}>{awb}^FS",
            "^FO50,540^GB712,2,2^FS",
            "^FO50,570^A0N,22,22^FD21 CFR PART 11 CRYPTOGRAPHIC AUDIT SEAL (SHA-256):^FS",
            f"^FO50,605^A0N,20,20^FD{short_hash}...^FS",
            f"^FO50,640^A0N,20,20^FDTIMESTAMP: {ts_utc}^FS",
            "^XZ",
        ])

        return {
            "printer_protocol": "ZPL-II",
            "printer_model": "Zebra ZT411 Industrial (300 DPI)",
            "order_number": order_number,
            "awb": awb,
            "storage_zone": storage_zone,
            "zpl_command": zpl_payload,
            "audit_hash_prefix": short_hash,
            "generated_at_utc": ts_utc,
            "dispatch_cleared": True,
        }


zebra_label_generator = ZebraZPLGenerator()

