"""
YOLOv8 Real Logistics Package Defect Training Pipeline
Trains real-time computer vision defect detector on real parcel damage datasets (Kaputt & Roboflow).
Exports trained weights to ONNX format for sub-150ms edge inference.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ultralytics import YOLO

def train_defect_detector(
    model_variant: str = "yolov8n.pt",
    data_yaml: str = "ml/dataset/real_damage_data.yaml",
    epochs: int = 50,
    imgsz: int = 640,
    batch_size: int = 16,
    device: str = "cpu"  # 'mps' for Apple Silicon, '0' for CUDA GPU, 'cpu' fallback
):
    print(f"🚀 Initializing YOLOv8 Defect Detection Training with real dataset config: {data_yaml}")
    print(f"📦 Model Backbone: {model_variant} | Image Size: {imgsz}x{imgsz} | Epochs: {epochs}")

    # 1. Load Pretrained YOLOv8 Backbone
    model = YOLO(model_variant)

    # 2. Train on Real Logistics Damage Dataset
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        device=device,
        project="runs/defect_detect",
        name="real_parcel_damage_model",
        exist_ok=True,
        # Industrial augmentations: lighting shifts, warehouse perspective tilt
        degrees=10.0,
        translate=0.1,
        scale=0.2,
        flipud=0.0,  # Never flip boxes upside down in pharma!
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1
    )

    print("📊 Training Completed. Evaluating validation metrics (mAP@50, mAP@50-95)...")
    metrics = model.val()
    print(f"✅ Validation mAP@50: {metrics.box.map50:.4f} | mAP@50-95: {metrics.box.map:.4f}")

    # 3. Export to High-Speed ONNX Runtime for Warehouse Edge Deployment
    print("⚡ Exporting fine-tuned weights to ONNX format for edge deployment...")
    onnx_path = model.export(format="onnx", imgsz=imgsz, dynamic=True)
    print(f"🎉 Edge ONNX Model ready at: {onnx_path}")
    return onnx_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train YOLOv8 on real logistics damage dataset")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLOv8 variant (yolov8n.pt, yolov8s.pt)")
    args = parser.parse_args()

    train_defect_detector(model_variant=args.model, epochs=args.epochs)
