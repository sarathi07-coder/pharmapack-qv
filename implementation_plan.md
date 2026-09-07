# 🏗️ PharmaPack QV — Backend Build Implementation Plan (0% to 45%)

This plan details the implementation steps to scaffold the entire project folder structure and build the **Backend & AI Core Engine** from 0% to 45% completion, covering **Splits B1, B2, B3, B4, and core B5** as outlined in [Work_Breakdown_Structure.md](file:///Users/sarathi/Documents/Ps%20project/Work_Breakdown_Structure.md).

---

## 🎯 Target Scope (45% Milestone)

| Split ID | Module | WBS Pieces | Weight | Cumulative |
|---|---|:---:|:---:|:---:|
| **DIR** | Full Project Directory Scaffolding & Config | All | N/A | Framework |
| **B1** | Database, Security & Core Schemas | B1.1 – B1.10 | 8.0% | 8.0% |
| **B2** | Dataset Ingestion & Synthetic Generation | B2.1 – B2.9 | 7.0% | 15.0% |
| **B3** | AI/ML Computer Vision & Edge Pipeline | B3.1 – B3.18 | 15.0% | 30.0% |
| **B4** | LangGraph Orchestration & Decision Engine | B4.1 – B4.14 | 12.0% | 42.0% |
| **B5 (Core)**| FastAPI App, Middleware, Auth & Live Inspection API | B5.1 – B5.4 | 3.0% | **45.0%** |

---

## 🛠️ Proposed Changes & File Additions

### 📁 Project Root & Configuration
Initialize clean modular repository structure and environment definitions.

#### [NEW] `backend/requirements.txt`
Dependencies: FastAPI, Uvicorn, SQLAlchemy, Alembic, Pydantic v2, PyJWT, LangGraph, LangChain, OpenCV, Pillow, PyTorch/Torchvision, Ultralytics (YOLOv8), NumPy, SciPy, Pyzbar, ChromaDB, etc.

#### [NEW] `backend/core/config.py`
Pydantic Settings for database URLs, JWT secret keys, storage paths, model paths, and controlled zone thresholds (2-8°C, 15-25°C, -20°C).

#### [NEW] `docker-compose.yml`
Local orchestration for PostgreSQL (with pgvector), Redis, MinIO (S3-compatible image store), and backend dev container.

---

### 🗄️ Split B1: Database, Security & Core Schemas (8.0%)
*Deliverable*: SQLite/PostgreSQL dual-compatible schema, SQLAlchemy ORM models, 21 CFR Part 11 SHA-256 audit log, and Pydantic v2 validation contracts.

#### [NEW] `backend/models/base.py`
Declarative base with UUID primary keys and timestamp mixins.

#### [NEW] `backend/models/operator.py`
Operator entity (ID, badge, name, shift, role, certification expiry, fatigue metrics).

#### [NEW] `backend/models/dispatch.py`
Warehouse shipment package entity (AWB, order ID, storage zone, cold chain flag, customer, SLA).

#### [NEW] `backend/models/inspection.py`
Inspection session record (verdict: PASS/FAIL/FLAGGED, confidence, operator_id, station_id, timestamps, image paths, sensor readings).

#### [NEW] `backend/models/audit.py`
**21 CFR Part 11 compliant tamper-proof audit trail** with chained SHA-256 hashes (`previous_hash` + `current_hash`), electronic signature metadata, and UTC timestamps.

#### [NEW] `backend/db/session.py`
Async / sync database engine, connection pooling, and scoped session manager.

#### [NEW] `backend/core/security.py`
Password hashing (bcrypt/argon2), JWT token encoder/decoder, role-based permissions (Operator, Supervisor, QA Auditor, Admin).

#### [NEW] `backend/schemas/inspection_schema.py`
Pydantic v2 schemas: `InspectionCreate`, `InspectionResponse`, `DefectItem`, `BoundingBox`, `TradeOffScore`.

#### [NEW] `backend/schemas/sop_schema.py`
Pydantic schemas for Packaging SOP rules, controlled zone criteria, and packaging checklists.

---

### 🧪 Split B2: Dataset Ingestion & Synthetic Generation (7.0%)
*Deliverable*: Python generator creating non-identifiable pharmaceutical package images with realistic defects (crushed box, missing label, seal puncture, missing ice pack, tilted vial).

#### [NEW] `ml/dataset/synthetic_generator.py`
Procedural Pillow/OpenCV image generator creating realistic pharma secondary packaging boxes with GS1-128 barcodes, temperature warning icons, and simulated defects.

#### [NEW] `ml/dataset/blister_vial_generator.py`
Renderer for primary packaging: crushed blister foil pockets, broken tamper-evident seals, and missing ampoules.

#### [NEW] `ml/dataset/privacy_scrubber.py`
PII scrubber stripping facial data, operator reflection, and external courier markings to guarantee ethical compliance.

#### [NEW] `ml/dataset/dataset_splitter.py`
Generates train/val/test splits in standard format with JSON metadata.

#### [NEW] `backend/db/seed_data.py`
Populates initial mock database with 5 operators, 3 packing stations, 10 SOP definitions, and pre-packaged test inspection runs.

---

### 👁️ Split B3: AI/ML Computer Vision & Edge Pipeline (15.0%)
*Deliverable*: Modular vision pipeline performing defect detection, OCR extraction, anomaly scoring, and Grad-CAM visual heatmaps.

#### [NEW] `ml/models/defect_detector.py`
YOLOv8 defect detector wrapper with simulated/pre-trained weights handling 12 pharma packaging defect classes (Crushed Corner, Punctured Seal, Missing Dunnage, etc.).

#### [NEW] `ml/models/ocr_engine.py`
PaddleOCR / pyzbar extraction wrapper extracting GS1-128 batch number, manufacture/expiry dates, and storage temperature requirements.

#### [NEW] `ml/models/fill_level_estimator.py`
RGB-D / Fast-SCNN void volume estimator calculating percentage of empty space and dunnage padding compliance.

#### [NEW] `ml/models/anomaly_detector.py`
Autoencoder / PatchCore model calculating visual anomaly reconstruction error for novel/unseen damage.

#### [NEW] `ml/explainability/gradcam.py`
Grad-CAM overlay generator producing visual heatmaps highlighting defect regions for operator screen.

#### [NEW] `ml/models/vision_service.py`
Unified vision service executing full multi-model inference pipeline in a single async call.

---

### 🧠 Split B4: LangGraph Orchestration & Decision Engine (12.0%)
*Deliverable*: Multi-step stateful decision graph integrating deterministic pharmaceutical SOP rules, multi-attribute verification, trade-off optimization, and HITL escalation.

#### [NEW] `backend/pipeline/state.py`
`InspectionGraphState` TypedDict carrying inspection ID, image metadata, OCR results, detected defects, rule violations, trade-off scores, and final verdict.

#### [NEW] `backend/rules/pharma_rules_engine.py`
Deterministic rules engine validating cold chain temperature rules (2-8°C vs 15-25°C), maximum weight thresholds, mandatory tamper tape, and minimum dunnage ratio.

#### [NEW] `backend/services/tradeoff_calculator.py`
Multi-objective mathematical trade-off optimizer calculating:
- **Cost**: Packaging materials + rework cost
- **Time**: Packing & verification latency (seconds)
- **Emissions (CO2)**: Material carbon footprint (kg CO2e)
- **Reliability**: Defect escape probability (%)

#### [NEW] `backend/ai/rag/sop_retriever.py`
In-memory vector store matching packaging attributes to standard operating procedure (SOP) clauses.

#### [NEW] `backend/pipeline/nodes.py`
LangGraph graph nodes:
1. `vision_node`: Runs vision service & OCR
2. `rule_node`: Runs deterministic SOP checks
3. `rag_node`: Injects relevant SOP standards
4. `tradeoff_node`: Computes 4-way trade-off matrix
5. `verdict_node`: Computes final status (PASS / REJECT / ESCALATE_HITL)
6. `capa_node`: Generates automated corrective action advice

#### [NEW] `backend/pipeline/graph_builder.py`
Assembles and compiles the LangGraph StateGraph with conditional edges routing low-confidence or conflicting states to HITL queue.

---

### ⚡ Split B5 (Core): FastAPI REST & Real-Time WebSocket APIs (3.0% -> Total 45%)
*Deliverable*: Executable FastAPI server exposing health checks, authentication, and the primary inspection submission endpoint.

#### [NEW] `backend/main.py`
FastAPI application entrypoint with lifespan event handler, CORS middleware, router mounting, and static asset mount.

#### [NEW] `backend/api/v1/endpoints/auth.py`
`/api/v1/auth/login` and `/api/v1/auth/me` endpoints for operator and supervisor authentication.

#### [NEW] `backend/api/v1/endpoints/inspections.py`
`POST /api/v1/inspections/submit` endpoint that receives an image + metadata, invokes the LangGraph pipeline, commits the 21 CFR Part 11 audit log, and returns the full verdict + trade-off breakdown.

#### [NEW] `backend/tests/test_pipeline_e2e.py`
Automated end-to-end integration test verifying that submitting a sample image returns a verified verdict, rule checks, trade-off scores, and audit record.

---

## 🧪 Verification Plan

### Automated Tests
1. **Unit & Schema Tests**:
   - `pytest backend/tests/test_schemas.py` — Verifies Pydantic v2 schemas and validation constraints.
   - `pytest backend/tests/test_audit_trail.py` — Tests SHA-256 cryptographic chain integrity and detects simulated tampering.
   - `pytest backend/tests/test_rules_engine.py` — Tests deterministic cold storage zone packaging rules (2-8°C vs ambient).
2. **LangGraph Pipeline Test**:
   - `pytest backend/tests/test_pipeline_e2e.py` — Tests full LangGraph state transition from image input to trade-off score & verdict output.
3. **FastAPI Endpoint Smoke Test**:
   - Launch FastAPI with Uvicorn on test port (`8000`), execute `POST /api/v1/inspections/submit` with mock packaging image, and assert HTTP 200 with structured JSON response containing:
     - `verdict` (PASS / REJECT / ESCALATE)
     - `confidence_score`
     - `defects_detected`
     - `tradeoff_matrix` (cost, time, emissions, reliability)
     - `audit_hash` (SHA-256)

### Manual Verification
- Execute `python backend/db/seed_data.py` to confirm database seeds cleanly with realistic test records.
- Run `curl -X POST http://127.0.0.1:8000/api/v1/inspections/submit` to verify real-time processing under 500ms.
