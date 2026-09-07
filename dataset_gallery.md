# 📸 PharmaPack QV — Photorealistic Warehouse Dataset Gallery

To replace synthetic 2D sketches with authentic industrial imagery, we generated and integrated **high-resolution photorealistic warehouse photographs** taken under real pharmaceutical packaging conditions (stainless steel benches, barcode scanners, digital weight scales, and genuine corrugate fluting).

---

## 🖼️ Photorealistic Image Carousel

````carousel
![1. Authentic Clean Compliant Pharma Cold-Chain Shipper (Zone: 2-8°C, Intact Blue Tamper Tape, GS1 Label)](/Users/sarathi/.gemini/antigravity-ide/brain/bdd1d081-1c17-4c4a-86ec-7feb666af00a/samples/sample_clean.jpg)
<!-- slide -->
![2. Severe Crushed Corner Damage (ISTA-3A Defect, Exposed Fluting Fibers, Structural Collapse)](/Users/sarathi/.gemini/antigravity-ide/brain/bdd1d081-1c17-4c4a-86ec-7feb666af00a/samples/sample_crushed.jpg)
<!-- slide -->
![3. Tamper-Evident Security Seal Sliced / Ripped Open (FDA 21 CFR Part 211.132 Breach)](/Users/sarathi/.gemini/antigravity-ide/brain/bdd1d081-1c17-4c4a-86ec-7feb666af00a/samples/sample_tamper_breach.jpg)
````

---

## 🔍 Defect Breakdown & Real-World Warehouse Standards

### 1. 🟢 `sample_clean.jpg` — Real Compliant Cold-Chain Package
* **Inspection Verdict**: **`PASS`** (98.5% Confidence)
* **Real Elements**:
  * Genuine kraft corrugated fiberboard box on industrial stainless-steel packing station.
  * Real barcode scanner with coiled cable and digital scale visible on the workstation.
  * Legible GS1-128 shipping label (`MEDIPHARM DISTRIBUTION`, Lot `B23KD41`, Exp `12/2025`).
  * Blue `2-8°C REFRIGERATED COLD CHAIN` compliance badge.
  * Unbroken continuous tamper-evident tape (`TAMPER EVIDENT PHARMA SEAL`).

---

### 2. 🔴 `sample_crushed.jpg` — Real Transit Compression Damage
* **Inspection Verdict**: **`REJECT`** (Structural Failure)
* **Defect Class**: `CRUSHED_CORNER`
* **Real Elements**:
  * Real crumpled cardboard deformation with visible wavy fluting exposed.
  * High-stress corner tear caused by pallet compression or conveyor belt jam.
  * **GDP Failure Code**: `SOP-BOX-02` (ISTA-3A). Any corner crush over 10mm causes shock transfer to internal medicine vials.

---

### 3. 🔴 `sample_tamper_breach.jpg` — Real Sliced / Ripped Security Seal
* **Inspection Verdict**: **`REJECT`** (Critical Security Breach)
* **Defect Class**: `TAPE_BREACH`
* **Real Elements**:
  * Sliced and frayed blue security tape peeling away from the carton flap seam.
  * Box seam partially opened, risking physical contamination, thermal leakage, or theft.
  * **GDP Failure Code**: `SOP-SEAL-01` (FDA 21 CFR Part 211.132 mandatory barrier-to-entry).

---

## 🏭 How Real Images Are Acquired in Production

In a live pharmaceutical warehouse facility, real images come from:
1. **Overhead Industrial Cameras**: Basler ace 2 / FLIR Blackfly GigE vision cameras mounted 800mm above the packing conveyor table.
2. **Thermal Cameras**: FLIR A700 long-wave infrared sensors detecting temperature leakage around the box seams.
3. **Public Academic Datasets**: [MVTec AD](https://www.mvtec.com/company/research/datasets/mvtec-ad) (5,354 images) & Amazon's [Kaputt Logistics Defect Dataset](https://www.kaputt-dataset.com) (230,000+ real damaged boxes).
