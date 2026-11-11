# PharmaPack QV™ — Final Academic Capstone Dossier (IEEE Technical Monograph)

**Course:** Sem 5 — IE28 Project | Rathinam Raale CoE Growth  
**System Version:** `v2.6.0-Capstone-100%` (100% Completion Milestone)  
**Compliance Baseline:** FDA 21 CFR Part 11, 21 CFR §211.132, WHO Annex 5 Good Distribution Practices (GDP), ISTA-3A  
**Repository:** [https://github.com/sarathi07-coder/pharmapack-qv](https://github.com/sarathi07-coder/pharmapack-qv)

---

## Abstract
In pharmaceutical cold-chain warehousing (`-20°C`, `2–8°C`, `15–25°C`), human packing variance under shift pressure leads to omitted refrigerant packs, crushed fluting corners, compromised tamper-evident seals, and unreadable GS1 barcodes—over 90% of which are discovered latently only at receiving hospitals. **PharmaPack QV™** resolves this crisis through a deterministic + agentic two-stage dual-camera vision inspection gate orchestrated by a **LangGraph 6-Node Verification Pipeline**, hardened by a sub-15ms **PyTorch QNNPACK INT8** edge circuit breaker (`0.216 ms` mean latency, `4,630.3 FPS`), enforced by **FDA 21 CFR Part 11 SHA-256 hash-chained audit logs**, and integrated into warehouse operations via **Dual-Channel RTSP/MJPEG video streams**, **Zebra ZPL II GDP-gated printing**, **HMAC-SHA256 ERP/WMS webhooks**, and **operator ergonomic shift guardrails**.

---

## 1. End-to-End Two-Stage System Architecture

```
+--------------------------- WAREHOUSE PACKING FLOOR (RTSP GENLOCK) ---------------------------+
| [CAM-01-OVERHEAD (15fps Stage 1 Open-Box)]    [CAM-02-CONVEYOR (30fps Stage 2 Sealed Box)]   |
+--------------------------------------+-------------------------------------------------------+
                                       | (Multipart MJPEG / Synchronized Dual-Capture API)
                                       v
+------------------------------ HYBRID RESILIENCE VISION TIER ---------------------------------+
| Tier 1: Roboflow Cloud Serverless (Closed State) -> Circuit Breaker -> Tier 2 Offline Edge    |
| Tier 2: OpenCV Spatial Heuristics + PyTorch QNNPACK INT8 PharmaEdgeNet (0.216ms / 4,630 FPS) |
+--------------------------------------+-------------------------------------------------------+
                                       |
                                       v
+-------------------------- LANGGRAPH 6-NODE DETERMINISTIC PIPELINE ---------------------------+
| 1. Ingest/OCR (GS1-128) -> 2. Vision Inference -> 3. Zero-Tolerance WHO/ISTA Rules Engine    |
| 4. Guideline SOP RAG    -> 5. 4-Way Trade-Off Matrix -> 6. Verdict / HITL / SHA-256 Chain    |
+------+-------------------------------+---------------------------------------+---------------+
       | (verdict == "PASS")           | (0.50 <= conf < 0.85)                 | (defect / rule)
       v                               v                                       v
[Zebra ZT411 ZPL II Printer]   [Supervisor HITL Console]               [HTTP 403 ZPL Block +]
[ERP/WMS HMAC-SHA256 Sync]     [21 CFR Part 11 PIN E-Sign]             [CAPA Repack Escalation]
```

---

## 2. Quantified Engineering Benchmarks & Validation

### 2.1 Edge INT8 Quantization vs FP32 vs MPS Accelerator (`data/edge_quantization_benchmark.json`)
Trained `PharmaEdgeNet` (Depthwise-Separable CNN across 300 curated + augmented samples spanning `CLEAN`, `CRUSHED_CORNER`, `TAPE_BREACH`, `LABEL_OBSCURED`, `MISSING_ICE_PACK`) and quantized via PyTorch ARM64 `qnnpack` Static PTQ:

| Execution Mode | Mean Latency (ms) | p95 Latency (ms) | Throughput (FPS) | Validation Acc | Model Size |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FP32 TorchScript (CPU)** | `3.094 ms` | `3.240 ms` | `323.2 FPS` | `100.0%` | `203.27 KB` |
| **Apple MPS Accelerator** | `1.899 ms` | `4.141 ms` | `526.5 FPS` | `100.0%` | `203.27 KB` |
| **INT8 QNNPACK (CPU Edge)** | **`0.216 ms`** | **`0.275 ms`** | **`4,630.3 FPS`** | **`100.0%`** | **`107.90 KB`** (`-46.9%`) |

- **Speedup:** `14.32x` faster than FP32 CPU; meets `<15ms` inline high-speed conveyor SLA with **69x headroom**.
- **Edge Manifest:** NVIDIA Jetson Orin / TensorRT deployment spec exported at `ml/artifacts/tensorrt_engine_spec.json`.

### 2.2 Hybrid Cloud-to-Edge Circuit Breaker Resilience (`data/resilience_benchmark_report.json`)
Measured across 20 sequential inspections per outage tier:
- **0% Cloud Drops (Nominal):** `1,242.34 ms` mean latency (`100%` zero dropped inspections).
- **25% Intermittent Packet Drops:** `131.98 ms` mean (`7.6 FPS`, `100%` continuity).
- **50% Heavy Rate-Limit Congestion:** `399.47 ms` mean (`2.5 FPS`, `100%` continuity).
- **100% Network Blackout (Offline Edge Fallback):** **`4.29 ms`** mean (`5.05 ms` p95, `232.0 FPS`, `119.8 MB` RAM, `100%` continuity).

### 2.3 Empirical Physical Packing Floor Trials (`data/empirical_trial_results.json`)
Across `100` controlled mixed-zone trials (`-20°C`, `2–8°C`, `15–25°C`):
- **Verdict Split:** `31` `PASS` (`31.0%`), `37` `REJECT` (`37.0%`), `32` `ESCALATE_HITL` (`32.0%`).
- **Operator Handling Time:** `4.44 seconds` average (`423.8 units/hr` station capacity vs `85 units/hr` manual ergonomic baseline).

---

## 3. Production Modules & Enterprise Compliance
1. **Multi-Camera RTSP & MJPEG Engine (`edge/camera_capture/rtsp_client.py`):** Thread-safe Stage 1 overhead (`CAM-01-OVERHEAD`) and Stage 2 conveyor (`CAM-02-CONVEYOR`) ingestion with genlock dual-capture `/api/v1/streams/dual-capture-inspect`.
2. **Zebra ZPL II GDP-Gated Printer (`backend/integrations/zebra_printer.py`):** Generates `^XA...^XZ` thermal labels embedding GS1 order/AWB + SHA-256 audit prefix, raising `PermissionError` (`HTTP 403`) whenever `verdict != "PASS"`.
3. **Enterprise ERP/WMS Connector (`backend/integrations/wms_connector.py`):** Bi-directional JSON webhooks for `SAP_EWM`, `MANHATTAN_WMS`, and `ORACLE_SCM` signed via `HMAC-SHA256` with persistent retry ledger (`data/wms_sync_queue.json`) and `/replay-queue`.
4. **Ergonomic Shift Guardrail (`/api/v1/enterprise/ergonomics/status`):** Tracks pace ceiling (`85 parcels/hr`), `110-min` unrotated shift limit, and fatigue risk (`>= 0.70`), flagging `OP-102` (`MANDATORY_BREAK_REQUIRED`).
5. **FDA 21 CFR Part 11 Cryptographic Audit Chain (`/api/v1/audit/verify-chain` & `/export`):** Linked SHA-256 block hashes across inspections, supervisor overrides, ZPL prints, and WMS dispatches with 1-click CSV & JSON compliance export.

