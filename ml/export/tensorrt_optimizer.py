"""
Edge Neural Inference Engine & TensorRT / Jetson Deployment Adapter
Loads quantized INT8 TorchScript artifacts for sub-15ms warehouse edge classification
and provides Jetson Orin TensorRT engine build metadata.
"""
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

import numpy as np
from PIL import Image
import torch

from ml.export.edge_quantizer import (
    ARTIFACTS_DIR,
    BENCHMARK_REPORT_PATH,
    CLASS_NAMES,
    preprocess_pil,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class EdgeNeuralInferenceEngine:
    """Thread-safe quantized INT8 edge classifier for warehouse stations."""

    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: float = 0.72):
        self.model_path = model_path or (ARTIFACTS_DIR / "pharma_edge_int8.pt")
        self.fp32_fallback_path = ARTIFACTS_DIR / "pharma_edge_fp32.pt"
        self.confidence_threshold = confidence_threshold
        self.model: Optional[torch.jit.ScriptModule] = None
        self.engine_mode = "UNINITIALIZED"
        self._load_model()

    def _load_model(self) -> None:
        torch.backends.quantized.engine = "qnnpack"
        target = self.model_path if self.model_path.exists() else self.fp32_fallback_path
        if target.exists():
            try:
                self.model = torch.jit.load(str(target), map_location="cpu")
                self.model.eval()
                self.engine_mode = "INT8_QNNPACK" if target == self.model_path else "FP32_TORCHSCRIPT"
                # Warm up TorchScript QNNPACK kernels once at load so inference meets <15ms SLA
                dummy = torch.zeros(1, 3, 128, 128)
                with torch.no_grad():
                    for _ in range(3):
                        self.model(dummy)
            except Exception:
                self.model = None
                self.engine_mode = "UNAVAILABLE"

    def is_ready(self) -> bool:
        return self.model is not None

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """Runs single-frame edge neural classification with wall-clock timing."""
        if not self.model:
            return {
                "available": False,
                "engine_mode": self.engine_mode,
                "predicted_class": "UNKNOWN",
                "confidence": 0.0,
                "latency_ms": 0.0,
                "probabilities": {},
            }

        t0 = time.perf_counter()
        tensor = preprocess_pil(image).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
        t1 = time.perf_counter()

        top_idx = int(np.argmax(probs))
        top_class = CLASS_NAMES[top_idx]
        top_conf = float(probs[top_idx])

        return {
            "available": True,
            "engine_mode": self.engine_mode,
            "predicted_class": top_class,
            "confidence": round(top_conf, 4),
            "latency_ms": round((t1 - t0) * 1000.0, 3),
            "probabilities": {cls_name: round(float(probs[i]), 4) for i, cls_name in enumerate(CLASS_NAMES)},
        }

    @staticmethod
    def get_benchmark_summary() -> Dict[str, Any]:
        """Loads persisted FP32 vs INT8 vs MPS edge quantization metrics."""
        if BENCHMARK_REPORT_PATH.exists():
            return json.loads(BENCHMARK_REPORT_PATH.read_text())
        return {"status": "NOT_YET_BENCHMARKED"}


class TensorRTOptimizer:
    """Provides NVIDIA Jetson Orin / TensorRT deployment manifests & ONNX build specs."""

    @staticmethod
    def get_deployment_manifest() -> Dict[str, Any]:
        spec_path = ARTIFACTS_DIR / "tensorrt_engine_spec.json"
        if spec_path.exists():
            return json.loads(spec_path.read_text())
        return {
            "model_name": "PharmaEdgeNet-v2",
            "status": "SPEC_NOT_GENERATED",
        }

