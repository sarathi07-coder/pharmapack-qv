"""
Amazon Kaputt Dataset Loader (ICCV 2025 Standard)
Parses Amazon Science's Kaputt Logistics Defect Dataset annotations and formats them for YOLOv8 & PyTorch.

Reference & Citation:
@inproceedings{kaputt2025,
  title = {Kaputt: A Large-Scale Dataset for Visual Defect Detection},
  author = {Höfer, Sebastian and Henning, Dorian and Amiranashvili, Artemij and Morrison, Douglas and Tzes, Mariliza and Posner, Ingmar and Matvienko, Marc and Rennola, Alessandro and Milan, Anton},
  booktitle = {Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)},
  month = {October},
  year = {2025},
  address = {Honolulu, Hawaii, USA},
  publisher = {IEEE}
}
Website: https://www.kaputt-dataset.com
"""
import json
from pathlib import Path
from typing import Dict, Any, List
import torch
from torch.utils.data import Dataset
from PIL import Image

KAPUTT_CLASSES = {
    0: "clean_intact",
    1: "deformation_crush",
    2: "penetration_puncture",
    3: "tape_breach_tear",
    4: "label_damage",
    5: "wetness_spillage"
}

class KaputtLogisticsDataset(Dataset):
    """
    PyTorch Dataset wrapper for Amazon Science Kaputt dataset.
    Loads real logistics images and defect annotations.
    """
    def __init__(self, data_dir: str, split: str = "train", transform=None):
        self.data_dir = Path(data_dir)
        self.split = split
        self.transform = transform
        self.samples: List[Dict[str, Any]] = []

        manifest_path = self.data_dir / f"{split}_manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                self.samples = json.load(f)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int):
        item = self.samples[idx]
        img_path = self.data_dir / item["image_path"]
        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        target = {
            "boxes": torch.tensor(item.get("boxes", []), dtype=torch.float32),
            "labels": torch.tensor(item.get("labels", []), dtype=torch.int64),
            "severity": item.get("severity", "minor")
        }

        return image, target
