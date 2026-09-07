"""
Database Seeding Script — Populates realistic initial warehouse records, operators, orders, and test images.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.session import sync_engine
from backend.models.base import Base
from backend.models.operator import Operator
from backend.models.dispatch import DispatchOrder
from backend.models.audit import AuditLog, compute_sha256_hash
from backend.core.security import get_password_hash
from ml.dataset.synthetic_generator import PharmaPackageGenerator

def seed_database():
    print("🌱 Initializing database schema...")
    Base.metadata.create_all(bind=sync_engine)

    with Session(sync_engine) as session:
        # Check if already seeded
        existing_op = session.query(Operator).first()
        if existing_op:
            print("✅ Database already seeded. Skipping operator generation.")
            return

        print("👷 Creating initial warehouse operators and supervisors...")
        operators = [
            Operator(
                badge_number="OP-101",
                full_name="Rajesh Kumar",
                role="OPERATOR",
                hashed_password=get_password_hash("packer123"),
                shift_name="Morning Shift A",
                current_station_id="STATION-01",
                consecutive_hours_worked=2.5,
                fatigue_risk_score=0.15,
                total_packages_inspected=142,
                total_defects_caught=9,
                compliance_rating=99.1
            ),
            Operator(
                badge_number="OP-102",
                full_name="Elena Rostova",
                role="OPERATOR",
                hashed_password=get_password_hash("packer123"),
                shift_name="Morning Shift A",
                current_station_id="STATION-02",
                consecutive_hours_worked=6.8,
                fatigue_risk_score=0.72,  # Approaching fatigue threshold
                total_packages_inspected=310,
                total_defects_caught=18,
                compliance_rating=96.4
            ),
            Operator(
                badge_number="SUP-501",
                full_name="Marcus Vance",
                role="SUPERVISOR",
                hashed_password=get_password_hash("supervisor123"),
                shift_name="Floor Supervisor",
                current_station_id="HUB-01",
                consecutive_hours_worked=4.0,
                fatigue_risk_score=0.20,
                total_packages_inspected=850,
                total_defects_caught=64,
                compliance_rating=99.8
            ),
            Operator(
                badge_number="QA-901",
                full_name="Dr. Sarah Jenkins",
                role="QA_AUDITOR",
                hashed_password=get_password_hash("auditor123"),
                shift_name="Quality Assurance",
                current_station_id="QA-LAB",
                consecutive_hours_worked=3.0,
                fatigue_risk_score=0.10,
                total_packages_inspected=1200,
                total_defects_caught=110,
                compliance_rating=100.0
            )
        ]
        session.add_all(operators)
        session.commit()

        print("📦 Creating dispatch orders across controlled storage zones...")
        orders = [
            DispatchOrder(
                order_number="PH-ORD-9021",
                tracking_awb="AWB-8839210",
                destination_facility="Metro General Hospital Oncology Pharmacy",
                storage_zone="2-8°C",
                min_temp_c=2.0,
                max_temp_c=8.0,
                is_cold_chain=True,
                required_box_type="VIP_INSULATED_SHIPPER",
                requires_ice_packs=True,
                ice_pack_count=4.0,
                requires_tamper_tape=True,
                max_gross_weight_kg=6.5,
                status="PENDING_INSPECTION"
            ),
            DispatchOrder(
                order_number="PH-ORD-9022",
                tracking_awb="AWB-8839211",
                destination_facility="St. Jude Pediatric Clinic",
                storage_zone="15-25°C",
                min_temp_c=15.0,
                max_temp_c=25.0,
                is_cold_chain=False,
                required_box_type="STANDARD_CORRUGATED",
                requires_ice_packs=False,
                ice_pack_count=0.0,
                requires_tamper_tape=True,
                max_gross_weight_kg=4.2,
                status="PENDING_INSPECTION"
            ),
            DispatchOrder(
                order_number="PH-ORD-9023",
                tracking_awb="AWB-8839212",
                destination_facility="Biotech Research Center",
                storage_zone="-20°C",
                min_temp_c=-25.0,
                max_temp_c=-15.0,
                is_cold_chain=True,
                required_box_type="DRY_ICE_DEEP_FREEZE",
                requires_ice_packs=True,
                ice_pack_count=6.0,
                requires_tamper_tape=True,
                max_gross_weight_kg=9.0,
                status="PENDING_INSPECTION"
            )
        ]
        session.add_all(orders)
        session.commit()

        print("📸 Generating procedural sample packaging images in data/samples...")
        generator = PharmaPackageGenerator()
        sample_configs = [
            ("sample_clean.jpg", "CLEAN", "2-8°C", "PH-ORD-9021", "AWB-8839210"),
            ("sample_crushed.jpg", "CRUSHED_CORNER", "15-25°C", "PH-ORD-9022", "AWB-8839211"),
            ("sample_tamper_breach.jpg", "TAPE_BREACH", "2-8°C", "PH-ORD-9023", "AWB-8839212"),
            ("sample_missing_ice.jpg", "MISSING_ICE_PACK", "2-8°C", "PH-ORD-9024", "AWB-8839213"),
        ]

        for filename, defect, zone, ord_num, awb in sample_configs:
            img, _ = generator.generate_package(defect_type=defect, zone=zone, order_number=ord_num, awb=awb)
            img_path = settings.SAMPLES_DIR / filename
            img.save(img_path, format="JPEG")

        print("🔒 Initializing 21 CFR Part 11 Genesis Audit Record...")
        genesis_ts = datetime.now(timezone.utc).isoformat()
        genesis_prev_hash = "0" * 64
        genesis_payload = {"system_initialized": True, "gdp_rules_version": "2026.1"}
        genesis_block_hash = compute_sha256_hash(
            genesis_prev_hash,
            "SYSTEM_INITIALIZE",
            "SYSTEM",
            "ROOT",
            genesis_payload,
            genesis_ts
        )

        genesis_audit = AuditLog(
            action="SYSTEM_INITIALIZE",
            user_badge="SYSTEM",
            user_role="ADMIN",
            entity_type="SYSTEM",
            entity_id="ROOT",
            previous_block_hash=genesis_prev_hash,
            block_hash=genesis_block_hash,
            details=genesis_payload,
            digital_signature="SYSTEM_CERT_SHA256_ROOT"
        )
        session.add(genesis_audit)
        session.commit()

        print("🎉 Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
