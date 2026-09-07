"""
Procedural Synthetic Dataset Generator for Pharmaceutical Secondary Packaging
Generates realistic 640x640 packaging images with controlled defects and Ground Truth bounding boxes.
"""
import io
import base64
import random
from typing import Tuple, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import numpy as np

class PharmaPackageGenerator:
    def __init__(self, width: int = 640, height: int = 640):
        self.width = width
        self.height = height

    def generate_package(
        self,
        defect_type: str = "CLEAN",
        zone: str = "2-8°C",
        order_number: str = "PH-ORD-9021",
        awb: str = "AWB-8839210"
    ) -> Tuple[Image.Image, List[Dict[str, Any]]]:
        """
        Generate a synthetic packaging image with ground-truth defect annotations.
        defect_type options: 'CLEAN', 'CRUSHED_CORNER', 'TAPE_BREACH', 'LABEL_OBSCURED', 'MISSING_ICE_PACK'
        """
        # 1. Base industrial background (steel inspection table)
        bg = np.random.randint(45, 55, (self.height, self.width, 3), dtype=np.uint8)
        img = Image.fromarray(bg)
        draw = ImageDraw.Draw(img)

        # 2. Draw corrugated box body
        bx0, by0, bx1, by1 = 100, 100, 540, 540
        box_color = (198, 156, 109)  # Cardboard kraft brown
        draw.rectangle([bx0, by0, bx1, by1], fill=box_color, outline=(140, 100, 60), width=3)

        # Cardboard texture lines
        for y in range(by0 + 15, by1, 12):
            draw.line([(bx0, y), (bx1, y)], fill=(185, 145, 100), width=1)

        # 3. Central carton seam & Tamper-Evident Tape
        seam_y = (by0 + by1) // 2
        draw.line([(bx0, seam_y), (bx1, seam_y)], fill=(130, 90, 50), width=2)
        
        # Tape strip (blue tamper tape for pharma)
        tape_color = (30, 90, 180)
        draw.rectangle([bx0, seam_y - 22, bx1, seam_y + 22], fill=tape_color)
        draw.text((bx0 + 30, seam_y - 8), "TAMPER EVIDENT PHARMA SEAL — SECURE SHIPMENT", fill=(255, 255, 255))

        # 4. Pharma Shipping Label (white rectangle)
        lx0, ly0, lx1, ly1 = 130, 130, 370, 240
        draw.rectangle([lx0, ly0, lx1, ly1], fill=(250, 250, 250), outline=(50, 50, 50), width=2)
        
        # Barcode lines simulation
        draw.text((lx0 + 10, ly0 + 10), "PHARMACEUTICAL CARRIER", fill=(10, 10, 10))
        draw.text((lx0 + 10, ly0 + 26), f"ORDER: {order_number}", fill=(20, 20, 20))
        draw.text((lx0 + 10, ly0 + 42), f"TRACKING: {awb}", fill=(20, 20, 20))
        
        # Simulated GS1 Barcode bars
        bx_start = lx0 + 15
        for i in range(28):
            bw = 2 if (i % 3 == 0) else 4
            draw.rectangle([bx_start, ly0 + 62, bx_start + bw, ly0 + 98], fill=(0, 0, 0))
            bx_start += bw + 3

        # 5. Controlled Zone Badge
        zx0, zy0, zx1, zy1 = 390, 130, 510, 220
        if "2-8" in zone:
            zone_color = (0, 120, 215) # Ice blue
            zone_text = "❄️ COLD CHAIN\n2°C to 8°C\nSTORE REFRIGERATED"
        elif "-20" in zone:
            zone_color = (130, 40, 180) # Deep frost purple
            zone_text = "🧊 FROZEN\n-20°C CRITICAL\nDRY ICE PACK"
        else:
            zone_color = (30, 140, 60) # Amber / green
            zone_text = "🌡️ CRT ROOM\n15°C to 25°C\nDO NOT FREEZE"

        draw.rectangle([zx0, zy0, zx1, zy1], fill=zone_color, outline=(255, 255, 255), width=2)
        draw.text((zx0 + 8, zy0 + 12), zone_text, fill=(255, 255, 255))

        defects: List[Dict[str, Any]] = []

        # 6. Controlled Injected Defect Mutations
        if defect_type == "CRUSHED_CORNER":
            # Crushed top-right corner
            cx0, cy0, cx1, cy1 = 460, 100, 540, 180
            draw.polygon([(460, 100), (540, 180), (540, 100)], fill=(80, 50, 30))
            draw.line([(460, 100), (500, 140), (540, 180)], fill=(30, 20, 10), width=4)
            defects.append({
                "defect_type": "CRUSHED_CORNER",
                "confidence": 0.94,
                "severity": "HIGH",
                "bbox": {"x": 460 / self.width, "y": 100 / self.height, "width": 80 / self.width, "height": 80 / self.height},
                "description": "Corrugated shipper corner crushed; structural integrity compromised."
            })

        elif defect_type == "TAPE_BREACH":
            # Tamper seal split/torn
            tx0, ty0, tx1, ty1 = 300, seam_y - 25, 380, seam_y + 25
            draw.rectangle([tx0, ty0, tx1, ty1], fill=(180, 40, 40)) # Broken red tear
            draw.line([(tx0 + 10, ty0), (tx1 - 10, ty1)], fill=(255, 255, 255), width=3)
            defects.append({
                "defect_type": "TAPE_BREACH",
                "confidence": 0.96,
                "severity": "CRITICAL",
                "bbox": {"x": tx0 / self.width, "y": ty0 / self.height, "width": 80 / self.width, "height": 50 / self.height},
                "description": "Tamper-evident seal punctured or broken; risk of package breach."
            })

        elif defect_type == "LABEL_OBSCURED":
            # Smear / scratch across barcode
            sx0, sy0, sx1, sy1 = lx0 + 10, ly0 + 55, lx1 - 10, ly0 + 105
            draw.rectangle([sx0, sy0, sx1, sy1], fill=(40, 40, 40, 220))
            defects.append({
                "defect_type": "LABEL_OBSCURED",
                "confidence": 0.91,
                "severity": "HIGH",
                "bbox": {"x": sx0 / self.width, "y": sy0 / self.height, "width": (lx1 - lx0 - 20) / self.width, "height": 50 / self.height},
                "description": "GS1 barcode scratched or obscured; automated sorting failure."
            })

        elif defect_type == "MISSING_ICE_PACK":
            # Cold chain shipment missing mandatory insulation indicator
            mx0, my0, mx1, my1 = 200, 360, 440, 480
            draw.rectangle([mx0, my0, mx1, my1], fill=(120, 80, 40), outline=(220, 30, 30), width=3)
            draw.text((mx0 + 15, my0 + 40), "⚠️ VOID: NO ICE PACK DETECTED", fill=(255, 100, 100))
            defects.append({
                "defect_type": "MISSING_ICE_PACK",
                "confidence": 0.95,
                "severity": "CRITICAL",
                "bbox": {"x": mx0 / self.width, "y": my0 / self.height, "width": 240 / self.width, "height": 120 / self.height},
                "description": "Cold chain (2-8°C) shipper missing mandatory phase-change coolant packs."
            })

        return img, defects

    def generate_base64_image(self, defect_type: str = "CLEAN", zone: str = "2-8°C") -> Tuple[str, List[Dict[str, Any]]]:
        img, defects = self.generate_package(defect_type=defect_type, zone=zone)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return b64_str, defects
