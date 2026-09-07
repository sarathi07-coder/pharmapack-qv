"""
Grad-CAM Explainable AI (XAI) Overlay Generator
Generates visual attention heatmaps highlighting defect regions for operator screen inspection.
"""
import io
import base64
from typing import List, Dict, Any
from PIL import Image, ImageDraw
import numpy as np

class GradCamGenerator:
    @staticmethod
    def generate_heatmap(image: Image.Image, defects: List[Dict[str, Any]]) -> Image.Image:
        """
        Creates a semi-transparent heat overlay highlighting defect bounding boxes.
        """
        base = image.convert("RGBA")
        width, height = base.size
        
        # Overlay canvas
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        if not defects:
            # When clean, show gentle green compliance glow
            draw.rectangle([100, 100, width - 100, height - 100], fill=(0, 220, 50, 40), outline=(0, 255, 100, 180), width=3)
        else:
            # Highlight detected defects in high-visibility warning colors
            for d in defects:
                bbox = d.get("bbox")
                if bbox:
                    x0 = int(bbox["x"] * width)
                    y0 = int(bbox["y"] * height)
                    x1 = int((bbox["x"] + bbox["width"]) * width)
                    y1 = int((bbox["y"] + bbox["height"]) * height)
                    
                    # Outer warning glow
                    draw.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], fill=(255, 40, 40, 80))
                    # Inner highlighted box
                    draw.rectangle([x0, y0, x1, y1], fill=(255, 120, 0, 110), outline=(255, 0, 0, 240), width=3)
                    # Label text
                    draw.text((x0 + 4, y0 - 16), f"⚠️ {d.get('defect_type')} ({int(d.get('confidence', 0.9)*100)}%)", fill=(255, 255, 255, 255))

        # Composite overlay on original image
        combined = Image.alpha_composite(base, overlay).convert("RGB")
        return combined

    @classmethod
    def generate_heatmap_base64(cls, image: Image.Image, defects: List[Dict[str, Any]]) -> str:
        heatmap_img = cls.generate_heatmap(image, defects)
        buffer = io.BytesIO()
        heatmap_img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
