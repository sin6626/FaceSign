from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class User:
    """
    用户模型
    
    Attributes:
        id: 用户ID
        username: 用户名
        password_hash: 密码哈希
        name: 姓名
        role: 角色 (teacher/student)
        student_id: 学号（学生才有）
        created_at: 创建时间
    """
    id: Optional[int] = None
    username: str = ''
    password_hash: str = ''
    name: str = ''
    role: str = ''
    student_id: Optional[str] = None
    created_at: Optional[str] = None
    
    def to_dict(self, include_password: bool = False) -> dict:
        """转换为字典格式"""
        data = {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "role": self.role,
            "student_id": self.student_id,
            "created_at": self.created_at
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data


@dataclass
class FaceData:
    """
    人脸数据模型
    
    Attributes:
        id: 记录ID
        user_id: 关联用户ID
        face_encoding: 人脸编码向量
        image_path: 原始图片路径
    """
    id: Optional[int] = None
    user_id: int = 0
    face_encoding: Optional[List[float]] = None
    image_path: str = ''
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "face_encoding": self.face_encoding,
            "image_path": self.image_path
        }


@dataclass
class SignTask:
    """
    签到任务模型
    
    Attributes:
        id: 任务ID
        teacher_id: 发布老师ID
        title: 签到标题
        status: 状态 (active/ended)
        created_at: 创建时间
        ended_at: 结束时间
    """
    id: Optional[int] = None
    teacher_id: int = 0
    title: str = ''
    status: str = 'active'
    created_at: Optional[str] = None
    ended_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "ended_at": self.ended_at
        }


@dataclass
class SignRecord:
    """
    签到记录模型
    
    Attributes:
        id: 记录ID
        task_id: 签到任务ID
        student_id: 签到学生ID
        confidence: 识别置信度
        signed_at: 签到时间
    """
    id: Optional[int] = None
    task_id: int = 0
    student_id: int = 0
    confidence: float = 0.0
    signed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "student_id": self.student_id,
            "confidence": self.confidence,
            "signed_at": self.signed_at
        }