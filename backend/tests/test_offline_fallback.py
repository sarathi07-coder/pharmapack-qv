"""
Unit & Integration Tests for Offline Fallback & Circuit Breaker Resilience
Verifies Qbee AI Requirement #1: System resilience under cloud API drops.
"""
from PIL import Image
from ml.models.hybrid_vision_client import HybridVisionClient, CircuitState

def test_circuit_breaker_forced_offline():
    client = HybridVisionClient(api_key="test_key", failure_threshold=2)
    client.force_offline(True)
    assert client.state == CircuitState.OPEN

    test_img = Image.new("RGB", (640, 640), color=(180, 140, 90))
    res = client.predict(test_img)

    assert res["source"] == "OFFLINE_EDGE_FALLBACK"
    assert res["circuit_state"] == "OPEN"
    assert res["latency_ms"] < 100.0  # Fast edge execution
    assert "defects" in res

def test_circuit_breaker_telemetry():
    client = HybridVisionClient(api_key="test_key")
    client.force_offline(True)

    img = Image.new("RGB", (640, 640), color=(100, 100, 100))
    client.predict(img)
    client.predict(img)

    telemetry = client.get_telemetry()
    assert telemetry["total_inspections"] == 2
    assert telemetry["offline_fallback_count"] == 2
    assert telemetry["circuit_state"] == "OPEN"
    assert "99.99%" in telemetry["resilience_sla"]

def test_offline_crushed_corner_detection():
    import numpy as np
    client = HybridVisionClient(api_key=None)
    client.force_offline(True)

    # Create synthetic crushed corner image (noisy high-contrast corner shadow)
    arr = np.ones((640, 640, 3), dtype=np.uint8) * 180
    # Add dark crumpled corner shadow in top-right
    arr[70:200, 450:600] = np.random.randint(20, 100, (130, 150, 3), dtype=np.uint8)
    crushed_img = Image.fromarray(arr)

    res = client.predict(crushed_img)
    assert res["source"] == "OFFLINE_EDGE_FALLBACK"
    assert any(d["defect_type"] == "CRUSHED_CORNER" for d in res["defects"])
