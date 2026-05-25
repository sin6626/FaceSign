import face_recognition
import numpy as np
from typing import Tuple, Optional, Dict, List
import os

class FaceRecognizer:
    """
    人脸识别类
    
    使用face_recognition库进行人脸检测和识别
    
    Attributes:
        known_encodings: 已知人脸编码字典 {student_id: encoding}
        known_names: 已知人脸姓名字典 {student_id: name}
        tolerance: 识别容差值，默认0.6
    """
    
    def __init__(self, tolerance: float = 0.6):
        """
        初始化人脸识别器
        
        Args:
            tolerance: 识别容差值，值越小越严格，默认0.6
        """
        self.known_encodings: Dict[str, np.ndarray] = {}
        self.known_names: Dict[str, str] = {}
        self.tolerance = tolerance
    
    def load_known_faces(self, image_path: str, student_id: str, name: str) -> bool:
        """
        加载已知人脸
        
        Args:
            image_path: 图片路径
            student_id: 学号
            name: 姓名
            
        Returns:
            bool: 加载是否成功
        """
        try:
            # 加载图片
            image = face_recognition.load_image_file(image_path)
            
            # 检测人脸位置
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print(f"未检测到人脸: {image_path}")
                return False
            
            # 获取人脸编码
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                print(f"无法获取人脸编码: {image_path}")
                return False
            
            # 使用第一张检测到的人脸
            self.known_encodings[student_id] = face_encodings[0]
            self.known_names[student_id] = name
            
            return True
            
        except Exception as e:
            print(f"加载人脸失败: {e}")
            return False
    
    def recognize_face(self, image_path: str) -> Tuple[Optional[str], float]:
        """
        识别人脸
        
        Args:
            image_path: 待识别图片路径
            
        Returns:
            Tuple[Optional[str], float]: (学号, 置信度)，如果未识别到则返回(None, 0.0)
        """
        try:
            # 加载图片
            image = face_recognition.load_image_file(image_path)
            
            # 检测人脸位置
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                return None, 0.0
            
            # 获取人脸编码
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                return None, 0.0
            
            # 比较已知人脸
            for face_encoding in face_encodings:
                for student_id, known_encoding in self.known_encodings.items():
                    # 计算人脸距离
                    face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                    
                    # 如果距离小于容差值，认为匹配
                    if face_distance <= self.tolerance:
                        confidence = 1.0 - face_distance
                        return student_id, confidence
            
            return None, 0.0
            
        except Exception as e:
            print(f"人脸识别失败: {e}")
            return None, 0.0
    
    def get_all_students(self) -> List[Tuple[str, str]]:
        """
        获取所有已加载的学生信息
        
        Returns:
            List[Tuple[str, str]]: [(学号, 姓名), ...]
        """
        return [(sid, name) for sid, name in self.known_names.items()]