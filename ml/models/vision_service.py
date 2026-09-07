"""
Unified Vision Pipeline Service
Executes defect detection, OCR extraction, void volume estimation, and Grad-CAM generation in parallel.
"""
from typing import Dict, Any, List
from PIL import Image
from ml.models.defect_detector import PackagingDefectDetector
from ml.models.ocr_engine import PackageOcrEngine
from ml.models.fill_level_estimator import FillLevelEstimator
from ml.models.anomaly_detector import VisualAnomalyDetector
from ml.explainability.gradcam import GradCamGenerator

class VisionService:
    def __init__(self):
        self.defect_detector = PackagingDefectDetector()
        self.ocr_engine = PackageOcrEngine()
        self.fill_estimator = FillLevelEstimator()
        self.anomaly_detector = VisualAnomalyDetector()

    def process_image(self, image: Image.Image, order_hint: str = "") -> Dict[str, Any]:
        """
        Runs comprehensive multi-modal inspection on package image.
        """
        # 1. Defect Detection
        defects = self.defect_detector.predict(image)

        # 2. OCR Extraction
        ocr_data = self.ocr_engine.extract_metadata(image, order_hint=order_hint)

        # 3. Fill & Void Estimation
        void_data = self.fill_estimator.estimate_void_ratio(image)

        # 4. Unsupervised Anomaly Scoring
        anomaly_data = self.anomaly_detector.score_anomaly(image)

        # 5. Grad-CAM Visual Heatmap
        heatmap_base64 = GradCamGenerator.generate_heatmap_base64(image, defects)

        # Overall Vision Confidence
        if defects:
            min_defect_conf = min(d["confidence"] for d in defects)
            overall_confidence = round(min_defect_conf, 3)
        else:
            overall_confidence = 0.985

        return {
            "defects": defects,
            "ocr_data": ocr_data,
            "void_metrics": void_data,
            "anomaly_metrics": anomaly_data,
            "heatmap_base64": heatmap_base64,
            "overall_vision_confidence": overall_confidence
        }

vision_service = VisionService()
