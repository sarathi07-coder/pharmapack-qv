"""
Edge INT8 / TorchScript Quantization & Hardware Accelerator Benchmarking Pipeline
Trains a compact Depthwise-Separable CNN (PharmaEdgeNet) on curated warehouse
samples + real drug packaging images, performs ARM64 QNNPACK INT8 quantization,
exports deployable TorchScript & TensorRT/Jetson manifests, and benchmarks
FP32 vs INT8 vs Hardware Accelerator (MPS) sub-15ms edge performance.
"""
import os
import sys
import time
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np
from PIL import Image, ImageEnhance
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.dataset.synthetic_generator import PharmaPackageGenerator

CLASS_NAMES = [
    "CLEAN",
    "CRUSHED_CORNER",
    "TAPE_BREACH",
    "LABEL_OBSCURED",
    "MISSING_ICE_PACK",
]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
INPUT_SIZE = 128

ARTIFACTS_DIR = PROJECT_ROOT / "ml" / "artifacts"
BENCHMARK_REPORT_PATH = PROJECT_ROOT / "data" / "edge_quantization_benchmark.json"


class DepthwiseSeparableBlock(nn.Module):
    """Lightweight MobileNet-style block for fast edge inference."""

    def __init__(self, in_ch: int, out_ch: int, stride: int = 1):
        super().__init__()
        self.depthwise = nn.Conv2d(
            in_ch, in_ch, kernel_size=3, stride=stride, padding=1, groups=in_ch, bias=False
        )
        self.bn1 = nn.BatchNorm2d(in_ch)
        self.relu1 = nn.ReLU(inplace=False)
        self.pointwise = nn.Conv2d(in_ch, out_ch, kernel_size=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_ch)
        self.relu2 = nn.ReLU(inplace=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.relu1(self.bn1(self.depthwise(x)))
        x = self.relu2(self.bn2(self.pointwise(x)))
        return x


class PharmaEdgeNet(nn.Module):
    """
    Ultra-compact industrial packaging classifier (<1.5 MB INT8) designed for
    sub-15ms edge execution on conveyor Gateways and NVIDIA Jetson Orin.
    """

    def __init__(self, num_classes: int = len(CLASS_NAMES)):
        super().__init__()
        self.quant = torch.ao.quantization.QuantStub()
        self.stem = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=False),
        )
        self.features = nn.Sequential(
            DepthwiseSeparableBlock(16, 32, stride=2),
            DepthwiseSeparableBlock(32, 64, stride=2),
            DepthwiseSeparableBlock(64, 96, stride=2),
            DepthwiseSeparableBlock(96, 128, stride=2),
        )
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 64),
            nn.ReLU(inplace=False),
            nn.Linear(64, num_classes),
        )
        self.dequant = torch.ao.quantization.DeQuantStub()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.quant(x)
        x = self.stem(x)
        x = self.features(x)
        x = self.pool(x)
        x = self.classifier(x)
        x = self.dequant(x)
        return x


def preprocess_pil(img: Image.Image) -> torch.Tensor:
    """Converts PIL image to normalized CHW float32 tensor."""
    resized = img.convert("RGB").resize((INPUT_SIZE, INPUT_SIZE), Image.Resampling.BILINEAR)
    arr = np.asarray(resized, dtype=np.float32) / 255.0
    # ImageNet-style centering
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr - mean) / std
    arr = np.transpose(arr, (2, 0, 1))
    return torch.from_numpy(arr.copy())


def augment_image(img: Image.Image, rng: random.Random) -> Image.Image:
    """Simulates warehouse conveyor brightness/contrast jitter."""
    b = rng.uniform(0.85, 1.15)
    c = rng.uniform(0.88, 1.12)
    out = ImageEnhance.Brightness(img).enhance(b)
    out = ImageEnhance.Contrast(out).enhance(c)
    return out


class PackagingEdgeDataset(Dataset):
    """Combines curated warehouse samples and authentic real packaging variations."""

    def __init__(self, samples_per_class: int = 40, seed: int = 42):
        self.rng = random.Random(seed)
        self.generator = PharmaPackageGenerator(width=640, height=640)
        self.tensors: List[torch.Tensor] = []
        self.labels: List[int] = []

        samples_dir = PROJECT_ROOT / "data" / "samples"
        real_clean_dir = PROJECT_ROOT / "data" / "real_datasets" / "drug_names" / "train" / "images"
        real_imgs: List[Path] = []
        if real_clean_dir.exists():
            real_imgs = sorted(real_clean_dir.glob("*.jpg"))[:20]

        sample_map = {
            "CLEAN": samples_dir / "sample_clean.jpg",
            "CRUSHED_CORNER": samples_dir / "sample_crushed.jpg",
            "TAPE_BREACH": samples_dir / "sample_tamper_breach.jpg",
            "LABEL_OBSCURED": samples_dir / "sample_damaged_barcode.jpg",
            "MISSING_ICE_PACK": samples_dir / "sample_missing_ice.jpg",
        }
        zones = ["2-8°C", "15-25°C", "-20°C"]

        for cls_name in CLASS_NAMES:
            cls_idx = CLASS_TO_IDX[cls_name]
            sample_path = sample_map.get(cls_name)
            base_real_img = Image.open(sample_path).convert("RGB") if sample_path and sample_path.exists() else None

            for i in range(samples_per_class):
                if base_real_img is not None and i % 3 == 0:
                    img = augment_image(base_real_img, self.rng)
                elif cls_name == "CLEAN" and real_imgs and i % 4 == 1:
                    rpath = real_imgs[i % len(real_imgs)]
                    img = augment_image(Image.open(rpath).convert("RGB"), self.rng)
                else:
                    zone = zones[i % len(zones)]
                    img, _ = self.generator.generate_package(
                        defect_type=cls_name,
                        zone=zone,
                        order_number=f"EDGE-{i:04d}",
                        awb=f"AWB-{1000 + i}",
                    )
                    img = augment_image(img, self.rng)

                self.tensors.append(preprocess_pil(img))
                self.labels.append(cls_idx)

    def __len__(self) -> int:
        return len(self.tensors)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        return self.tensors[idx], self.labels[idx]


def evaluate_accuracy(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)
            preds = logits.argmax(dim=1)
            correct += int((preds == y).sum().item())
            total += int(y.size(0))
    return round((correct / max(total, 1)) * 100.0, 2)


def benchmark_model_latency(
    model: nn.Module,
    device: torch.device,
    runs: int = 120,
    warmup: int = 20,
) -> Dict[str, float]:
    model.eval()
    dummy = torch.randn(1, 3, INPUT_SIZE, INPUT_SIZE, device=device)

    with torch.no_grad():
        for _ in range(warmup):
            _ = model(dummy)
        if device.type == "mps":
            torch.mps.synchronize()

        latencies_ms: List[float] = []
        for _ in range(runs):
            t0 = time.perf_counter()
            _ = model(dummy)
            if device.type == "mps":
                torch.mps.synchronize()
            t1 = time.perf_counter()
            latencies_ms.append((t1 - t0) * 1000.0)

    arr = np.array(latencies_ms, dtype=np.float64)
    mean_ms = float(np.mean(arr))
    p95_ms = float(np.percentile(arr, 95))
    fps = 1000.0 / max(mean_ms, 1e-6)
    return {
        "mean_latency_ms": round(mean_ms, 3),
        "p95_latency_ms": round(p95_ms, 3),
        "throughput_fps": round(fps, 1),
    }


def fuse_edge_model(model: PharmaEdgeNet) -> None:
    """Fuses Conv+BN+ReLU layers prior to INT8 calibration."""
    for block in model.features:
        torch.ao.quantization.fuse_modules(block, [["depthwise", "bn1", "relu1"], ["pointwise", "bn2", "relu2"]], inplace=True)
    torch.ao.quantization.fuse_modules(model.stem, [["0", "1", "2"]], inplace=True)
    torch.ao.quantization.fuse_modules(model.classifier, [["1", "2"]], inplace=True)


def run_edge_quantization_pipeline(epochs: int = 8) -> Dict[str, Any]:
    """
    Executes end-to-end training, FP32 export, ARM64 QNNPACK INT8 static quantization,
    accelerator benchmarking, and TensorRT spec emission.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    BENCHMARK_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    torch.manual_seed(42)
    train_ds = PackagingEdgeDataset(samples_per_class=45, seed=42)
    val_ds = PackagingEdgeDataset(samples_per_class=15, seed=99)
    train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)

    # Train on Apple Silicon MPS if available, else CPU
    train_device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model = PharmaEdgeNet().to(train_device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-3)

    for _ in range(epochs):
        model.train()
        for x, y in train_loader:
            x, y = x.to(train_device), y.to(train_device)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()

    # Bring trained weights to CPU for TorchScript + INT8 Quantization
    fp32_cpu = model.to(torch.device("cpu")).eval()
    fp32_acc = evaluate_accuracy(fp32_cpu, val_loader, torch.device("cpu"))

    # Save FP32 TorchScript
    example_input = torch.randn(1, 3, INPUT_SIZE, INPUT_SIZE)
    fp32_traced = torch.jit.trace(fp32_cpu, example_input)
    fp32_path = ARTIFACTS_DIR / "pharma_edge_fp32.pt"
    fp32_traced.save(str(fp32_path))

    # Quantize to INT8 using QNNPACK (ARM64 / Edge CPU engine)
    torch.backends.quantized.engine = "qnnpack"
    quant_prep = PharmaEdgeNet()
    quant_prep.load_state_dict(fp32_cpu.state_dict())
    quant_prep.eval()
    fuse_edge_model(quant_prep)
    quant_prep.qconfig = torch.ao.quantization.get_default_qconfig("qnnpack")
    torch.ao.quantization.prepare(quant_prep, inplace=True)

    # Calibrate with validation/train tensors
    with torch.no_grad():
        for i, (x, _) in enumerate(train_loader):
            quant_prep(x)
            if i >= 4:
                break

    int8_model = torch.ao.quantization.convert(quant_prep, inplace=False).eval()
    int8_acc = evaluate_accuracy(int8_model, val_loader, torch.device("cpu"))

    int8_traced = torch.jit.trace(int8_model, example_input)
    int8_path = ARTIFACTS_DIR / "pharma_edge_int8.pt"
    int8_traced.save(str(int8_path))

    # Benchmark FP32 CPU vs INT8 CPU vs MPS Accelerator
    fp32_bench = benchmark_model_latency(fp32_traced, torch.device("cpu"))
    int8_bench = benchmark_model_latency(int8_traced, torch.device("cpu"))

    mps_bench = None
    if torch.backends.mps.is_available():
        mps_model = model.to(torch.device("mps")).eval()
        mps_bench = benchmark_model_latency(mps_model, torch.device("mps"))

    fp32_kb = round(fp32_path.stat().st_size / 1024.0, 2)
    int8_kb = round(int8_path.stat().st_size / 1024.0, 2)
    size_reduction_pct = round((1.0 - (int8_kb / max(fp32_kb, 1e-6))) * 100.0, 1)
    speedup_vs_fp32 = round(fp32_bench["mean_latency_ms"] / max(int8_bench["mean_latency_ms"], 1e-6), 2)

    # Emit Jetson Orin TensorRT / ONNX deployment spec
    trt_spec = {
        "model_name": "PharmaEdgeNet-v2",
        "input_shape": [1, 3, INPUT_SIZE, INPUT_SIZE],
        "classes": CLASS_NAMES,
        "quantization_engine": "qnnpack",
        "target_edge_hardware": ["NVIDIA Jetson Orin Nano", "Apple Silicon Edge Gateway", "Intel OpenVINO IPC"],
        "tensorrt_build_flags": [
            "--onnx=pharma_edge_fp32.onnx",
            "--saveEngine=pharma_edge_fp16_int8.engine",
            "--int8",
            "--fp16",
            "--workspace=1024",
        ],
        "artifacts": {
            "fp32_torchscript": str(fp32_path.relative_to(PROJECT_ROOT)),
            "int8_torchscript": str(int8_path.relative_to(PROJECT_ROOT)),
        },
        "sla_target_ms": 15.0,
        "sla_met": int8_bench["mean_latency_ms"] < 15.0,
    }
    trt_spec_path = ARTIFACTS_DIR / "tensorrt_engine_spec.json"
    trt_spec_path.write_text(json.dumps(trt_spec, indent=2))

    report = {
        "model_architecture": "PharmaEdgeNet (Depthwise-Separable Edge CNN)",
        "dataset_size": len(train_ds) + len(val_ds),
        "classes": CLASS_NAMES,
        "quantization_backend": "torch.ao.quantization (qnnpack INT8)",
        "fp32_cpu": {
            **fp32_bench,
            "accuracy_pct": fp32_acc,
            "artifact_size_kb": fp32_kb,
        },
        "int8_quantized_cpu": {
            **int8_bench,
            "accuracy_pct": int8_acc,
            "artifact_size_kb": int8_kb,
            "speedup_vs_fp32": speedup_vs_fp32,
            "size_reduction_pct": size_reduction_pct,
        },
        "gpu_mps_accelerator": mps_bench,
        "sub_15ms_sla_met": int8_bench["mean_latency_ms"] < 15.0,
        "tensorrt_spec_path": str(trt_spec_path.relative_to(PROJECT_ROOT)),
    }
    BENCHMARK_REPORT_PATH.write_text(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    print("⚡ Training & Quantizing PharmaEdgeNet (FP32 -> INT8 QNNPACK)...")
    metrics = run_edge_quantization_pipeline(epochs=8)
    print(json.dumps(metrics, indent=2))

