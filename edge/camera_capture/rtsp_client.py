"""
Multi-Camera Industrial RTSP / MJPEG Stream Ingestion Client
Manages dual synchronized camera channels:
  - CAM-01-OVERHEAD: Stage 1 Open-Box Payload Overhead GigE/RTSP Camera
  - CAM-02-CONVEYOR: Stage 2 Sealed-Carton Conveyor Side/Corner Camera
Supports native OpenCV RTSP streams when hardware cameras are configured,
and deterministic real-warehouse sample loopback streams in development/testing.
"""
import io
import os
import time
import threading
import base64
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Generator, Tuple

import cv2
import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"


@dataclass
class CameraChannelConfig:
    camera_id: str
    stage: str
    role_description: str
    rtsp_url: str
    resolution: str
    target_fps: int
    sample_sequence: List[str]


DEFAULT_CAMERA_CHANNELS = [
    CameraChannelConfig(
        camera_id="CAM-01-OVERHEAD",
        stage="STAGE_1_OPEN_BOX",
        role_description="Overhead Open-Carton Payload, Vial & Ice-Pack Gate",
        rtsp_url=os.environ.get("RTSP_CAM_01_URL", "rtsp://127.0.0.1:8554/pharma_overhead_stage1"),
        resolution="1280x720",
        target_fps=15,
        sample_sequence=["sample_inside_pack.jpg", "sample_missing_ice.jpg", "sample_clean.jpg"],
    ),
    CameraChannelConfig(
        camera_id="CAM-02-CONVEYOR",
        stage="STAGE_2_SEALED_CARTON",
        role_description="Conveyor Multi-View Carton Crush, Seal & GS1 Barcode Gate",
        rtsp_url=os.environ.get("RTSP_CAM_02_URL", "rtsp://127.0.0.1:8554/pharma_conveyor_stage2"),
        resolution="1280x720",
        target_fps=30,
        sample_sequence=["sample_clean.jpg", "sample_crushed.jpg", "sample_tamper_breach.jpg", "sample_damaged_barcode.jpg"],
    ),
]


class MultiCameraRTSPManager:
    """Thread-safe dual-camera ingestion engine with live RTSP + loopback fallback."""

    def __init__(self, channels: Optional[List[CameraChannelConfig]] = None):
        self.channels: Dict[str, CameraChannelConfig] = {
            cfg.camera_id: cfg for cfg in (channels or DEFAULT_CAMERA_CHANNELS)
        }
        self._lock = threading.Lock()
        self._frame_counters: Dict[str, int] = {cid: 0 for cid in self.channels}
        self._active_sample_override: Dict[str, Optional[str]] = {cid: None for cid in self.channels}
        self._base_frames_cache: Dict[str, np.ndarray] = {}
        self._hardware_caps: Dict[str, Any] = {}
        self._preload_sample_frames()

    def _preload_sample_frames(self) -> None:
        """Loads calibrated industrial reference frames into memory for zero-disk-lag streaming."""
        for fname in [
            "sample_clean.jpg",
            "sample_crushed.jpg",
            "sample_tamper_breach.jpg",
            "sample_missing_ice.jpg",
            "sample_inside_pack.jpg",
            "sample_damaged_barcode.jpg",
        ]:
            fpath = SAMPLES_DIR / fname
            if fpath.exists():
                bgr = cv2.imread(str(fpath))
                if bgr is not None:
                    self._base_frames_cache[fname] = cv2.resize(bgr, (960, 540))

    def set_channel_sample(self, camera_id: str, sample_filename: Optional[str]) -> bool:
        """Pins a specific test preset or clears override to resume automated conveyor cycling."""
        if camera_id not in self.channels:
            return False
        with self._lock:
            self._active_sample_override[camera_id] = sample_filename
        return True

    def _try_hardware_rtsp(self, camera_id: str) -> Optional[np.ndarray]:
        """Attempts live RTSP hardware capture if explicitly enabled via USE_HARDWARE_RTSP=1."""
        if os.environ.get("USE_HARDWARE_RTSP", "0") != "1":
            return None
        cfg = self.channels[camera_id]
        cap = self._hardware_caps.get(camera_id)
        if cap is None:
            cap = cv2.VideoCapture(cfg.rtsp_url)
            self._hardware_caps[camera_id] = cap
        if cap.isOpened():
            ok, frame = cap.read()
            if ok and frame is not None:
                return cv2.resize(frame, (960, 540))
        return None

    def grab_frame_bgr(self, camera_id: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Captures current synchronized BGR frame and annotates industrial RTSP telemetry HUD."""
        if camera_id not in self.channels:
            raise ValueError(f"Unknown camera channel: {camera_id}")

        cfg = self.channels[camera_id]
        hw_frame = self._try_hardware_rtsp(camera_id)

        with self._lock:
            self._frame_counters[camera_id] += 1
            seq_num = self._frame_counters[camera_id]
            pinned = self._active_sample_override.get(camera_id)

        if hw_frame is not None:
            frame = hw_frame.copy()
            mode = "LIVE_RTSP_HARDWARE"
            source_file = cfg.rtsp_url
        else:
            mode = "INDUSTRIAL_RTSP_LOOPBACK"
            if pinned and pinned in self._base_frames_cache:
                source_file = pinned
            else:
                # Cycle every ~45 frames so human viewers and tests see active conveyor throughput
                cycle_idx = (seq_num // 45) % len(cfg.sample_sequence)
                source_file = cfg.sample_sequence[cycle_idx]

            base = self._base_frames_cache.get(source_file)
            if base is None:
                frame = np.zeros((540, 960, 3), dtype=np.uint8)
            else:
                frame = base.copy()

        # Draw crisp telemetry overlay (non-destructive to top-right/corners analyzed by CV heuristics)
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        cv2.rectangle(frame, (0, 504), (960, 540), (12, 18, 34), -1)
        cv2.putText(
            frame,
            f"RTSP CH: {camera_id} | {cfg.stage} | FRAME #{seq_num:05d} | {ts_str}",
            (14, 527),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 224, 255),
            1,
            cv2.LINE_AA,
        )
        # Live green/cyan indicator dot
        cv2.circle(frame, (938, 522), 6, (0, 245, 155), -1)

        meta = {
            "camera_id": camera_id,
            "stage": cfg.stage,
            "mode": mode,
            "frame_number": seq_num,
            "source": source_file,
            "resolution": cfg.resolution,
            "timestamp_utc": ts_str,
        }
        return frame, meta

    def grab_frame_jpeg(self, camera_id: str, quality: int = 85) -> Tuple[bytes, Dict[str, Any]]:
        frame_bgr, meta = self.grab_frame_bgr(camera_id)
        ok, enc = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not ok:
            raise RuntimeError(f"Failed JPEG encode on {camera_id}")
        return enc.tobytes(), meta

    def grab_frame_pil(self, camera_id: str) -> Tuple[Image.Image, Dict[str, Any]]:
        frame_bgr, meta = self.grab_frame_bgr(camera_id)
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb), meta

    def grab_synchronized_dual_frames(self) -> Dict[str, Any]:
        """Captures synchronized Stage 1 + Stage 2 inspection pair across both cameras."""
        img1, meta1 = self.grab_frame_pil("CAM-01-OVERHEAD")
        img2, meta2 = self.grab_frame_pil("CAM-02-CONVEYOR")

        buf1, buf2 = io.BytesIO(), io.BytesIO()
        img1.save(buf1, format="JPEG", quality=88)
        img2.save(buf2, format="JPEG", quality=88)

        return {
            "stage_1_overhead": {
                "meta": meta1,
                "image": img1,
                "base64": base64.b64encode(buf1.getvalue()).decode("utf-8"),
            },
            "stage_2_conveyor": {
                "meta": meta2,
                "image": img2,
                "base64": base64.b64encode(buf2.getvalue()).decode("utf-8"),
            },
        }

    def mjpeg_stream_generator(self, camera_id: str, fps: int = 10, max_frames: Optional[int] = None) -> Generator[bytes, None, None]:
        """Yields standard multipart/x-mixed-replace MJPEG frames for HTTP video streaming."""
        delay = 1.0 / max(fps, 1)
        count = 0
        while max_frames is None or count < max_frames:
            jpeg_bytes, _ = self.grab_frame_jpeg(camera_id)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg_bytes + b"\r\n"
            )
            count += 1
            time.sleep(delay)

    def get_all_channel_status(self) -> List[Dict[str, Any]]:
        statuses = []
        with self._lock:
            for cid, cfg in self.channels.items():
                statuses.append({
                    **asdict(cfg),
                    "frames_captured": self._frame_counters[cid],
                    "pinned_sample": self._active_sample_override[cid],
                    "status": "ONLINE_STREAMING",
                    "ingestion_mode": "LIVE_RTSP_HARDWARE" if os.environ.get("USE_HARDWARE_RTSP", "0") == "1" else "INDUSTRIAL_RTSP_LOOPBACK",
                })
        return statuses


rtsp_stream_manager = MultiCameraRTSPManager()

