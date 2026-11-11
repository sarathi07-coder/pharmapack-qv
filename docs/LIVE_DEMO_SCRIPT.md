# PharmaPack QV™ — Live Capstone Jury Demo Script (5-Minute Walkthrough)

**Pre-Launch Terminal Command:**
```bash
cd "/Users/sarathi/Documents/Ps project"
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open browser: `http://127.0.0.1:8000`

---

### Act 1: Ergonomic Guardrail & Live Dual-Camera RTSP Inspection (90 sec)
1. Point out the top navigation header:
   - Cold-chain storage status badge (`ZONE B: 4.2°C`).
   - Live **Shift Guardrail Pill** (`SHIFT GUARD: 1 Fatigue Alert`) automatically flagging `OP-102` from `/api/v1/enterprise/ergonomics/status`.
2. In **Operator Station**, click **📡 RTSP Live Cam** in the top-right corner of Station 01 Live View to stream real multipart MJPEG frames directly from `CAM-02-CONVEYOR` (`/api/v1/streams/CAM-02-CONVEYOR/mjpeg`).
3. Select **Clean Compliant** (`PH-ORD-9021`, `2-8°C`) and click **⚡ RUN AI VERIFICATION**:
   - Executes synchronized dual-cam capture (`POST /api/v1/streams/dual-capture-inspect`), runs LangGraph 6-node verification + INT8 Edge neural telemetry, logs an immutable SHA-256 block, and announces `"Package verified compliant"`.
4. Click **🖨️ PRINT ZEBRA DISPATCH LABEL** -> backend verifies `PASS`, logs `ZPL_LABEL_PRINTED`, and opens the live **Zebra ZT411 ZPL II Modal** (`^XA ... ^XZ`).

### Act 2: Zero-Tolerance Safety Interlock & HTTP 403 ZPL Lockout (60 sec)
1. Click **Crushed Corner** (`PH-ORD-9022`) or **Missing Ice Pack** (`PH-ORD-9024`).
2. Click **⚡ RUN AI VERIFICATION** -> Verdict flips immediately to **REJECT / ESCALATE** with XAI redGrad-CAM bounding heatmap and **SOP-BOX-02 / SOP-COLD-02** violation flagged.
3. Click **🖨️ PRINT ZEBRA DISPATCH LABEL** -> Backend returns **HTTP 403 Forbidden** (`Zero-Tolerance GDP policy prevents label printing`), proving defective cartons are physically blocked from dispatch.

### Act 3: Supervisor HITL Electronic Signature & 21 CFR Part 11 Chain Audit (75 sec)
1. Open **🛡️ Supervisor HITL**, select an escalated carton, enter Badge (`SUP-QA-401`), Root Cause, Notes, and 21 CFR Part 11 PIN, and click **APPROVE OVERRIDE & SIGN** or **CONFIRM REJECT & REPACK**.
2. Switch to **🔒 21 CFR Part 11 Audit** tab:
   - Click **🔒 VERIFY CHAIN INTEGRITY** -> traverses every block from Genesis (`#001`) to head, confirming **0 tampered blocks (`VERIFIED_VALID`)**.
   - Click **⬇️ EXPORT CSV** or **⬇️ EXPORT JSON** to download the regulatory compliance ledger.

### Act 4: Executive Analytics, INT8 Speedup & SAP/Manhattan ERP Sync (75 sec)
1. Switch to **⚖️ 4-Way Trade-Off** tab:
   - Show live DB KPIs (Total Inspections, Claims Avoided in USD, ESG CO₂e Saved), **Defect Pareto** bars, and **INT8 QNNPACK Benchmark (`0.216 ms`, `4,630 FPS`, `14.32x` speedup)**.
   - In **Enterprise ERP / WMS Webhook Gateway**, select `SAP_EWM`, check **Simulate ERP Offline Queue**, click **📤 DISPATCH WEBHOOK** -> status shows `QUEUED_RETRY`.
   - Click **🔁 REPLAY QUEUE** -> flushes retry ledger to `REPLAYED_200_OK` with HMAC-SHA256 signature verification.
   - Review the **Ergonomic Workload Guardrail Monitor** table highlighting `OP-102` (`MANDATORY_BREAK_REQUIRED`).

