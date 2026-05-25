from dataclasses import dataclass
from typing import List
import json

@dataclass
class Student:
    """
    学生信息模型
    
    Attributes:
        student_id: 学号
        name: 姓名
        face_encoding: 人脸编码向量
    """
    student_id: str
    name: str
    face_encoding: List[float]
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "face_encoding": self.face_encoding
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Student':
        """从字典创建Student对象"""
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            face_encoding=data["face_encoding"]
        )

@dataclass
class AttendanceRecord:
    """
    签到记录模型
    
    Attributes:
        student_id: 学号
        timestamp: 签到时间
        status: 签到状态 (present/absent/late)
    """
    student_id: str
    timestamp: str
    status: str
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "student_id": self.student_id,
            "timestamp": self.timestamp,
            "status": self.status
        }