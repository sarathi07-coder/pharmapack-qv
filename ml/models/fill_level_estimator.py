"""
Fill Level & Void Ratio Estimator
Measures empty box volume and cushioning dunnage compliance.
"""
from typing import Dict, Any
from PIL import Image
import numpy as np

class FillLevelEstimator:
    def estimate_void_ratio(self, image: Image.Image) -> Dict[str, Any]:
        """
        Estimate box interior fill ratio and dunnage padding compliance.
        """
        img_np = np.array(image.convert("L"))
        # Analyze inner box region
        h, w = img_np.shape
        inner = img_np[int(h * 0.2):int(h * 0.8), int(w * 0.2):int(w * 0.8)]
        
        # Calculate texture variance (dunnage bubble wrap / air pillows create high spatial variance)
        variance = np.var(inner)
        estimated_fill_pct = min(100.0, max(40.0, (variance / 50.0) * 10.0 + 65.0))
        void_ratio = max(0.0, (100.0 - estimated_fill_pct) / 100.0)

        dunnage_sufficient = void_ratio <= 0.20  # Max 20% void allowed by Pharma SOP

        return {
            "fill_percentage": round(estimated_fill_pct, 1),
            "void_ratio": round(void_ratio, 3),
            "dunnage_sufficient": dunnage_sufficient,
            "recommended_action": "NO_ACTION" if dunnage_sufficient else "ADD_BUBBLE_DUNNAGE"
        }
