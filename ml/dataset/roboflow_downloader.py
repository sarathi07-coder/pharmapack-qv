"""
Roboflow Logistics Package Damage Dataset Integrator
Downloads and formats real-world packaging damage datasets from Roboflow Universe for YOLOv8 training.
"""
import os
from pathlib import Path
from roboflow import Roboflow

DATASET_ROOT = Path(__file__).resolve().parent.parent.parent / "data" / "real_datasets"

class RoboflowLogisticsDownloader:
    """
    Downloads real-world logistics parcel damage datasets from Roboflow Universe.
    Dataset: smart-damage-detection-for-logistics-packages-using-computer-vision
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ROBOFLOW_API_KEY", "")

    def download_dataset(self, version: int = 1, export_format: str = "yolov8") -> Path:
        output_dir = DATASET_ROOT / "roboflow_parcel_damage"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not self.api_key:
            print("⚠️ No ROBOFLOW_API_KEY found in environment.")
            print("ℹ️ To download automatically, set ROBOFLOW_API_KEY or use public dataset URL:")
            print("👉 https://universe.roboflow.com/smart-damage-detection-for-logistics-packages-using-computer-vision/damage-detection-for-packages")
            return output_dir

        rf = Roboflow(api_key=self.api_key)
        project = rf.workspace("smart-damage-detection-for-logistics-packages-using-computer-vision").project("damage-detection-for-packages")
        dataset = project.version(version).download(export_format, location=str(output_dir))
        print(f"✅ Real parcel damage dataset downloaded to: {dataset.location}")
        return Path(dataset.location)

if __name__ == "__main__":
    downloader = RoboflowLogisticsDownloader()
    downloader.download_dataset()
