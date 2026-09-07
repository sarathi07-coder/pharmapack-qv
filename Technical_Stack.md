# ⚙️ PharmaPack QV — Complete Technical Stack
## Every Single Technology, Model, Library & Tool — Nothing Hidden

> Full list of everything used in the system. Zero vagueness.

---

## 🧠 CATEGORY 1 — LARGE LANGUAGE MODELS (LLM)

| Model | Provider | Version | Purpose in System |
|-------|----------|---------|-------------------|
| **GPT-4o** | OpenAI | gpt-4o-2024-11-20 | Primary cloud verdict synthesis, CAPA report generation, complex reasoning |
| **Gemini 1.5 Pro** | Google | gemini-1.5-pro-002 | Fallback LLM, multi-modal image+text reasoning |
| **Gemini 2.0 Flash** | Google | gemini-2.0-flash | Fast, cost-efficient RAG answer generation |
| **Claude Sonnet** | Anthropic | claude-sonnet-4-5 | Long-document SOP analysis, regulatory report drafting |

**When used**: Cloud connection available → LLM handles complex verdict synthesis, CAPA generation, stakeholder reports, SOP analysis, regulatory compliance queries

---

## 📱 CATEGORY 2 — SMALL LANGUAGE MODELS (SLM) — On-Device / Edge

| Model | Size | Quantisation | Purpose in System |
|-------|------|-------------|-------------------|
| **Microsoft Phi-3 Mini** | 3.8B params | 4-bit GGUF (Q4_K_M) | Primary edge SLM — packing guidance, operator Q&A, simple verdicts |
| **Phi-3.5 Mini Instruct** | 3.8B params | 4-bit GGUF | Updated Phi, better instruction following |
| **Mistral 7B Instruct** | 7B params | 4-bit GGUF (Q4_K_M) | Fallback SLM — richer reasoning offline |
| **Llama 3.2 3B** | 3B params | 4-bit GGUF | Ultra-lightweight, AR glasses deployment |
| **TinyLlama 1.1B** | 1.1B params | 4-bit GGUF | Absolute minimum — very low RAM tablets |

**Served via**: `Ollama` (local model server)  
**Latency**: Phi-3 Mini → < 300ms on 4GB VRAM  
**When used**: Offline / low-latency / AR glasses / voice assistant

---

## 👁️ CATEGORY 3 — COMPUTER VISION MODELS (CNN + Object Detection)

| Model | Framework | Purpose | Speed |
|-------|-----------|---------|-------|
| **YOLOv8n** (nano) | Ultralytics | Real-time defect detection on edge tablet | 80+ FPS |
| **YOLOv8s** (small) | Ultralytics | Server-side defect detection + bounding boxes | 60+ FPS |
| **YOLOv8m** (medium) | Ultralytics | High-accuracy detection (batch validation) | 40+ FPS |
| **MobileNetV2** | PyTorch | Lightweight image classifier for tablet deployment | Edge-optimised |
| **MobileNetV3-Large** | PyTorch | Updated mobile CNN, better accuracy/speed ratio | Edge-optimised |
| **ResNet-50** | PyTorch | High-accuracy server-side classification | Server-only |
| **EfficientNet-B3** | PyTorch | Accuracy-efficiency balanced classification | Hybrid |
| **Grad-CAM** | `pytorch-gradcam` lib | Explainability heatmaps — shows WHERE defect is | Post-inference |

**Training framework**: `Ultralytics` for YOLO, `torchvision` for ResNet/Mobile  
**Inference**: ONNX export → `onnxruntime` for deployment  

---

## 🔬 CATEGORY 4 — SPECIALISED NEURAL NETWORKS

| Network | Architecture | Library | Purpose |
|---------|-------------|---------|---------|
| **Anomaly Autoencoder** | Conv Encoder-Decoder | PyTorch | Unsupervised — detects novel defects not in training set |
| **LSTM (Fatigue Model)** | 2-layer LSTM + Dense | PyTorch | Predicts operator fatigue from shift time + error rate sequence |
| **XGBoost + MLP Ensemble** | Gradient Boosted Trees + MLP | `xgboost` + PyTorch | Pre-pack risk scoring from tabular item attributes |
| **Sentence-BERT** | Transformer (SBERT) | `sentence-transformers` | Text embedding for RAG semantic search |
| **CLIP** | Vision-Language | OpenAI via HuggingFace | Multimodal: matches text descriptions to packing images |

---

## 🔗 CATEGORY 5 — AGENTIC FRAMEWORKS

| Framework | Version | Purpose |
|-----------|---------|---------|
| **LangGraph** | `langgraph>=0.2.0` | Core agentic workflow — stateful verification pipeline with HITL interrupt/resume |
| **LangChain** | `langchain>=0.3.0` | Tool orchestration, RAG chain building, agent memory |
| **LangChain Core** | `langchain-core>=0.3` | Base abstractions (Runnables, ChatModels, Tools) |
| **LangChain OpenAI** | `langchain-openai` | GPT-4o integration |
| **LangChain Google** | `langchain-google-genai` | Gemini integration |
| **LangSmith** | `langsmith` | LangGraph workflow tracing, debugging, monitoring |

### LangGraph Node Map
```
[START]
  ↓
[pre_pack_risk_node]        ← XGBoost risk score
  ↓
[rule_check_node]           ← Python rule engine
  ↓ (HARD FAIL → reject_node)
[cv_inspect_node]           ← YOLOv8 + MobileNetV2
  ↓
[confidence_router_node]    ← Route by CNN score
  ├─ > 0.90  → [auto_verdict_node]
  ├─ 0.65-0.90 → [hitl_gate_node]  ← interrupt()
  └─ < 0.65  → [escalate_node]
[llm_judge_node]            ← GPT-4o / SLM verdict
  ↓
[rag_citation_node]         ← GDP/SOP citation
  ↓
[tradeoff_calc_node]        ← Cost/time/emission
  ↓
[blockchain_log_node]       ← Hyperledger write
  ↓
[audit_log_node]            ← PostgreSQL write
  ↓
[notify_node]               ← WebSocket push
  ↓
[END]
```

---

## 📚 CATEGORY 6 — RAG (RETRIEVAL-AUGMENTED GENERATION) STACK

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Document Loader** | `langchain.document_loaders.PyPDFLoader` | Load GDP/GMP SOP PDF documents |
| **Text Splitter** | `RecursiveCharacterTextSplitter` | Chunk documents (512 tokens, 50 overlap) |
| **Embedding Model** | `text-embedding-3-small` (OpenAI) | Convert chunks to 1536-dim vectors |
| **Fallback Embedding** | `all-MiniLM-L6-v2` (sentence-transformers) | Offline embedding (no API needed) |
| **Vector Store** | `pgvector` PostgreSQL extension | Store + cosine similarity search on embeddings |
| **Retriever** | `VectorStoreRetriever` (LangChain) | Top-K semantic search (K=5) |
| **RAG Chain** | `create_retrieval_chain` (LangChain) | Full RAG pipeline with citation |
| **Citation Enforcer** | Custom node | Forces every RAG answer to cite doc + page |

**Knowledge Base**:
```
Documents loaded into RAG:
  1. EU GDP Guidelines 2013/C 343/01 (PDF)
  2. WHO TRS 1025 — Good Distribution Practices (PDF)
  3. FDA 21 CFR Part 211 — cGMP (PDF)
  4. EU GMP Annex 15 — Qualification and Validation (PDF)
  5. DSCSA Guidance — Drug Supply Chain Security Act (PDF)
  6. Internal Packaging SOPs (uploaded by QA team)
  7. Packaging Material Specifications by product class
```

---

## 🗄️ CATEGORY 7 — DATABASES

| Database | Version | Type | Purpose |
|----------|---------|------|---------|
| **PostgreSQL** | 16.x | Relational | Core data store — sessions, operators, items, verdicts, audit |
| **pgvector** | 0.7.x | Vector extension | RAG embeddings — cosine similarity search |
| **TimescaleDB** | 2.x | Time-series extension | IoT sensor readings (temp, humidity, weight) — hypertable |
| **Redis** | 7.x | In-memory cache | Session state, HITL queue, real-time leaderboard, pub/sub |
| **MinIO** | Latest | Object storage (S3-compatible) | Packing images, model artifacts, exported reports |
| **Elasticsearch** | 8.x | Search + analytics | Audit trail search (21 CFR Part 11), full-text log search |
| **Hyperledger Fabric** | 2.5.x | Permissioned blockchain | Immutable chain-of-custody records, DSCSA compliance |

### Core PostgreSQL Tables
```sql
operators          → Operator records (anonymised, role, zone, workload limit)
items              → Pharmaceutical item catalogue (fragility, temp zone, SKU)
packaging_specs    → Packaging requirements per item (material, padding, seal)
packing_sessions   → Every packing event (image, verdict, scores, HITL result)
damage_outcomes    → Linked damage reports from post-dispatch feedback
operator_workload  → Shift-level fatigue tracking per operator
audit_trail        → Immutable 21 CFR Part 11 audit log
sop_documents      → RAG knowledge base document index
sop_chunks         → pgvector embedding chunks for RAG retrieval
zone_sensor_readings → TimescaleDB hypertable for IoT readings
```

---

## 🖥️ CATEGORY 8 — BACKEND & API

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Primary language for all backend + ML |
| **FastAPI** | 0.115.x | REST API gateway — async, high-performance |
| **Uvicorn** | 0.30.x | ASGI server for FastAPI |
| **Pydantic v2** | 2.x | Request/response validation, data models |
| **SQLAlchemy** | 2.x (async) | ORM for PostgreSQL (async sessions) |
| **Alembic** | 1.x | Database migrations |
| **Celery** | 5.x | Async task queue (model inference, report gen) |
| **Redis** (as broker) | 7.x | Celery message broker |
| **WebSockets** | FastAPI built-in | Real-time HITL notifications to supervisor UI |
| **JWT Auth** | `python-jose` | JSON Web Token authentication |
| **RBAC** | Custom middleware | Role-based access control (10 roles) |
| **OpenAPI 3.1** | Auto-generated | API documentation (Swagger UI at `/docs`) |

---

## 🤖 CATEGORY 9 — ML / AI LIBRARIES

| Library | Version | Purpose |
|---------|---------|---------|
| **PyTorch** | 2.3.x | Primary deep learning framework |
| **Torchvision** | 0.18.x | CNN models (ResNet, MobileNet) + transforms |
| **Ultralytics** | 8.x | YOLOv8 training, inference, export |
| **ONNX** | 1.16.x | Export models for cross-platform inference |
| **ONNXRuntime** | 1.18.x | Fast inference engine (CPU + GPU) |
| **Scikit-learn** | 1.5.x | XGBoost pipeline, metrics, preprocessing |
| **XGBoost** | 2.1.x | Pre-pack risk scoring model |
| **Albumentations** | 1.4.x | Image augmentation pipeline |
| **Anomalib** | 1.x | Anomaly detection framework (autoencoder) |
| **OpenCV** | 4.10.x | Image preprocessing, format conversion |
| **Pillow (PIL)** | 10.x | Image loading and manipulation |
| **NumPy** | 1.26.x | Numerical arrays |
| **Pandas** | 2.2.x | Tabular data processing |
| **Matplotlib** | 3.9.x | Plots, confusion matrix, charts |
| **Seaborn** | 0.13.x | Statistical visualisation |
| **HuggingFace Transformers** | 4.44.x | BERT, CLIP, Sentence-BERT |
| **HuggingFace Datasets** | 2.21.x | Dataset loading and processing |
| **sentence-transformers** | 3.x | Semantic embeddings for RAG |
| **Roboflow** | `roboflow` Python SDK | Dataset download from Roboflow Universe |
| **pytorch-gradcam** | `grad-cam` | Grad-CAM explainability heatmaps |

---

## 🎤 CATEGORY 10 — VOICE ASSISTANT STACK (Edge)

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Whisper.cpp** | Latest | Speech-to-text — runs locally on tablet, no cloud |
| **OpenAI Whisper** | `whisper` Python | Fallback STT (cloud, when internet available) |
| **Coqui TTS** | `TTS` Python | Text-to-speech — offline, natural voice |
| **pyaudio** | 0.2.x | Microphone input capture |
| **Ollama** | Latest | Local model server for SLM (Phi-3, Mistral, Llama) |

---

## 🌐 CATEGORY 11 — FRONTEND & UI

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 14.x (App Router) | Primary web application framework |
| **React** | 18.x | UI component library |
| **TypeScript** | 5.x | Type-safe frontend |
| **Tailwind CSS** | 3.x | Utility-first styling |
| **shadcn/ui** | Latest | Premium UI components (dialogs, cards, badges) |
| **Recharts** | 2.x | Trade-off dashboard charts (area, bar, radar) |
| **React Query (TanStack)** | 5.x | Server state management, auto-refresh |
| **Socket.io Client** | 4.x | Real-time WebSocket (HITL notifications) |
| **Next.js PWA** | `next-pwa` | Progressive Web App for tablet deployment |
| **Framer Motion** | 11.x | Animations (dashboard micro-animations) |
| **Lucide React** | Latest | Icon library |
| **Zustand** | 4.x | Lightweight client state management |
| **React Hook Form** | 7.x | Form validation (QA forms, CAPA) |
| **Zod** | 3.x | Schema validation (shared with backend Pydantic) |

### AR Glasses Interface
| Technology | Purpose |
|-----------|---------|
| **RealWear Navigator 520** | Primary AR smart glasses hardware |
| **Vuzix Blade 2** | Alternative AR hardware |
| **RealWear WearHF** | Voice command framework for AR glasses |
| **Android WebView** | Render PWA on glasses display |

---

## 🏗️ CATEGORY 12 — INFRASTRUCTURE & DEVOPS

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Docker** | 26.x | Containerisation of all services |
| **Docker Compose** | 2.x | Local development orchestration |
| **Kubernetes (K8s)** | 1.31.x | Production container orchestration (future) |
| **Nginx** | 1.26.x | Reverse proxy, SSL termination |
| **GitHub Actions** | - | CI/CD pipeline |
| **LangSmith** | Latest | LangGraph trace monitoring + debugging |
| **Grafana** | 11.x | System metrics dashboard |
| **Prometheus** | 2.x | Metrics collection |
| **Flower (Celery)** | 2.x | Celery task monitoring UI |
| **Sentry** | Latest | Error tracking + alerting |

### Docker Compose Services
```yaml
services:
  api:          FastAPI backend
  worker:       Celery async task worker
  db:           PostgreSQL 16 + pgvector + TimescaleDB
  redis:        Redis 7 (cache + Celery broker)
  minio:        MinIO object storage
  elasticsearch: Elasticsearch 8 (audit logs)
  ollama:       Local SLM server (Phi-3, Mistral)
  langsmith:    LangGraph monitoring
  grafana:      System monitoring dashboard
  prometheus:   Metrics scraper
  web:          Next.js frontend
  nginx:        Reverse proxy
```

---

## 🌿 CATEGORY 13 — FEDERATED LEARNING STACK

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Flower (flwr)** | 1.11.x | Federated learning framework (client + server) |
| **flwr-datasets** | Latest | Partitioning datasets across simulated sites |
| **Differential Privacy** | `opacus` (PyTorch) | Add mathematical privacy guarantees to model updates |
| **Secure Aggregation** | Flower built-in | Cryptographic aggregation of model weights |

### Federated Setup
```
CENTRAL SERVER (HQ)
  └── FedAvg aggregation every 50 local rounds
  
SITE A CLIENT          SITE B CLIENT          SITE C CLIENT
(London warehouse)     (Manchester warehouse) (Edinburgh warehouse)
Local YOLOv8 training  Local YOLOv8 training  Local YOLOv8 training
No data shared         No data shared         No data shared
Only weights shared    Only weights shared    Only weights shared
```

---

## 📡 CATEGORY 14 — IoT & HARDWARE INTEGRATION

| Hardware/Protocol | Purpose |
|------------------|---------|
| **Temperature Sensors (PT100/DS18B20)** | Zone temperature monitoring (2–8°C, -20°C, 15–25°C) |
| **Humidity Sensors (DHT22/SHT31)** | Humidity control in storage zones |
| **Load Cell Weight Sensor** | Auto-weigh packed box → compare vs expected ±tolerance |
| **Barcode Scanner (Honeywell 1900)** | Scan item SKU + DSCSA serial number at packing |
| **QR Code Reader** | Read packaging specification QR code |
| **MQTT Protocol** | IoT sensor data transmission to TimescaleDB |
| **Raspberry Pi 4** | Edge IoT gateway per zone (aggregates sensors → MQTT) |
| **RealWear Navigator 520** | AR smart glasses hardware |
| **Industrial Tablet (IP65 rated)** | Packing station device (ruggedised for warehouse) |

---

## ⛓️ CATEGORY 15 — BLOCKCHAIN STACK

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Hyperledger Fabric** | 2.5.x | Permissioned enterprise blockchain |
| **Fabric SDK (Python)** | `hfc` Python SDK | Write packing session records to chain |
| **Chaincode (Go)** | Go 1.21 | Smart contract for packing audit records |
| **CouchDB** | 3.x | World state database for Fabric |

---

## 🧪 CATEGORY 16 — TESTING & VALIDATION

| Tool | Purpose |
|------|---------|
| **pytest** | Backend unit + integration tests |
| **pytest-asyncio** | Async FastAPI endpoint testing |
| **httpx** | FastAPI test client |
| **Playwright** | End-to-end UI testing |
| **Great Expectations** | Dataset validation (class balance, label quality) |
| **MLflow** | ML experiment tracking (model versions, metrics) |
| **DVC (Data Version Control)** | Dataset versioning + reproducibility |
| **Locust** | API load testing (throughput benchmarks) |

---

## 📦 CATEGORY 17 — KEY PYTHON PACKAGES (Complete List)

```txt
# requirements.txt (core)

# API & Server
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
python-jose[cryptography]
passlib[bcrypt]
sqlalchemy[asyncio]>=2.0.0
alembic
asyncpg
redis[hiredis]
celery[redis]

# AI Orchestration
langchain>=0.3.0
langchain-core>=0.3.0
langchain-openai
langchain-google-genai
langgraph>=0.2.0
langsmith
langchain-community

# LLM / Embeddings
openai>=1.40.0
google-generativeai
anthropic
sentence-transformers>=3.0.0
ollama  # local SLM client

# Computer Vision
torch>=2.3.0
torchvision>=0.18.0
ultralytics>=8.0.0
onnx>=1.16.0
onnxruntime>=1.18.0
opencv-python>=4.10.0
Pillow>=10.0.0
albumentations>=1.4.0
anomalib>=1.0.0
grad-cam

# ML / Data Science
scikit-learn>=1.5.0
xgboost>=2.1.0
numpy>=1.26.0
pandas>=2.2.0
matplotlib>=3.9.0
seaborn>=0.13.0

# Vector Search & RAG
pgvector
pypdf
tiktoken

# HuggingFace
transformers>=4.44.0
datasets>=2.21.0
accelerate

# Federated Learning
flwr>=1.11.0
opacus  # differential privacy

# Voice
openai-whisper
TTS  # Coqui TTS

# Database
psycopg[async]
elasticsearch[async]
minio

# IoT
paho-mqtt  # MQTT client

# Blockchain
# hfc  # Hyperledger Fabric Python SDK

# Testing
pytest
pytest-asyncio
httpx
great-expectations
mlflow
dvc

# Monitoring
prometheus-client
sentry-sdk

# Utilities
python-multipart  # file upload
httpx
aiofiles
python-dotenv
loguru  # structured logging
rich    # CLI formatting
roboflow  # dataset download
```

---

## 📊 FULL TECHNOLOGY COUNT

| Category | Count |
|----------|-------|
| Large Language Models (LLM) | 4 |
| Small Language Models (SLM) | 5 |
| Computer Vision Models (CNN/YOLO) | 8 |
| Specialised Neural Networks | 5 |
| Agentic Frameworks | 6 |
| RAG Stack components | 8 |
| Databases | 7 |
| Backend/API | 11 |
| ML/AI Libraries | 21 |
| Voice Assistant Stack | 5 |
| Frontend/UI | 15 |
| Infrastructure/DevOps | 12 |
| Federated Learning | 4 |
| IoT/Hardware | 9 |
| Blockchain | 4 |
| Testing/Validation | 8 |
| **TOTAL** | **≈ 137 technologies** |

---

*PharmaPack QV — Complete Technical Stack | 2026-09-05*
