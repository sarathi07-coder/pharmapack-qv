# 🧩 PharmaPack QV — Work Breakdown Structure & Modular Execution Plan
## Granular Step-by-Step Implementation Roadmap

> **Total Project Weight**: 100%  
> **Total Modular Pieces**: 124 Executable Units  
> **Primary Division**: Backend & Core Engine (58%, 72 Pieces) vs Frontend & User Interfaces (42%, 52 Pieces)

---

## 📊 High-Level Macro Split Overview

```
TOTAL PROJECT EFFORT (100% / 124 Pieces)
├── ⚙️ BACKEND & CORE ENGINE: 58% (72 Pieces)
│   ├── [B1] Database, Security & Core Schemas           →  8% (10 Pieces)
│   ├── [B2] Dataset Ingestion & Synthetic Generation   →  7% (9 Pieces)
│   ├── [B3] AI/ML Computer Vision & Edge Pipeline      → 15% (18 Pieces)
│   ├── [B4] LangGraph Orchestration & Decision Engine  → 12% (14 Pieces)
│   ├── [B5] FastAPI REST & Real-time WebSocket APIs     → 10% (13 Pieces)
│   └── [B6] Integrations, Voice & IoT Pipeline          →  6% (8 Pieces)
│
└── 🖥️ FRONTEND & USER EXPERIENCES: 42% (52 Pieces)
    ├── [F1] Design System, Base Shell & Components     →  6% (8 Pieces)
    ├── [F2] Operator Station Touch & Voice UI          → 12% (14 Pieces)
    ├── [F3] Supervisor HITL Exception Hub              → 10% (12 Pieces)
    ├── [F4] QA 21 CFR Part 11 Audit Trail & CAPA       →  7% (9 Pieces)
    └── [F5] Executive Analytics, Trade-Off & ESG       →  7% (9 Pieces)
```

---

## ⚙️ PART 1 — BACKEND & CORE ENGINE BREAKDOWN (58% | 72 Pieces)

### 🔹 Split B1: Database, Security & Core Schemas (8% Weight | 10 Pieces)
*Foundation layer for multi-tenant data persistence, cryptographic auditing, and strict data contracts.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B1.1** | PostgreSQL schema with pgvector extension setup | `backend/db/migrations/001_init.sql` | 0.8% |
| **B1.2** | SQLAlchemy ORM models for Operators, Stations, Dispatches | `backend/models/operator.py`, `dispatch.py` | 0.8% |
| **B1.3** | Inspection & InspectionItem schema with confidence scoring | `backend/models/inspection.py` | 0.8% |
| **B1.4** | 21 CFR Part 11 append-only Audit Log model with SHA-256 chaining | `backend/models/audit.py` | 1.0% |
| **B1.5** | Redis cache manager for active sessions & real-time queues | `backend/db/redis_client.py` | 0.6% |
| **B1.6** | Pydantic v2 validation schemas for packing request payloads | `backend/schemas/inspection_schema.py` | 0.8% |
| **B1.7** | Pydantic schemas for multi-attribute verification & SOP items | `backend/schemas/sop_schema.py` | 0.8% |
| **B1.8** | JWT authentication & Role-Based Access Control (RBAC) security | `backend/core/security.py` | 1.0% |
| **B1.9** | Database connection pooling, session fixtures & health check | `backend/db/session.py`, `backend/core/config.py`| 0.7% |
| **B1.10**| MinIO / S3 bucket provisioning & pre-signed URL generator | `backend/services/storage_service.py` | 0.7% |

---

### 🔹 Split B2: Dataset Ingestion & Synthetic Generation (7% Weight | 9 Pieces)
*Curates ethical, non-identifiable pharmaceutical warehouse dataset with realistic packaging defects.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B2.1** | Synthetic pharma box & label generator with controlled defects | `ml/dataset/synthetic_generator.py` | 1.0% |
| **B2.2** | Blister pack & vial synthetic renderer (crush, void, tilt) | `ml/dataset/blister_vial_generator.py` | 0.9% |
| **B2.3** | Albumentations pipeline (lighting, warehouse blur, tilt noise) | `ml/dataset/augmentations.py` | 0.7% |
| **B2.4** | PII and face scrubber for non-identifiable ethical compliance | `ml/dataset/privacy_scrubber.py` | 0.8% |
| **B2.5** | Roboflow / COCO format parser and train/val/test split balancer | `ml/dataset/dataset_splitter.py` | 0.8% |
| **B2.6** | Multi-attribute label encoder (zone, temp, tamper, dunnage) | `ml/dataset/attribute_encoder.py` | 0.7% |
| **B2.7** | Historical dispatch-outcome correlation dataset builder | `ml/dataset/historical_builder.py` | 0.7% |
| **B2.8** | Dataset validation suite checking class imbalance & leakage | `ml/dataset/dataset_validator.py` | 0.7% |
| **B2.9** | Seed script populating baseline sample images and test runs | `backend/db/seed_data.py` | 0.7% |

---

### 🔹 Split B3: AI/ML Computer Vision & Edge Pipeline (15% Weight | 18 Pieces)
*Core computer vision models, defect segmentation, OCR, thermal analysis, and edge optimization.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B3.1** | YOLOv8s fine-tuning script for 12 pharmaceutical packaging defects | `ml/models/yolo_defect/train.py` | 1.1% |
| **B3.2** | YOLOv8 inference engine with bounding box & confidence extraction | `ml/models/yolo_defect/inference.py` | 1.0% |
| **B3.3** | ResNet-50 defect classification head with feature embeddings | `ml/models/resnet_classifier/model.py` | 0.9% |
| **B3.4** | ConvNeXt secondary validator for subtle micro-tears & seal cracks | `ml/models/convnext_verifier/model.py` | 0.9% |
| **B3.5** | Fast-SCNN void ratio & dunnage volume segmentation | `ml/models/segmentation/fast_scnn.py` | 0.9% |
| **B3.6** | Depth/RGB-D box fill calculator (ultrasonic/stereo camera input) | `ml/models/depth/fill_level_estimator.py` | 0.8% |
| **B3.7** | PaddleOCR pipeline for GS1 barcode, batch number & expiry date | `ml/models/ocr/paddle_ocr_engine.py` | 1.0% |
| **B3.8** | Pyzbar 2D DataMatrix & QR code hardware-accelerated reader | `ml/models/ocr/datamatrix_decoder.py` | 0.7% |
| **B3.9** | Thermal FLIR camera parser for cold chain heat-leak detection | `ml/models/thermal/heat_leak_detector.py` | 0.8% |
| **B3.10**| PatchCore anomaly detection model for unseen / novel defects | `ml/models/anomaly/patchcore_engine.py` | 0.9% |
| **B3.11**| ONNX Runtime export pipeline for all PyTorch vision models | `ml/export/onnx_converter.py` | 0.8% |
| **B3.12**| TensorRT FP16 quantization script for Jetson Orin / GPU edge | `ml/export/tensorrt_optimizer.py` | 0.8% |
| **B3.13**| OpenVINO INT8 quantization script for Intel warehouse mini-PCs | `ml/export/openvino_optimizer.py` | 0.8% |
| **B3.14**| Grad-CAM & Integrated Gradients visual explainability generator | `ml/explainability/gradcam.py` | 0.8% |
| **B3.15**| Model ensemble combiner (YOLO + ResNet + PatchCore voting) | `ml/models/ensemble_scorer.py` | 0.8% |
| **B3.16**| Edge camera frame grabber with RTSP/WebRTC streamer | `edge/camera_capture/rtsp_client.py` | 0.7% |
| **B3.17**| Local edge inference daemon with sub-150ms latency target | `edge/inference_daemon/main.py` | 0.7% |
| **B3.18**| Edge-to-Cloud sync manager for offline buffering & replay | `edge/sync/offline_buffer.py` | 0.6% |

---

### 🔹 Split B4: LangGraph Orchestration & Decision Engine (12% Weight | 14 Pieces)
*Stateful AI agent pipeline combining multi-modal LLM reasoning, deterministic rule checks, and trade-off math.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B4.1** | LangGraph State definition (`InspectionGraphState` TypedDict) | `backend/pipeline/state.py` | 0.8% |
| **B4.2** | Deterministic packaging rules engine (temperature, zone, weight) | `backend/rules/pharma_rules_engine.py`| 1.0% |
| **B4.3** | Node 1: Vision Aggregator & OCR validation node | `backend/pipeline/nodes/vision_node.py` | 0.9% |
| **B4.4** | Node 2: Deterministic Rule Verifier node | `backend/pipeline/nodes/rule_node.py` | 0.9% |
| **B4.5** | ChromaDB / pgvector SOP embedding vector store & retriever | `backend/ai/rag/sop_retriever.py` | 0.9% |
| **B4.6** | Node 3: RAG SOP Context Injector node | `backend/pipeline/nodes/rag_node.py` | 0.9% |
| **B4.7** | Multimodal LLM (GPT-4o / Gemini 1.5 Pro) reasoning prompt chain | `backend/ai/llm/multimodal_chain.py` | 1.0% |
| **B4.8** | Local SLM (Phi-3 Mini / Llama 3.2 3B) offline fallback chain | `backend/ai/slm/local_slm_chain.py` | 0.9% |
| **B4.9** | Node 4: LLM/SLM Root Cause & Compliance Assessor node | `backend/pipeline/nodes/reasoning_node.py`| 0.9% |
| **B4.10**| Node 5: Trade-off Optimizer (Cost vs Time vs CO2 vs Reliability)| `backend/services/tradeoff_calculator.py`| 1.0% |
| **B4.11**| Node 6: HITL Threshold Router (Pass / Auto-Reject / Escalate) | `backend/pipeline/nodes/router_node.py` | 0.9% |
| **B4.12**| Automated CAPA (Corrective and Preventive Action) generator | `backend/services/capa_generator.py` | 0.8% |
| **B4.13**| LangSmith observability callback hooks & latency metrics | `backend/pipeline/observability.py` | 0.6% |
| **B4.14**| LangGraph compiled workflow assembly & execution wrapper | `backend/pipeline/graph_builder.py` | 0.7% |

---

### 🔹 Split B5: FastAPI REST & Real-Time WebSocket APIs (10% Weight | 13 Pieces)
*High-throughput async backend server exposing operational endpoints and live streaming channels.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B5.1** | FastAPI app initialization, middleware, CORS & error handlers | `backend/main.py` | 0.7% |
| **B5.2** | Operator Auth & Session endpoints (`/api/v1/auth/*`) | `backend/api/v1/endpoints/auth.py` | 0.7% |
| **B5.3** | Live Inspection Submission API (`POST /api/v1/inspections/submit`)| `backend/api/v1/endpoints/inspections.py`| 1.0% |
| **B5.4** | Real-time WebSocket for Operator Station instant feedback | `backend/api/v1/websockets/operator_ws.py`| 0.9% |
| **B5.5** | Supervisor Exception Queue API (`GET /api/v1/supervisor/queue`) | `backend/api/v1/endpoints/supervisor.py` | 0.8% |
| **B5.6** | Supervisor HITL Decision API (`POST /api/v1/supervisor/decide`) | `backend/api/v1/endpoints/supervisor.py` | 0.8% |
| **B5.7** | WebSocket stream for Supervisor live inspection feed | `backend/api/v1/websockets/supervisor_ws.py`| 0.8% |
| **B5.8** | 21 CFR Part 11 Audit Trail Query & Export API (`/api/v1/audit/*`)| `backend/api/v1/endpoints/audit.py` | 0.8% |
| **B5.9** | Executive Analytics & Metrics API (`/api/v1/analytics/*`) | `backend/api/v1/endpoints/analytics.py` | 0.8% |
| **B5.10**| Operator Performance & Training Needs API (`/api/v1/operators/*`)| `backend/api/v1/endpoints/operators.py` | 0.7% |
| **B5.11**| Celery background tasks for async report generation & ML sync | `backend/tasks/async_tasks.py` | 0.7% |
| **B5.12**| Automated Swagger/OpenAPI documentation with response schemas | `backend/core/openapi.py` | 0.6% |
| **B5.13**| Comprehensive API integration test suite with Pytest | `backend/tests/test_api_integration.py` | 0.7% |

---

### 🔹 Split B6: Integrations, Voice & IoT Pipeline (6% Weight | 8 Pieces)
*Connects industrial peripherals, WMS enterprise systems, voice assistant, and cold-chain sensors.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **B6.1** | MQTT broker listener for conveyor sensors & thermal probes | `backend/integrations/mqtt_client.py` | 0.8% |
| **B6.2** | SAP / Manhattan WMS mock bi-directional dispatch connector | `backend/integrations/wms_connector.py` | 0.8% |
| **B6.3** | Zebra / ZPL thermal dispatch label printer protocol generator | `backend/integrations/zebra_printer.py` | 0.7% |
| **B6.4** | Whisper.cpp local voice transcription service for hands-free ops | `backend/services/voice/stt_service.py` | 0.8% |
| **B6.5** | Coqui TTS voice feedback generator for audio packing prompts | `backend/services/voice/tts_service.py` | 0.7% |
| **B6.6** | IoT scale & digital caliper serial/USB protocol reader | `backend/integrations/scale_reader.py` | 0.7% |
| **B6.7** | Cold storage zone IoT gateway logger (2-8°C, 15-25°C, -20°C) | `backend/integrations/cold_zone_monitor.py`| 0.8% |
| **B6.8** | Webhook notification dispatcher (Slack/Teams/Email alerts) | `backend/services/notifier.py` | 0.7% |

---

## 🖥️ PART 2 — FRONTEND & USER EXPERIENCES BREAKDOWN (42% | 52 Pieces)

### 🔹 Split F1: Design System, Base Shell & Components (6% Weight | 8 Pieces)
*Builds modern, responsive, high-contrast industrial UI system with dark/light themes and shared tokens.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **F1.1** | Global CSS token system (colors, typography, glassmorphism) | `frontend/src/index.css`, `variables.css`| 0.8% |
| **F1.2** | Role-based navigation shell & top bar with warehouse status | `frontend/src/components/layout/Shell.jsx`| 0.8% |
| **F1.3** | High-contrast industrial badge, alert and status pill components| `frontend/src/components/common/Badge.jsx`| 0.7% |
| **F1.4** | Bounding box & Grad-CAM visual overlay canvas component | `frontend/src/components/common/VisualOverlay.jsx`| 0.9% |
| **F1.5** | WebSocket real-time connection hook with auto-reconnect | `frontend/src/hooks/useWebSocket.js` | 0.8% |
| **F1.6** | Global state management (Zustand store for auth & inspections) | `frontend/src/store/appStore.js` | 0.8% |
| **F1.7** | Accessible modal, drawer, and confirmation dialog components | `frontend/src/components/common/Modal.jsx`| 0.6% |
| **F1.8** | Keyboard shortcut controller (Space to scan, 1-4 for quick tags)| `frontend/src/hooks/useShortcuts.js` | 0.6% |

---

### 🔹 Split F2: Operator Station Touch & Voice UI (12% Weight | 14 Pieces)
*Ultra-fast, touch-first interface for warehouse packers with live camera feed, voice prompts, and instant verdicts.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **F2.1** | Live camera viewfinder with target crosshair & scan bounding box| `frontend/src/views/operator/CameraFeed.jsx`| 0.9% |
| **F2.2** | Barcode / DataMatrix instant scanner overlay | `frontend/src/views/operator/ScannerBox.jsx`| 0.8% |
| **F2.3** | Package attribute selector (Zone: 2-8°C vs 15-25°C, Shipper Box)| `frontend/src/views/operator/ZoneSelector.jsx`| 0.8% |
| **F2.4** | Dynamic SOP Packing Checklist with live compliance indicators | `frontend/src/views/operator/SopChecklist.jsx`| 1.0% |
| **F2.5** | Full-screen Instant Verdict Card (GREEN Pass / RED Reject / AMBER)| `frontend/src/views/operator/VerdictCard.jsx`| 1.0% |
| **F2.6** | Real-time Defect Heatmap toggle (Grad-CAM visual inspection) | `frontend/src/views/operator/HeatmapToggle.jsx`| 0.9% |
| **F2.7** | Step-by-Step Interactive Correction Guide (e.g. "Add 2 ice packs")| `frontend/src/views/operator/GuidanceSteps.jsx`| 0.9% |
| **F2.8** | Voice Assistant mic button & speech waveform visualizer | `frontend/src/views/operator/VoiceAssistant.jsx`| 0.9% |
| **F2.9** | Voice TTS audio player trigger for hands-free audio announcements| `frontend/src/views/operator/AudioFeedback.jsx`| 0.8% |
| **F2.10**| Operator Shift Stats widget (Boxes packed, pass rate, speed) | `frontend/src/views/operator/ShiftStats.jsx` | 0.8% |
| **F2.11**| Offline status banner & queued package sync indicator | `frontend/src/views/operator/OfflineBanner.jsx`| 0.7% |
| **F2.12**| Print Shipping Label button (triggers Zebra ZPL print on Pass)| `frontend/src/views/operator/PrintAction.jsx`| 0.8% |
| **F2.13**| Dispatch Escalation Modal with photo attachment for supervisor | `frontend/src/views/operator/EscalateModal.jsx`| 0.9% |
| **F2.14**| Touch screen responsive optimization (large 48px+ touch targets)| `frontend/src/views/operator/TouchLayout.css`| 0.8% |

---

### 🔹 Split F3: Supervisor HITL Exception Hub (10% Weight | 12 Pieces)
*High-density command center for warehouse supervisors to review ambiguous packages and override decisions.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **F3.1** | Live Priority Escalation Queue sorted by severity and urgency | `frontend/src/views/supervisor/QueueList.jsx` | 1.0% |
| **F3.2** | Multi-Angle Image Inspection Viewer with zoom & pan controls | `frontend/src/views/supervisor/ImageViewer.jsx`| 0.9% |
| **F3.3** | Side-by-side AI Defect Detection vs Golden Standard SOP image | `frontend/src/views/supervisor/CompareView.jsx`| 0.9% |
| **F3.4** | Multi-attribute confidence score breakdown gauge | `frontend/src/views/supervisor/ScoreGauges.jsx`| 0.8% |
| **F3.5** | AI Root Cause Explanation card with cited SOP paragraph | `frontend/src/views/supervisor/ReasoningBox.jsx`| 0.9% |
| **F3.6** | One-Click Action Center: Approve Override / Reject & Repack | `frontend/src/views/supervisor/ActionCenter.jsx`| 0.9% |
| **F3.7** | Electronic Signature dialog for 21 CFR Part 11 Supervisor Sign-off| `frontend/src/views/supervisor/ESignModal.jsx`| 0.9% |
| **F3.8** | Mandatory Root Cause Reason & Corrective Tagging selector | `frontend/src/views/supervisor/TagSelector.jsx`| 0.8% |
| **F3.9** | Operator Coaching Note dispatcher (sends guidance to packer screen)| `frontend/src/views/supervisor/CoachNote.jsx` | 0.8% |
| **F3.10**| Active Packing Stations Live Heatmap & Operator Load Status | `frontend/src/views/supervisor/StationGrid.jsx`| 0.8% |
| **F3.11**| Audio chime & browser push notifications for urgent escalations| `frontend/src/views/supervisor/Notification.jsx`| 0.6% |
| **F3.12**| Inspection history search and filter panel | `frontend/src/views/supervisor/FilterPanel.jsx` | 0.7% |

---

### 🔹 Split F4: QA 21 CFR Part 11 Audit Trail & CAPA (7% Weight | 9 Pieces)
*Regulatory compliance console for Quality Assurance teams, auditors, FDA/EU GMP inspection readiness.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **F4.1** | Immutable Audit Trail Table with SHA-256 block hash verification| `frontend/src/views/qa/AuditTrailTable.jsx` | 0.9% |
| **F4.2** | Cryptographic integrity verification badge (Valid vs Tampered)| `frontend/src/views/qa/ChainValidator.jsx` | 0.8% |
| **F4.3** | Deep Inspection Forensic Viewer (Raw image, model output, e-sign)| `frontend/src/views/qa/ForensicViewer.jsx` | 0.9% |
| **F4.4** | CAPA Incident Management Dashboard (Open, Under Review, Closed)| `frontend/src/views/qa/CapaDashboard.jsx` | 0.8% |
| **F4.5** | Automated CAPA Report Viewer with AI 5-Why root cause analysis| `frontend/src/views/qa/CapaReportView.jsx` | 0.8% |
| **F4.6** | FDA 21 CFR Part 11 compliant PDF Certificate generator | `frontend/src/views/qa/PdfExport.jsx` | 0.8% |
| **F4.7** | Systematic Operator Variation Analyzer (defect rate by shift) | `frontend/src/views/qa/OperatorVariance.jsx`| 0.7% |
| **F4.8** | Cold Chain Excursion Log (temperature integrity verification) | `frontend/src/views/qa/ColdChainLog.jsx` | 0.7% |
| **F4.9** | Regulatory Audit Export button (CSV, JSON, Cryptographic bundle)| `frontend/src/views/qa/AuditExporter.jsx` | 0.6% |

---

### 🔹 Split F5: Executive Analytics, Trade-Off & ESG (7% Weight | 9 Pieces)
*C-suite and Operations Director dashboard showing business impact, ROI trade-off matrix, and carbon metrics.*

| Piece ID | Sub-Task / Deliverable | Files / Artifacts | Percentage |
|---|---|---|---|
| **F5.1** | Four-Way Trade-Off Matrix chart (Cost vs Time vs CO2 vs Reliability)| `frontend/src/views/analytics/TradeoffChart.jsx`| 0.9% |
| **F5.2** | ROI & Savings Calculator (Damages prevented vs Cost of system)| `frontend/src/views/analytics/RoiCalculator.jsx`| 0.8% |
| **F5.3** | Packing Defect Distribution Sunburst & Pareto chart (Chart.js)| `frontend/src/views/analytics/DefectPareto.jsx`| 0.8% |
| **F5.4** | Operator Consistency & Skill Distribution Matrix | `frontend/src/views/analytics/SkillMatrix.jsx` | 0.8% |
| **F5.5** | ESG Packaging Carbon Footprint & Dross Reduction tracker | `frontend/src/views/analytics/EsgTracker.jsx` | 0.8% |
| **F5.6** | False Positive vs False Negative trade-off curve slider | `frontend/src/views/analytics/ThresholdSlider.jsx`| 0.8% |
| **F5.7** | Warehouse Controlled Zone Performance Comparison widget | `frontend/src/views/analytics/ZoneComparison.jsx`| 0.7% |
| **F5.8** | Predictive Damage Risk Forecast (Next 30 Days projection) | `frontend/src/views/analytics/RiskForecast.jsx` | 0.6% |
| **F5.9** | Executive PDF Executive Summary report generator | `frontend/src/views/analytics/ExecReport.jsx` | 0.6% |

---

## 📈 Summary Split Table by Domain & Weight

| Split Code | Domain Name | Category | Pieces | Weight (%) | Cumulative % |
|---|---|---|:---:|:---:|:---:|
| **B1** | Database, Security & Core Schemas | **Backend** | 10 | 8.0% | 8.0% |
| **B2** | Dataset Ingestion & Synthetic Generation | **Backend** | 9 | 7.0% | 15.0% |
| **B3** | AI/ML Computer Vision & Edge Pipeline | **Backend** | 18 | 15.0% | 30.0% |
| **B4** | LangGraph Orchestration & Decision Engine | **Backend** | 14 | 12.0% | 42.0% |
| **B5** | FastAPI REST & Real-Time WebSocket APIs | **Backend** | 13 | 10.0% | 52.0% |
| **B6** | Integrations, Voice & IoT Pipeline | **Backend** | 8 | 6.0% | **58.0%** |
| *SUBTOTAL* | *All Backend Engineering* | *Backend* | *72* | *58.0%* | *58.0%* |
| **F1** | Design System, Base Shell & Components | **Frontend** | 8 | 6.0% | 64.0% |
| **F2** | Operator Station Touch & Voice UI | **Frontend** | 14 | 12.0% | 76.0% |
| **F3** | Supervisor HITL Exception Hub | **Frontend** | 12 | 10.0% | 86.0% |
| **F4** | QA 21 CFR Part 11 Audit Trail & CAPA | **Frontend** | 9 | 7.0% | 93.0% |
| **F5** | Executive Analytics, Trade-Off & ESG | **Frontend** | 9 | 7.0% | **100.0%** |
| *SUBTOTAL* | *All Frontend Engineering* | *Frontend* | *52* | *42.0%* | *100.0%* |
| **TOTAL** | **PharmaPack QV End-to-End System** | **Full Project** | **124** | **100.0%** | **100.0%** |

---

## 🚀 Execution Order & Milestone Sequence

We will proceed in 6 agile build phases so every component is tested in working order:

1. **Milestone 1 (Pieces 1 to 19 | 15% Total)**:
   - Complete Split B1 (Database, Schemas & Security) + Split B2 (Synthetic Dataset & Seed Data).
   - *Deliverable*: Running database, Pydantic schemas, and working 1,000+ image test dataset.
2. **Milestone 2 (Pieces 20 to 37 | 15% Total)**:
   - Complete Split B3 (YOLOv8 + ResNet + OCR + Anomaly + Grad-CAM).
   - *Deliverable*: Trained vision models outputting bounding boxes, OCR text, and heatmaps.
3. **Milestone 3 (Pieces 38 to 64 | 22% Total)**:
   - Complete Split B4 (LangGraph & Rules Engine) + Split B5 (FastAPI REST & WebSockets).
   - *Deliverable*: Working AI inspection API returning verdicts, trade-off scores, and live WebSocket streaming.
4. **Milestone 4 (Pieces 65 to 86 | 18% Total)**:
   - Complete Split F1 (Design System) + Split F2 (Operator Station Touch/Voice UI).
   - *Deliverable*: Live operator screen with real-time camera feed, instant Pass/Reject cards, and voice prompts.
5. **Milestone 5 (Pieces 87 to 107 | 17% Total)**:
   - Complete Split F3 (Supervisor HITL Hub) + Split F4 (QA Audit Trail & 21 CFR Part 11).
   - *Deliverable*: Supervisor override queue with electronic signatures and tamper-proof SHA-256 audit logs.
6. **Milestone 6 (Pieces 108 to 124 | 13% Total)**:
   - Complete Split B6 (Hardware/IoT/Voice) + Split F5 (Executive Trade-off & ESG Dashboard).
   - *Deliverable*: Full enterprise end-to-end integration, 4-way trade-off matrix, and automated PDF reports.
