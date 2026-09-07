"""
SOP Vector Retriever (RAG Engine)
Indexes pharmaceutical Good Distribution Practice (GDP) standard operating procedures and retrieves citations.
"""
from typing import List, Dict, Any

PHARMA_SOP_DATABASE = [
    {
        "id": "SOP-COLD-01",
        "title": "WHO Annex 5: Cold Chain Transport (2-8°C)",
        "clause": "Clause 4.3.1",
        "text": "Medicinal products requiring storage at 2°C to 8°C must be packed within pre-conditioned insulated shippers with qualified phase-change material to maintain temperature stability for minimum 48 hours transit.",
        "tags": ["2-8°C", "cold_chain", "temperature", "ice_pack"]
    },
    {
        "id": "SOP-SEAL-01",
        "title": "FDA 21 CFR Part 211.132: Tamper-Evident Packaging",
        "clause": "Section 211.132(b)",
        "text": "Each manufacturer and packer who packages a pharmaceutical product for distribution shall package the product in a tamper-evident package with a distinct barrier to entry.",
        "tags": ["tamper_tape", "security_seal", "tape_breach"]
    },
    {
        "id": "SOP-BOX-02",
        "title": "ISTA 3A: Corrugated Shipper Structural Integrity Standard",
        "clause": "ISTA-3A-7",
        "text": "Secondary packaging cartons suffering corner compression or perimeter crush exceeding 10mm must be rejected to prevent dynamic transit shock transfer to primary vials.",
        "tags": ["crushed_corner", "box_damage", "structural_failure"]
    },
    {
        "id": "SOP-DUN-03",
        "title": "Internal QA SOP: Void Fill & Cushioning Ratio",
        "clause": "QA-PKG-SOP-12",
        "text": "All secondary shippers must maintain a maximum void volume ratio of 20%. Dunnage bubble wrap or paper cushioning must immobilize primary cartons against vibration.",
        "tags": ["dunnage", "void_ratio", "bubble_wrap", "vibration"]
    },
    {
        "id": "SOP-LBL-01",
        "title": "GS1 General Specifications: Healthcare Logistics Labeling",
        "clause": "GS1-HCLS-Sec5",
        "text": "Outer shipping containers must bear GS1-128 or DataMatrix barcodes with human-readable interpretation (HRI) compliant with ISO/IEC 15417 verification grade B or higher.",
        "tags": ["barcode", "label_obscured", "gs1", "tracking"]
    }
]

class SopRetriever:
    def retrieve_relevant_sop(self, defect_types: List[str], storage_zone: str) -> List[Dict[str, Any]]:
        """
        Retrieves matching SOP guidelines based on detected defects and storage zone.
        """
        matched: List[Dict[str, Any]] = []
        tags_to_look = set()
        
        for d in defect_types:
            tags_to_look.add(d.lower())
        if "2-8" in storage_zone:
            tags_to_look.add("2-8°c")
            tags_to_look.add("cold_chain")

        for sop in PHARMA_SOP_DATABASE:
            sop_tags = set(sop["tags"])
            if sop_tags.intersection(tags_to_look):
                matched.append(sop)

        return matched if matched else [PHARMA_SOP_DATABASE[0]]

sop_retriever = SopRetriever()
