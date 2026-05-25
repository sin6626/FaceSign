import pytest
import tempfile
import os
import numpy as np
from unittest.mock import Mock, patch
from src.face_recognizer import FaceRecognizer

@pytest.fixture
def mock_face_recognition():
    """模拟face_recognition库"""
    with patch('face_recognition.load_image_file') as mock_load:
        with patch('face_recognition.face_encodings') as mock_encodings:
            with patch('face_recognition.face_locations') as mock_locations:
                # 设置模拟返回值
                mock_load.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
                mock_encodings.return_value = [np.random.rand(128)]
                mock_locations.return_value = [(0, 100, 100, 0)]
                
                yield mock_load, mock_encodings, mock_locations

def test_face_recognizer_initialization():
    """测试人脸识别器初始化"""
    recognizer = FaceRecognizer()
    assert recognizer is not None

def test_load_known_faces(mock_face_recognition):
    """测试加载已知人脸"""
    recognizer = FaceRecognizer()
    
    # 创建临时图片文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = f.name
    
    try:
        result = recognizer.load_known_faces(temp_path, "2021001", "张三")
        assert result is True
    finally:
        os.unlink(temp_path)

def test_recognize_face(mock_face_recognition):
    """测试识别人脸"""
    recognizer = FaceRecognizer()
    
    # 创建临时图片文件
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        temp_path = f.name
    
    try:
        recognizer.load_known_faces(temp_path, "2021001", "张三")
        student_id, confidence = recognizer.recognize_face(temp_path)
        assert student_id == "2021001"
        assert confidence >= 0
    finally:
        os.unlink(temp_path)