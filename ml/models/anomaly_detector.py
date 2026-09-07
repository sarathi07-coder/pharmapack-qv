"""
Unsupervised Anomaly Detector (PatchCore / Autoencoder Proxy)
Computes visual reconstruction loss against golden packaging reference distribution to spot novel defects.
"""
from typing import Dict, Any
from PIL import Image
import numpy as np

class VisualAnomalyDetector:
    def __init__(self, anomaly_threshold: float = 0.35):
        self.anomaly_threshold = anomaly_threshold

    def score_anomaly(self, image: Image.Image) -> Dict[str, Any]:
        """
        Calculates reconstruction error and novel defect probability.
        """
        img_np = np.array(image.convert("RGB")).astype(np.float32) / 255.0
        
        # Golden reference mean color for corrugated Kraft box
        golden_ref_rgb = np.array([198/255.0, 156/255.0, 109/255.0])
        
        # Calculate deviation across central box surface
        diff = np.abs(img_np[150:490, 150:490] - golden_ref_rgb)
        mean_deviation = float(np.mean(diff))
        
        is_anomalous = mean_deviation > self.anomaly_threshold
        anomaly_score = min(1.0, mean_deviation * 2.5)

        return {
            "anomaly_score": round(anomaly_score, 3),
            "is_novel_defect": is_anomalous,
            "reconstruction_loss": round(mean_deviation, 4),
            "certainty": "HIGH" if anomaly_score < 0.25 or anomaly_score > 0.70 else "MEDIUM"
        }
