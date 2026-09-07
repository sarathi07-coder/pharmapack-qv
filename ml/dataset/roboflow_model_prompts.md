# 🏷️ Roboflow Prompts & Configuration Guide for Warehouse Damage Detection

This guide provides the exact **prompts, class taxonomy, auto-labeling configurations, and Python scripts** to create and train the Pharmaceutical Packaging Damage Model in **Roboflow**.

---

## 1. Roboflow Project Specification
When creating the project in the [Roboflow Dashboard](https://app.roboflow.com/):

| Setting | Value |
| :--- | :--- |
| **Project Name** | `pharmapack-damage-detection` |
| **Project Type** | **Object Detection** (Bounding Boxes) |
| **Primary Object** | `Packaging Defect` |
| **Target Architecture** | YOLOv8 / YOLOv11 / Roboflow 3.0 |
| **Input Resolution** | 640 × 640 |

---

## 2. 🤖 Auto-Labeling Prompts (Grounding DINO / Florence-2 in Roboflow Annotate)

Use these exact prompts in **Roboflow Annotate ➡️ "Label with Model / Prompts"** (powered by open-vocabulary foundation models like Grounding DINO, Florence-2, and SAM) to auto-annotate thousands of raw conveyor images without drawing manual boxes.

### Combined Detection Prompt (Dot-Separated Syntax)
```text
crushed corner of cardboard box . dented carton edge . collapsed box corner . peeling packaging tape . torn blue security seal . sliced tamper evident tape on box seam . puncture hole in cardboard box . penetrated carton wall . water stain on corrugated carton . intact shipping label
```

---

## 3. Class-by-Class Prompt Taxonomy & Mapping

| Class Name | Roboflow Auto-Label Prompt | Description / What the Model Learns |
| :--- | :--- | :--- |
| `crushed_corner` | `"crushed corner of cardboard box . dented carton edge . crumpled cardboard fluting"` | Detects transit compression, dropped box impacts, and conveyor belt squeeze. |
| `tape_breach` | `"peeled blue tamper tape . broken packaging tape seam . sliced security seal on cardboard carton"` | Identifies broken tamper-evident seals (violates FDA 21 CFR §211.132). |
| `puncture` | `"puncture hole in cardboard box . penetrated carton wall . torn hole in corrugated fiberboard"` | Detects sharp object penetrations from forklift forks or handling tools. |
| `liquid_leak` | `"water stain on cardboard box . liquid leakage discoloration . damp corrugated carton"` | Detects cold-chain condensation or ruptured internal ampoules/vials. |
| `intact_box` | `"clean intact cardboard shipper . undamaged corrugated shipping box"` | Negative baseline reference for zero-defect verification. |

---

## 4. 🎨 Generative Augmentation Prompts (Roboflow Universe / Diffusion)

If you are using generative defect generation in Roboflow or Midjourney/Stable Diffusion to create synthetic training edge cases:

### Prompt 1: Severe Crushed Corner Defect
```text
Industrial macro photograph of a kraft corrugated pharmaceutical shipping carton on a stainless steel warehouse conveyor table. The front-left corner is severely crushed and crumpled with wavy brown fluting fibers torn open and exposed. Over-head fluorescent warehouse lighting, realistic cardboard texture, subtle dust, 8k resolution, photorealistic inspection camera view.
```

### Prompt 2: Sliced Tamper-Evident Tape Breach
```text
Top-down industrial photograph of a cold-chain pharmaceutical shipping box on an inspection station. The blue tamper-evident security tape running across the center flap is sliced open with a utility blade and peeling away, revealing a 5mm gap into the cardboard interior. Medical distribution label partially visible, realistic shadows, sharp macro focus.
```

### Prompt 3: Compliant Zero-Defect Baseline Shipper
```text
Crisp industrial photograph of a pristine, compliant pharmaceutical cold-chain corrugated shipper box resting on an industrial stainless-steel packing bench. Perfect 90-degree crisp corners, unbroken blue security seal tape with "TAMPER EVIDENT" printed along the seam, sharp white GS1-128 shipping barcode label, 2-8°C refrigerated storage badge.
```

---

## 5. Roboflow Dataset Preprocessing & Augmentations

Apply these settings in the **Generate Version** tab to maximize generalization across changing warehouse lighting:

### Preprocessing
* **Auto-Orient**: Applied (corrects camera tilt)
* **Resize**: 640 × 640 (Stretch or Fit with Black Border)
* **Grayscale / Auto-Contrast**: Disabled (tamper tape color is critical for cold-chain)

### Augmentations (3x Dataset Multiplier)
* **Horizontal Flip**: Yes (boxes arrive in both conveyor directions)
* **Vertical Flip**: No (boxes remain upright on conveyors)
* **Crop**: 0% to 15% (simulates partial camera occlusion)
* **Brightness**: -15% to +15% (simulates shifting warehouse bay lighting)
* **Blur**: Up to 1.5px (simulates conveyor belt motion blur)
* **Mosaic**: Enabled (helps small puncture & tape tear detection)

---

## 6. 🚀 Python Automation Script: Create Project & Train via Roboflow API

Run this script to automatically create the project, upload images, and trigger cloud training:

```python
import os
from roboflow import Roboflow

# 1. Initialize Roboflow client
API_KEY = os.environ.get("ROBOFLOW_API_KEY", "YOUR_API_KEY_HERE")
rf = Roboflow(api_key=API_KEY)

# 2. Get Workspace & Create/Retrieve Project
workspace = rf.workspace()
project = workspace.create_project(
    project_name="pharmapack-damage-detection",
    project_type="object-detection",
    project_license="Private",
    annotation="Packaging Defect"
)

# 3. Upload images for prompt-based labeling
sample_images = [
    "data/samples/sample_clean.jpg",
    "data/samples/sample_crushed.jpg",
    "data/samples/sample_tamper_breach.jpg"
]
for img_path in sample_images:
    project.upload(image_path=img_path, split="train")

print("✅ Images uploaded to Roboflow. Open Annotate tab to apply Auto-Label prompts!")

# 4. Generate version and start Roboflow Train
# version = project.generate_version(settings={...})
# model = version.train(model_type="yolov8x")
```
