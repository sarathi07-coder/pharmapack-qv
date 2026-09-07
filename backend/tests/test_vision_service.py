"""
Unit Tests for Vision Service and Model Pipeline
"""
from PIL import Image
from ml.dataset.synthetic_generator import PharmaPackageGenerator
from ml.models.vision_service import vision_service

def test_vision_pipeline_clean_image():
    generator = PharmaPackageGenerator()
    img, _ = generator.generate_package(defect_type="CLEAN", zone="2-8°C")
    result = vision_service.process_image(img, order_hint="PH-TEST-001")
    
    assert len(result["defects"]) == 0
    assert result["ocr_data"]["cold_chain_flag"] is True
    assert result["overall_vision_confidence"] > 0.90
    assert result["heatmap_base64"] is not None

def test_vision_pipeline_crushed_corner():
    generator = PharmaPackageGenerator()
    img, _ = generator.generate_package(defect_type="CRUSHED_CORNER", zone="15-25°C")
    result = vision_service.process_image(img, order_hint="PH-TEST-002")
    
    defect_types = [d["defect_type"] for d in result["defects"]]
    assert "CRUSHED_CORNER" in defect_types

def test_vision_pipeline_tamper_breach():
    generator = PharmaPackageGenerator()
    img, _ = generator.generate_package(defect_type="TAPE_BREACH", zone="2-8°C")
    result = vision_service.process_image(img, order_hint="PH-TEST-003")
    
    defect_types = [d["defect_type"] for d in result["defects"]]
    assert "TAPE_BREACH" in defect_types
