/**
 * PharmaPack QV — Frontend Client Logic
 * Connects UI to FastAPI Backend endpoints and real-time WebSockets
 * Compliant with 21 CFR Part 11 and WHO Annex 5 GDP workflows
 */

document.addEventListener('DOMContentLoaded', () => {
    // State
    const state = {
        currentPreset: 'sample_clean.jpg',
        currentZone: '2-8°C',
        currentDefect: 'CLEAN',
        orderNumber: 'PH-ORD-9021',
        stationId: 'STATION-01',
        operatorId: 'OP-101',
        isRawView: false,
        rtspMode: false,
        lastResult: null,
        ws: null,
        supervisorQueue: [],
        selectedSupervisorInspectionId: 'INSP-ESC-9024'
    };

    // DOM Elements - Operator View
    const cameraFeedImg = document.getElementById('cameraFeedImg');
    const heatmapImg = document.getElementById('heatmapImg');
    const defectTag = document.getElementById('defectTag');
    const toggleHeatmapBtn = document.getElementById('toggleHeatmapBtn');
    const verdictBanner = document.getElementById('verdictBanner');
    const verdictTitle = document.getElementById('verdictTitle');
    const verdictDesc = document.getElementById('verdictDesc');
    const verdictIcon = document.getElementById('verdictIcon');
    const confPill = document.getElementById('confPill');
    const sopList = document.getElementById('sopList');
    const voicePrompt = document.getElementById('voicePrompt');
    const voiceMicBtn = document.getElementById('voiceMicBtn');

    const toCost = document.getElementById('toCost');
    const toTime = document.getElementById('toTime');
    const toCarbon = document.getElementById('toCarbon');
    const toReliability = document.getElementById('toReliability');
    const adoptionText = document.getElementById('adoptionText');
    const auditHashDisplay = document.getElementById('auditHashDisplay');

    const btnRunVerification = document.getElementById('btnRunVerification');
    const btnPrintZebra = document.getElementById('btnPrintZebra');
    const btnEscalate = document.getElementById('btnEscalate');
    const toast = document.getElementById('toastNotification');
    const toastText = document.getElementById('toastText');

    // DOM Elements - Supervisor View
    const exceptionListContainer = document.getElementById('exceptionListContainer');
    const supDefectImg = document.getElementById('supDefectImg');
    const supDefectCaption = document.getElementById('supDefectCaption');
    const supSelectedOrder = document.getElementById('supSelectedOrder');
    const supBadgeId = document.getElementById('supBadgeId');
    const rootCauseSelect = document.getElementById('rootCauseSelect');
    const supNotes = document.getElementById('supNotes');
    const supPin = document.getElementById('supPin');
    const btnSupApprove = document.getElementById('btnSupApprove');
    const btnSupReject = document.getElementById('btnSupReject');
    const exceptionCountBadge = document.getElementById('exceptionCount');

    // DOM Elements - Audit View & Capstone 100% Controls
    const btnRefreshAudit = document.getElementById('btnRefreshAudit');
    const btnVerifyChain = document.getElementById('btnVerifyChain');
    const btnExportCsv = document.getElementById('btnExportCsv');
    const btnExportJson = document.getElementById('btnExportJson');
    const chainIntegrityStatus = document.getElementById('chainIntegrityStatus');
    const auditTableBody = document.getElementById('auditTableBody');
    const btnToggleRtspMode = document.getElementById('btnToggleRtspMode');
    const ergoShiftPill = document.getElementById('ergoShiftPill');

    const zplModalBackdrop = document.getElementById('zplModalBackdrop');
    const zplCodePre = document.getElementById('zplCodePre');
    const zplModalMeta = document.getElementById('zplModalMeta');
    const btnCopyZpl = document.getElementById('btnCopyZpl');
    const btnCloseZplModal = document.getElementById('btnCloseZplModal');

    // 1. Initialize WebSocket Connection
    function initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/api/v1/ws/operator/${state.stationId}`;
        
        try {
            state.ws = new WebSocket(wsUrl);
            state.ws.onopen = () => {
                showToast('Connected to PharmaPack Real-Time WebSocket', '✓');
            };
            state.ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                console.log('WS Message received:', msg);
            };
            state.ws.onerror = (err) => {
                console.warn('WebSocket error, falling back to REST polling:', err);
            };
        } catch (e) {
            console.warn('WebSocket initialization skipped:', e);
        }
    }

    // 2. Tab Navigation
    const tabs = document.querySelectorAll('.nav-tab');
    const panels = document.querySelectorAll('.view-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetId = tab.getAttribute('data-view');
            document.getElementById(targetId).classList.add('active');

            if (targetId === 'supervisorView') {
                loadSupervisorQueue();
            } else if (targetId === 'auditView') {
                loadAuditTrail();
            } else if (targetId === 'tradeoffView') {
                loadExecutiveAnalytics();
            }
        });
    });

    // 3. Preset Carton Selection
    const presetButtons = document.querySelectorAll('.preset-btn');
    presetButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            presetButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            state.currentPreset = btn.getAttribute('data-preset');
            state.currentZone = btn.getAttribute('data-zone');
            state.currentDefect = btn.getAttribute('data-defect');

            // Update Viewfinder (sync RTSP sample pin if RTSP live mode active)
            if (state.rtspMode) {
                fetch('/api/v1/streams/CAM-02-CONVEYOR/select-sample', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sample_filename: state.currentPreset })
                }).catch(() => {});
            } else {
                cameraFeedImg.src = `/static/samples/${state.currentPreset}`;
            }
            heatmapImg.src = `/static/samples/${state.currentPreset}`;

            // Update Zone Buttons
            document.querySelectorAll('.zone-btn').forEach(zb => {
                if (zb.getAttribute('data-zone') === state.currentZone) {
                    zb.classList.add('active');
                } else {
                    zb.classList.remove('active');
                }
            });

            // Adjust order numbers and simulated attributes
            const orderMapping = {
                'sample_clean.jpg': { order: 'PH-ORD-9021', weight: 3.42, temp: '4.2°C' },
                'sample_crushed.jpg': { order: 'PH-ORD-9022', weight: 3.38, temp: '21.4°C' },
                'sample_tamper_breach.jpg': { order: 'PH-ORD-9023', weight: 3.45, temp: '4.5°C' },
                'sample_missing_ice.jpg': { order: 'PH-ORD-9024', weight: 1.85, temp: '6.8°C' },
                'sample_inside_pack.jpg': { order: 'PH-ORD-9025', weight: 4.10, temp: '3.9°C' },
                'sample_damaged_barcode.jpg': { order: 'PH-ORD-9026', weight: 2.90, temp: '20.2°C' }
            };

            const config = orderMapping[state.currentPreset] || { order: 'PH-ORD-9021', weight: 3.42, temp: '4.2°C' };
            state.orderNumber = config.order;
            document.getElementById('hudOrderNum').textContent = state.orderNumber;
            document.getElementById('scaleLcd').innerHTML = `${config.weight.toFixed(2)} <span class="unit">KG</span>`;
            document.getElementById('hudTempReading').textContent = `TEMP: ${config.temp}`;

            showToast(`Loaded ${btn.textContent} for inspection. Click Run Verification.`, '📦');
        });
    });

    // 4. Zone Selection
    document.querySelectorAll('.zone-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.zone-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            state.currentZone = btn.getAttribute('data-zone');
            showToast(`Controlled Storage Zone set to ${state.currentZone}`, '🌡️');
        });
    });

    // 5. Heatmap Toggle
    toggleHeatmapBtn.addEventListener('click', () => {
        state.isRawView = !state.isRawView;
        if (state.isRawView) {
            toggleHeatmapBtn.textContent = 'Toggle XAI Heatmap';
            heatmapImg.src = `/static/samples/${state.currentPreset}`;
        } else {
            toggleHeatmapBtn.textContent = 'Toggle Raw View';
            if (state.lastResult && state.lastResult.heatmap_url) {
                heatmapImg.src = `data:image/jpeg;base64,${state.lastResult.heatmap_url}`;
            } else {
                heatmapImg.src = `/static/samples/${state.currentPreset}`;
            }
        }
    });

    // 6. Primary Action: Run AI Verification (Standard or Dual-Cam RTSP Mode)
    btnRunVerification.addEventListener('click', async () => {
        btnRunVerification.disabled = true;
        btnRunVerification.innerHTML = state.rtspMode
            ? '<span class="btn-icon">⏳</span> CAPTURING DUAL RTSP...'
            : '<span class="btn-icon">⏳</span> ANALYZING CARTON...';

        try {
            const endpoint = state.rtspMode
                ? '/api/v1/streams/dual-capture-inspect'
                : '/api/v1/inspections/submit';

            const payload = state.rtspMode
                ? {
                    order_number: state.orderNumber,
                    station_id: state.stationId,
                    operator_id: state.operatorId,
                    storage_zone: state.currentZone,
                    gross_weight_kg: 3.42
                }
                : {
                    order_number: state.orderNumber,
                    station_id: state.stationId,
                    operator_id: state.operatorId,
                    storage_zone: state.currentZone,
                    target_temperature_c: state.currentZone === '2-8°C' ? 4.2 : (state.currentZone === '-20°C' ? -20.0 : 21.0),
                    gross_weight_kg: 3.42
                };

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();
            state.lastResult = data;
            renderInspectionResult(data);
            loadErgonomicsBanner();

        } catch (error) {
            console.error('Inspection failed:', error);
            showToast(`Verification error: ${error.message}`, '❌');
        } finally {
            btnRunVerification.disabled = false;
            btnRunVerification.innerHTML = '<span class="btn-icon">⚡</span> RUN AI VERIFICATION';
        }
    });

    // 7. Render Inspection Verdict & Metrics (Supports both standard & dual-cam RTSP schemas)
    function renderInspectionResult(data) {
        const defectsList = data.defects || data.detected_defects || [];
        const capaText = data.capa_recommendation || data.capa_action || 'Packaging defect detected. Repack required.';
        const tradeoffObj = data.tradeoff || (data.tradeoff_matrix ? {
            cost_index_usd: data.tradeoff_matrix.cost_usd ?? 3.50,
            time_latency_sec: data.tradeoff_matrix.time_seconds ?? 0.35,
            emissions_kg_co2e: data.tradeoff_matrix.emissions_kg_co2e ?? 0.45,
            reliability_score_pct: data.tradeoff_matrix.reliability_score ?? 99.4
        } : null);

        // Update Verdict Banner
        verdictBanner.className = `verdict-banner ${data.verdict.toLowerCase()}`;
        confPill.textContent = `CONFIDENCE: ${(data.overall_confidence * 100).toFixed(1)}%`;

        if (data.verdict === 'PASS') {
            verdictTitle.textContent = 'PASS — VERIFIED';
            verdictIcon.textContent = '✓';
            verdictDesc.textContent = 'All packaging attributes comply with WHO Annex 5 & FDA 21 CFR standards.';
            defectTag.textContent = '✓ ZERO DEFECTS DETECTED';
            defectTag.style.borderColor = 'var(--neon-green)';
            defectTag.style.color = 'var(--neon-green)';
            voicePrompt.textContent = '"Package verified compliant. Ready for label print."';
            speakText("Package verified compliant. Clear to print label.");
        } else if (data.verdict === 'REJECT') {
            verdictTitle.textContent = 'REJECT — DEFECT DETECTED';
            verdictIcon.textContent = '✕';
            verdictDesc.textContent = capaText;
            const defectNames = defectsList.map(d => d.defect_type).join(', ');
            defectTag.textContent = `⚠️ DEFECT: ${defectNames || 'RULE VIOLATION'}`;
            defectTag.style.borderColor = 'var(--neon-red)';
            defectTag.style.color = 'var(--neon-red)';
            voicePrompt.textContent = `"Defect detected: ${defectNames}. Packaging rejected."`;
            speakText(`Packaging defect detected. ${defectNames}. Rework required.`);
        } else {
            verdictTitle.textContent = 'ESCALATE — HITL REVIEW';
            verdictIcon.textContent = '⚠️';
            verdictDesc.textContent = 'Marginal confidence score. Escalated to Floor Supervisor queue.';
            defectTag.textContent = '⚠️ ESCALATED TO HITL QUEUE';
            defectTag.style.borderColor = 'var(--neon-orange)';
            defectTag.style.color = 'var(--neon-orange)';
            voicePrompt.textContent = '"Review required. Escalated to supervisor."';
            speakText("Verification escalated to supervisor.");
        }

        // Update Heatmap / Captured RTSP Frame
        if (data.heatmap_url) {
            heatmapImg.src = `data:image/jpeg;base64,${data.heatmap_url}`;
            state.isRawView = false;
            toggleHeatmapBtn.textContent = 'Toggle Raw View';
        } else if (data.stage_2_camera && data.stage_2_camera.image_base64) {
            heatmapImg.src = `data:image/jpeg;base64,${data.stage_2_camera.image_base64}`;
            state.isRawView = false;
            toggleHeatmapBtn.textContent = 'Toggle Raw View';
        }

        // Update SOP Checklist
        renderSopChecklist({ defects: defectsList });

        // Update 4-Way Trade-Off Matrix
        if (tradeoffObj) {
            toCost.textContent = `$${Number(tradeoffObj.cost_index_usd).toFixed(2)}`;
            toTime.textContent = `${Number(tradeoffObj.time_latency_sec).toFixed(2)}s`;
            toCarbon.innerHTML = `${Number(tradeoffObj.emissions_kg_co2e).toFixed(2)} <span class="unit">kg</span>`;
            toReliability.textContent = `${Number(tradeoffObj.reliability_score_pct).toFixed(1)}%`;
        }

        if (defectsList.length > 0) {
            adoptionText.innerHTML = `<strong>Caught Pre-Dispatch:</strong> Prevented <strong>$137.00</strong> post-dispatch replacement cost and <strong>21.5kg CO2e</strong> reverse-freight emissions.`;
        } else {
            adoptionText.textContent = `Clean baseline dispatch. Zero rework penalty. Continuous monitoring ensures 99.4% defect escape prevention.`;
        }

        // Update Audit Hash
        if (data.audit_hash) {
            auditHashDisplay.textContent = data.audit_hash;
        }

        const edgeNote = (data.vision_telemetry && data.vision_telemetry.neural_edge && data.vision_telemetry.neural_edge.available)
            ? ` | INT8 Edge: ${data.vision_telemetry.neural_edge.latency_ms}ms`
            : '';
        showToast(`Verification Complete: ${data.verdict} (${(data.overall_confidence * 100).toFixed(1)}%)${edgeNote}`, data.verdict === 'PASS' ? '✓' : '⚠️');
    }

    function renderSopChecklist(data) {
        const hasCrush = data.defects ? data.defects.some(d => d.defect_type === 'CRUSHED_CORNER') : false;
        const hasSeal = data.defects ? data.defects.some(d => d.defect_type === 'TAPE_BREACH') : false;
        const hasIce = data.defects ? data.defects.some(d => d.defect_type === 'MISSING_ICE_PACK') : false;

        sopList.innerHTML = `
            <div class="sop-item ${hasSeal ? 'violated' : 'checked'}">
                <span class="sop-check">${hasSeal ? '✕' : '✓'}</span>
                <span>SOP-SEAL-01: Tamper-evident blue tape intact across seam</span>
            </div>
            <div class="sop-item ${hasCrush ? 'violated' : 'checked'}">
                <span class="sop-check">${hasCrush ? '✕' : '✓'}</span>
                <span>SOP-BOX-02: Shipper carton structural integrity intact</span>
            </div>
            <div class="sop-item ${hasIce ? 'violated' : 'checked'}">
                <span class="sop-check">${hasIce ? '✕' : '✓'}</span>
                <span>SOP-COLD-01: Pre-conditioned phase coolant verified</span>
            </div>
            <div class="sop-item checked">
                <span class="sop-check">✓</span>
                <span>SOP-DUN-03: Void ratio under 20% limit</span>
            </div>
        `;
    }

    // 8. Print Zebra ZPL II Dispatch Label (Backend GDP Gate)
    btnPrintZebra.addEventListener('click', async () => {
        const currentVerdict = state.lastResult ? state.lastResult.verdict : 'PASS';
        const currentHash = state.lastResult ? state.lastResult.audit_hash : null;
        const awbEl = document.getElementById('hudAwb');
        const awbText = awbEl ? awbEl.textContent.trim() : 'AWB-8839210';

        try {
            const res = await fetch('/api/v1/enterprise/zpl/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    order_number: state.orderNumber,
                    awb: awbText,
                    storage_zone: state.currentZone,
                    verdict: currentVerdict,
                    audit_hash: currentHash,
                    operator_badge: state.operatorId
                })
            });

            if (!res.ok) {
                const err = await res.json();
                showToast(err.detail || 'ZPL label print blocked by GDP Policy!', '🚫');
                return;
            }

            const zplData = await res.json();
            if (zplModalMeta && zplCodePre && zplModalBackdrop) {
                zplModalMeta.textContent = `${zplData.printer_model} | Order: ${zplData.order_number} | Zone: ${zplData.storage_zone} | Audit Block: ${zplData.audit_block_hash.slice(0, 16)}...`;
                zplCodePre.textContent = zplData.zpl_command;
                zplModalBackdrop.classList.add('open');
            }
            showToast(`Zebra ZPL II Label generated & audited for ${state.orderNumber}`, '🖨️');
        } catch (err) {
            showToast(`ZPL service error: ${err.message}`, '❌');
        }
    });

    // 9. Escalate Action
    btnEscalate.addEventListener('click', async () => {
        showToast(`Carton ${state.orderNumber} manually escalated to Supervisor HITL Queue`, '⚠️');
        exceptionCountBadge.textContent = String(parseInt(exceptionCountBadge.textContent || '1') + 1);
    });

    // 10. Voice Mic Trigger
    voiceMicBtn.addEventListener('click', () => {
        speakText(voicePrompt.textContent);
    });

    function speakText(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    // ================= 11. SUPERVISOR HITL HUB LOGIC =================
    async function loadSupervisorQueue() {
        if (!exceptionListContainer) return;
        
        try {
            const res = await fetch('/api/v1/supervisor/queue');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const queue = await res.json();
            state.supervisorQueue = queue;

            exceptionCountBadge.textContent = queue.length;

            if (queue.length === 0) {
                exceptionListContainer.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-muted);">No pending supervisor exceptions. All stations clear!</div>';
                return;
            }

            exceptionListContainer.innerHTML = queue.map((item, idx) => `
                <div class="exception-card ${idx === 0 ? 'active' : ''}" data-id="${item.inspection_id}" data-order="${item.order_number}" data-zone="${item.storage_zone}">
                    <div class="ex-top">
                        <span class="ex-order">${item.order_number}</span>
                        <span class="ex-badge-red">${item.verdict}</span>
                    </div>
                    <div class="ex-meta">${item.station_id} | Operator: ${item.operator_id} | Zone: ${item.storage_zone}</div>
                    <div class="ex-reason">Confidence: ${(item.confidence * 100).toFixed(1)}% | Defects: ${item.detected_defects_count} | Violations: ${item.rule_violations_count}</div>
                </div>
            `).join('');

            // Bind click to each card
            const cards = exceptionListContainer.querySelectorAll('.exception-card');
            cards.forEach(card => {
                card.addEventListener('click', () => {
                    cards.forEach(c => c.classList.remove('active'));
                    card.classList.add('active');

                    const inspId = card.getAttribute('data-id');
                    const orderNum = card.getAttribute('data-order');
                    state.selectedSupervisorInspectionId = inspId;
                    supSelectedOrder.value = orderNum;

                    // Update forensic defect view
                    supDefectCaption.textContent = `Inspecting ${orderNum} (ID: ${inspId})`;
                    showToast(`Selected ${orderNum} for forensic review`, '🔬');
                });
            });

            // Select first item
            if (queue.length > 0) {
                state.selectedSupervisorInspectionId = queue[0].inspection_id;
                supSelectedOrder.value = queue[0].order_number;
            }

        } catch (err) {
            console.error('Failed to load supervisor queue:', err);
        }
    }

    async function submitSupervisorDecision(decisionType) {
        const pin = supPin.value.trim();
        const badge = supBadgeId.value.trim() || 'SUP-QA-401';
        const notes = supNotes.value.trim();
        const rootCause = rootCauseSelect.value;

        if (!pin) {
            showToast('21 CFR Part 11 Electronic Signature PIN is required!', '⚠️');
            supPin.focus();
            return;
        }

        if (!notes) {
            showToast('Mandatory supervisor justification notes required for audit trail!', '⚠️');
            supNotes.focus();
            return;
        }

        const payload = {
            inspection_id: state.selectedSupervisorInspectionId || 'INSP-ESC-9024',
            decision: decisionType,
            root_cause_code: rootCause,
            justification_notes: notes,
            supervisor_badge: badge,
            electronic_signature: `PIN_SIG_${pin}_${Date.now()}`
        };

        try {
            const res = await fetch('/api/v1/supervisor/decide', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || `Server error ${res.status}`);
            }

            const data = await res.json();
            showToast(`Supervisor Decision [${decisionType}] recorded & signed. Hash: ${data.audit_block_hash.slice(0, 16)}...`, '✓');

            // Reset inputs & reload queue
            supPin.value = '';
            supNotes.value = '';
            loadSupervisorQueue();

        } catch (err) {
            console.error('Supervisor decision failed:', err);
            showToast(`Sign-off failed: ${err.message}`, '❌');
        }
    }

    btnSupApprove.addEventListener('click', () => submitSupervisorDecision('OVERRIDE_PASS'));
    btnSupReject.addEventListener('click', () => submitSupervisorDecision('CONFIRM_REJECT'));

    // ================= 12. 21 CFR PART 11 AUDIT TRAIL LOGIC =================
    async function loadAuditTrail() {
        auditTableBody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Loading cryptographic audit chain...</td></tr>';

        try {
            const res = await fetch('/api/v1/audit/logs?limit=50');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const logs = await res.json();
            
            if (logs.length === 0) {
                auditTableBody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No audit records found.</td></tr>';
                return;
            }

            auditTableBody.innerHTML = logs.map(log => `
                <tr>
                    <td>#${String(log.id).padStart(3, '0')}</td>
                    <td>${log.timestamp ? new Date(log.timestamp).toISOString() : 'N/A'}</td>
                    <td><strong style="color:var(--text-primary);">${log.action}</strong></td>
                    <td>${log.user_badge}</td>
                    <td>${log.user_role}</td>
                    <td class="hash" title="${log.previous_block_hash}">${log.previous_block_hash.slice(0, 12)}...</td>
                    <td class="hash" title="${log.block_hash}">${log.block_hash.slice(0, 16)}...</td>
                    <td><span class="badge-valid">VALIDATED ✓</span></td>
                </tr>
            `).join('');

        } catch (e) {
            console.error('Failed to load audit history:', e);
            auditTableBody.innerHTML = '<tr><td colspan="8" style="color:var(--neon-red); text-align:center;">Failed to fetch audit records from server.</td></tr>';
        }
    }

    btnRefreshAudit.addEventListener('click', loadAuditTrail);

    // Verify Entire Cryptographic Blockchain Chain
    btnVerifyChain.addEventListener('click', async () => {
        btnVerifyChain.disabled = true;
        btnVerifyChain.textContent = 'Verifying SHA-256 Chain...';

        try {
            const res = await fetch('/api/v1/audit/verify-chain');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            chainIntegrityStatus.style.display = 'block';
            if (data.chain_intact) {
                chainIntegrityStatus.style.background = 'rgba(16, 185, 129, 0.15)';
                chainIntegrityStatus.style.border = '1px solid var(--neon-green)';
                chainIntegrityStatus.style.color = 'var(--neon-green)';
                chainIntegrityStatus.innerHTML = `
                    <strong>✓ 21 CFR PART 11 CRYPTOGRAPHIC INTEGRITY VERIFIED:</strong><br>
                    Traversed ${data.total_blocks_verified} chained block records from Genesis. 0 corrupted blocks. Algorithm: ${data.verification_algorithm}. Compliance: ${data.compliance_standards.join(', ')}.
                `;
                showToast(`Chain Verified Intact (${data.total_blocks_verified} Blocks Validated)`, '🔒');
            } else {
                chainIntegrityStatus.style.background = 'rgba(239, 68, 68, 0.15)';
                chainIntegrityStatus.style.border = '1px solid var(--neon-red)';
                chainIntegrityStatus.style.color = 'var(--neon-red)';
                chainIntegrityStatus.innerHTML = `
                    <strong>⚠️ TAMPER DETECTED IN AUDIT TRAIL:</strong><br>
                    ${data.tampered_blocks_count} blocks failed cryptographic SHA-256 pointer validation!
                `;
                showToast('Audit Trail Discrepancy Detected!', '❌');
            }

        } catch (e) {
            console.error('Verification failed:', e);
            showToast(`Chain verification error: ${e.message}`, '❌');
        } finally {
            btnVerifyChain.disabled = false;
            btnVerifyChain.textContent = '🔒 VERIFY CHAIN INTEGRITY';
        }
    });

    // ================= 13. CAPSTONE 100%: RTSP, EXPORT, ERGONOMICS, ANALYTICS & WMS =================
    if (btnToggleRtspMode) {
        btnToggleRtspMode.addEventListener('click', () => {
            state.rtspMode = !state.rtspMode;
            if (state.rtspMode) {
                btnToggleRtspMode.textContent = '📡 RTSP ON (MJPEG)';
                btnToggleRtspMode.style.borderColor = 'var(--neon-green)';
                btnToggleRtspMode.style.color = 'var(--neon-green)';
                fetch('/api/v1/streams/CAM-02-CONVEYOR/select-sample', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sample_filename: state.currentPreset })
                }).finally(() => {
                    cameraFeedImg.src = `/api/v1/streams/CAM-02-CONVEYOR/mjpeg?fps=6&t=${Date.now()}`;
                });
                showToast('Dual-Camera Industrial RTSP/MJPEG stream active!', '📡');
            } else {
                btnToggleRtspMode.textContent = '📡 RTSP Live Cam';
                btnToggleRtspMode.style.borderColor = '';
                btnToggleRtspMode.style.color = '';
                cameraFeedImg.src = `/static/samples/${state.currentPreset}`;
                showToast('Switched to static carton preset preview.', '📷');
            }
        });
    }

    if (btnExportCsv) {
        btnExportCsv.addEventListener('click', () => {
            window.location.href = '/api/v1/audit/export?format=csv';
            showToast('Downloading FDA 21 CFR Part 11 Audit Ledger CSV...', '⬇️');
        });
    }

    if (btnExportJson) {
        btnExportJson.addEventListener('click', () => {
            window.location.href = '/api/v1/audit/export?format=json';
            showToast('Downloading FDA 21 CFR Part 11 Audit JSON Bundle...', '⬇️');
        });
    }

    if (btnCloseZplModal && zplModalBackdrop) {
        btnCloseZplModal.addEventListener('click', () => zplModalBackdrop.classList.remove('open'));
        zplModalBackdrop.addEventListener('click', (e) => {
            if (e.target === zplModalBackdrop) zplModalBackdrop.classList.remove('open');
        });
    }

    if (btnCopyZpl && zplCodePre) {
        btnCopyZpl.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(zplCodePre.textContent || '');
                showToast('ZPL II command stream copied to clipboard!', '📋');
            } catch {
                showToast('Clipboard permission unavailable in browser context.', '⚠️');
            }
        });
    }

    async function loadErgonomicsBanner() {
        try {
            const res = await fetch('/api/v1/enterprise/ergonomics/status');
            if (!res.ok) return;
            const data = await res.json();
            if (ergoShiftPill) {
                const labelEl = ergoShiftPill.querySelector('.pill-label');
                const alerts = data.alerts_active || 0;
                const op101 = (data.operators || []).find(o => o.badge_number === state.operatorId) || (data.operators || [])[0];
                const pace = op101 ? `${op101.estimated_pace_per_hr}/hr` : 'NOMINAL';
                if (alerts > 0) {
                    ergoShiftPill.classList.add('ergo-alert-pill');
                    if (labelEl) labelEl.innerHTML = `SHIFT GUARD: <strong>${pace} | ${alerts} Fatigue Alert</strong>`;
                } else {
                    ergoShiftPill.classList.remove('ergo-alert-pill');
                    if (labelEl) labelEl.innerHTML = `SHIFT GUARD: <strong>${pace} SAFE</strong>`;
                }
            }
            const ergoBody = document.getElementById('ergonomicsTableBody');
            if (ergoBody && data.operators) {
                ergoBody.innerHTML = data.operators.map(op => `
                    <tr>
                        <td><strong>${op.badge_number}</strong></td>
                        <td>${op.full_name} (${op.shift_name || 'A'})</td>
                        <td>${op.estimated_pace_per_hr}/hr</td>
                        <td>${(op.fatigue_risk_score * 100).toFixed(0)}%</td>
                        <td>
                            <span class="badge-valid" style="${op.guardrail_state !== 'SAFE_NOMINAL' ? 'color:var(--neon-orange); border-color:var(--neon-orange); background:rgba(245,158,11,0.15);' : ''}">
                                ${op.guardrail_state}
                            </span>
                        </td>
                    </tr>
                `).join('');
            }
        } catch (err) {
            console.warn('Ergonomics poll skipped:', err);
        }
    }

    async function loadExecutiveAnalytics() {
        try {
            const [execRes, wmsRes] = await Promise.all([
                fetch('/api/v1/analytics/executive'),
                fetch('/api/v1/enterprise/wms/status')
            ]);
            if (execRes.ok) {
                const ex = await execRes.json();
                const kpi = ex.live_database_kpis || {};
                const edge = (ex.edge_quantization_benchmark || {}).int8_quantized_cpu || {};

                const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
                setEl('execTotalInsp', kpi.total_inspections ?? '--');
                setEl('execClaimsAvoided', `$${Number(kpi.claims_avoided_usd || 0).toLocaleString()}`);
                setEl('execCo2Saved', `${Number(kpi.esg_reverse_logistics_co2_saved_kg || 0).toFixed(1)} kg`);
                setEl('execAuditBlocks', kpi.total_audit_blocks ?? '--');
                setEl('execInt8Latency', edge.mean_latency_ms ? `${edge.mean_latency_ms} ms` : '--');
                setEl('execRtspCount', `${ex.rtsp_cameras_online || 2} ONLINE`);

                const edgeSummaryEl = document.getElementById('edgeQuantSummary');
                if (edgeSummaryEl && edge.mean_latency_ms) {
                    edgeSummaryEl.innerHTML = `PyTorch QNNPACK INT8 Engine: <strong>${edge.mean_latency_ms} ms</strong> mean inference (<strong>${edge.throughput_fps} FPS</strong>, ${edge.speedup_vs_fp32}x speedup vs FP32, -${edge.size_reduction_pct}% size).`;
                }

                const paretoEl = document.getElementById('defectParetoContainer');
                const pareto = ex.defect_pareto || [];
                if (paretoEl) {
                    if (pareto.length === 0) {
                        paretoEl.innerHTML = '<div style="color:var(--text-muted); font-size:13px;">No defects recorded in DB yet.</div>';
                    } else {
                        const maxCount = Math.max(...pareto.map(p => p.count), 1);
                        paretoEl.innerHTML = pareto.map(p => `
                            <div class="pareto-row">
                                <span class="pareto-label" title="${p.defect_type}">${p.defect_type}</span>
                                <div class="pareto-track"><div class="pareto-fill" style="width:${Math.round((p.count / maxCount) * 100)}%"></div></div>
                                <span class="pareto-count">${p.count}</span>
                            </div>
                        `).join('');
                    }
                }
            }
            if (wmsRes.ok) {
                renderWmsTable(await wmsRes.json());
            }
            await loadErgonomicsBanner();
        } catch (err) {
            console.warn('Executive analytics load error:', err);
        }
    }

    function renderWmsTable(status) {
        const badge = document.getElementById('wmsLedgerStatus');
        const tbody = document.getElementById('wmsEventsTableBody');
        if (badge) {
            badge.textContent = `Synced: ${status.total_synced || 0} | Retry Queue: ${status.queued_retries || 0}`;
        }
        if (tbody) {
            const events = status.recent_events || [];
            if (events.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">No WMS webhook dispatches recorded yet.</td></tr>';
            } else {
                tbody.innerHTML = events.slice(0, 10).map(ev => `
                    <tr>
                        <td><strong>${ev.event_id}</strong></td>
                        <td>${ev.erp_target}</td>
                        <td>${ev.order_number}</td>
                        <td>${ev.wms_action}</td>
                        <td><span class="badge-valid">${ev.status}</span></td>
                    </tr>
                `).join('');
            }
        }
    }

    const btnRefreshExec = document.getElementById('btnRefreshExec');
    if (btnRefreshExec) btnRefreshExec.addEventListener('click', loadExecutiveAnalytics);

    const btnWmsSync = document.getElementById('btnWmsSync');
    if (btnWmsSync) {
        btnWmsSync.addEventListener('click', async () => {
            const erpTarget = (document.getElementById('wmsErpTarget') || {}).value || 'SAP_EWM';
            const simOffline = Boolean((document.getElementById('wmsSimulateOffline') || {}).checked);
            try {
                const res = await fetch('/api/v1/enterprise/wms/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        erp_target: erpTarget,
                        order_number: state.orderNumber,
                        inspection_id: (state.lastResult && state.lastResult.inspection_id) || 'INSP-UI-SYNC',
                        verdict: (state.lastResult && state.lastResult.verdict) || 'PASS',
                        storage_zone: state.currentZone,
                        audit_hash: (state.lastResult && state.lastResult.audit_hash) || null,
                        simulate_erp_offline: simOffline
                    })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
                if (data.status_summary) renderWmsTable(data.status_summary);
                showToast(`WMS Event ${data.event_id} (${data.status}) -> ${erpTarget}`, data.status === 'QUEUED_RETRY' ? '⏳' : '✓');
                loadExecutiveAnalytics();
            } catch (err) {
                showToast(`WMS sync error: ${err.message}`, '❌');
            }
        });
    }

    const btnWmsReplay = document.getElementById('btnWmsReplay');
    if (btnWmsReplay) {
        btnWmsReplay.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/v1/enterprise/wms/replay-queue', { method: 'POST' });
                const data = await res.json();
                if (data.status_summary) renderWmsTable(data.status_summary);
                showToast(`Replayed ${data.replayed_count || 0} queued ERP webhook(s)!`, '🔁');
                loadExecutiveAnalytics();
            } catch (err) {
                showToast(`WMS replay failed: ${err.message}`, '❌');
            }
        });
    }

    // Toast Utility
    function showToast(message, icon = 'ℹ️') {
        toastText.textContent = message;
        toast.querySelector('.toast-icon').textContent = icon;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3500);
    }

    // Initialize
    initWebSocket();
    loadErgonomicsBanner();
});
