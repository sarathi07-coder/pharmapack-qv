"""
Roboflow Serverless Workflow Client for PharmaPack QV
Integrates with Roboflow Workflows:
Workspace: partha-bnqgk
Workflow ID: pharmapack-damage-detection
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image

logger = logging.getLogger(__name__)

class RoboflowWorkflowClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        workspace_name: str = "partha-bnqgk",
        workflow_id: str = "pharmapack-damage-detection",
        api_url: str = "https://serverless.roboflow.com"
    ):
        self.api_key = api_key or os.environ.get("ROBOFLOW_API_KEY", "")
        self.workspace_name = workspace_name
        self.workflow_id = workflow_id
        self.api_url = api_url
        self._client = None

        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            from inference_sdk import InferenceHTTPClient, InferenceConfiguration
            self._client = InferenceHTTPClient(
                api_url=self.api_url,
                api_key=self.api_key
            ).configure(InferenceConfiguration(
                api_key_transport="header"
            ))
            logger.info(f"✅ Roboflow client initialized for workspace: {self.workspace_name}, workflow: {self.workflow_id}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize Roboflow InferenceHTTPClient: {e}")
            self._client = None

    def run_workflow_on_file(
        self,
        image_path: str,
        confidence: float = 0.40,
        iou_threshold: float = 0.30
    ) -> Dict[str, Any]:
        """
        Runs the Roboflow serverless workflow on a local image path.
        """
        if not self._client:
            if not self.api_key:
                raise ValueError("ROBOFLOW_API_KEY is not set. Please provide an API key.")
            self._init_client()
            if not self._client:
                raise RuntimeError("Roboflow InferenceHTTPClient is not available.")

        from PIL import Image
        img = Image.open(image_path)

        return self._client.run_workflow(
            workspace_name=self.workspace_name,
            workflow_id=self.workflow_id,
            images={
                "image": img
            },
            parameters={
                "confidence": confidence,
                "iou_threshold": iou_threshold,
                "class_agnostic_nms": False,
                "max_detections": 1000
            },
            use_cache=True
        )

    def parse_defects(self, workflow_result: Any, min_confidence: float = 0.68) -> List[Dict[str, Any]]:
        """
        Normalizes Roboflow workflow output into PharmaPack standard defect format.
        Filters detections below min_confidence to eliminate false positives on pristine packaging.
        """
        defects = []
        if not workflow_result:
            return defects

        img_w = 1.0
        img_h = 1.0
        predictions = []

        if isinstance(workflow_result, list) and len(workflow_result) > 0:
            first = workflow_result[0]
            if isinstance(first, dict):
                pred_block = first.get("predictions", first.get("output", {}))
                if isinstance(pred_block, dict):
                    img_info = pred_block.get("image", {})
                    img_w = float(img_info.get("width", 1.0))
                    img_h = float(img_info.get("height", 1.0))
                    predictions = pred_block.get("predictions", [])
                elif isinstance(pred_block, list):
                    predictions = pred_block
        elif isinstance(workflow_result, dict):
            pred_block = workflow_result.get("predictions", workflow_result.get("output", {}))
            if isinstance(pred_block, dict):
                img_info = pred_block.get("image", {})
                img_w = float(img_info.get("width", 1.0))
                img_h = float(img_info.get("height", 1.0))
                predictions = pred_block.get("predictions", [])
            elif isinstance(pred_block, list):
                predictions = pred_block

        if not isinstance(predictions, list):
            return defects

        for pred in predictions:
            if not isinstance(pred, dict):
                continue
            conf = float(pred.get("confidence", 0.85))
            if conf < min_confidence:
                continue

            raw_cls = str(pred.get("class", "DEFECT")).upper().replace(" ", "_")

            # Smart classification mapping for pharma compliance
            if any(k in raw_cls for k in ["CARTON", "BOX", "CRUSH", "DEFFECT", "DENT"]):
                defect_type = "CRUSHED_CORNER"
                severity = "HIGH"
                desc = f"Corrugated carton compression damage detected ({round(conf * 100, 1)}% confidence, violates ISTA-3A)."
            elif any(k in raw_cls for k in ["TAPE", "SEAL", "BREACH", "TEAR"]):
                defect_type = "TAPE_BREACH"
                severity = "CRITICAL"
                desc = f"Tamper-evident seal split or punctured ({round(conf * 100, 1)}% confidence, violates FDA 21 CFR §211.132)."
            elif any(k in raw_cls for k in ["ICE", "COLD", "GEL"]):
                defect_type = "MISSING_ICE_PACK"
                severity = "CRITICAL"
                desc = f"Missing temperature-stabilizing refrigerant pack ({round(conf * 100, 1)}% confidence)."
            elif any(k in raw_cls for k in ["LABEL", "BARCODE", "SMEAR"]):
                defect_type = "LABEL_OBSCURED"
                severity = "HIGH"
                desc = f"GS1 shipping barcode unreadable or damaged ({round(conf * 100, 1)}% confidence)."
            elif any(k in raw_cls for k in ["PUNCTURE", "HOLE"]):
                defect_type = "PUNCTURE"
                severity = "HIGH"
                desc = f"Penetration hole in corrugated barrier ({round(conf * 100, 1)}% confidence)."
            else:
                defect_type = raw_cls
                severity = "HIGH"
                desc = f"Roboflow Workflow detected {raw_cls} with {round(conf * 100, 1)}% confidence."

            # Normalize bounding box to [0.0, 1.0] if pixel coordinates were provided
            raw_x = float(pred.get("x", 0.5))
            raw_y = float(pred.get("y", 0.5))
            raw_w = float(pred.get("width", 0.2))
            raw_h = float(pred.get("height", 0.2))

            if img_w > 10.0 and img_h > 10.0:
                norm_w = min(round(raw_w / img_w, 4), 1.0)
                norm_h = min(round(raw_h / img_h, 4), 1.0)
                norm_x = min(max(round((raw_x - raw_w / 2.0) / img_w, 4), 0.0), 1.0)
                norm_y = min(max(round((raw_y - raw_h / 2.0) / img_h, 4), 0.0), 1.0)
            else:
                norm_x, norm_y, norm_w, norm_h = raw_x, raw_y, raw_w, raw_h

            defects.append({
                "defect_type": defect_type,
                "confidence": round(conf, 3),
                "severity": severity,
                "bbox": {
                    "x": norm_x,
                    "y": norm_y,
                    "width": norm_w,
                    "height": norm_h
                },
                "description": desc
            })

        return defects

