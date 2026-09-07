"""
Standalone Test Runner for Roboflow Workflow
Usage:
    export ROBOFLOW_API_KEY="your_api_key"
    .venv/bin/python ml/models/test_roboflow_workflow.py --image data/samples/sample_crushed.jpg
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.models.roboflow_client import RoboflowWorkflowClient

def main():
    parser = argparse.ArgumentParser(description="Test Roboflow Workflow for PharmaPack QV")
    parser.add_argument("--image", type=str, default="data/samples/sample_crushed.jpg", help="Path to input image")
    parser.add_argument("--api-key", type=str, default=None, help="Roboflow API key (or set ROBOFLOW_API_KEY env)")
    parser.add_argument("--workspace", type=str, default="partha-bnqgk", help="Roboflow workspace name")
    parser.add_argument("--workflow", type=str, default="pharmapack-damage-detection", help="Workflow ID")
    parser.add_argument("--confidence", type=float, default=0.4, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.3, help="IOU threshold")

    args = parser.parse_args()
    api_key = args.api_key or os.environ.get("ROBOFLOW_API_KEY", "")

    if not api_key:
        print("⚠️ ROBOFLOW_API_KEY not found!")
        print("Please provide it via --api-key YOUR_KEY or: export ROBOFLOW_API_KEY='YOUR_KEY'")
        sys.exit(1)

    image_path = Path(args.image)
    if not image_path.is_absolute():
        image_path = PROJECT_ROOT / image_path

    if not image_path.exists():
        print(f"❌ Image file not found at: {image_path}")
        sys.exit(1)

    print("=" * 60)
    print("🚀 Connecting to Roboflow Serverless Workflow...")
    print(f"   Workspace : {args.workspace}")
    print(f"   Workflow  : {args.workflow}")
    print(f"   Target Img: {image_path.name}")
    print("=" * 60)

    client = RoboflowWorkflowClient(
        api_key=api_key,
        workspace_name=args.workspace,
        workflow_id=args.workflow
    )

    try:
        raw_result = client.run_workflow_on_file(
            image_path=str(image_path),
            confidence=args.confidence,
            iou_threshold=args.iou
        )
        print("\n📦 Raw Workflow Response:")
        print(json.dumps(raw_result, indent=2, default=str))

        parsed = client.parse_defects(raw_result)
        print("\n🔍 Parsed PharmaPack Defect Detections:")
        print(json.dumps(parsed, indent=2))
        print(f"\n✅ Total defects detected: {len(parsed)}")

    except Exception as e:
        print(f"\n❌ Workflow execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
