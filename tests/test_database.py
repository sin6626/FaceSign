import pytest
import tempfile
import os
from src.database import Database
from src.models import Student, AttendanceRecord

@pytest.fixture
def temp_db():
    """创建临时数据库"""
    import tempfile
    import os
    import sqlite3
    
    # 创建临时文件
    temp_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    db = Database(db_path)
    yield db
    
    # 清理：关闭所有连接并删除文件
    try:
        # 尝试删除文件
        if os.path.exists(db_path):
            os.unlink(db_path)
    except PermissionError:
        # 如果文件被占用，忽略错误
        pass

def test_database_initialization(temp_db):
    """测试数据库初始化"""
    assert temp_db is not None

def test_add_student(temp_db):
    """测试添加学生"""
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    result = temp_db.add_student(student)
    assert result is True

def test_get_student(temp_db):
    """测试获取学生信息"""
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    temp_db.add_student(student)
    retrieved = temp_db.get_student("2021001")
    assert retrieved is not None
    assert retrieved.name == "张三"

def test_add_attendance(temp_db):
    """测试添加签到记录"""
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    temp_db.add_student(student)
    
    record = AttendanceRecord(
        student_id="2021001",
        timestamp="2026-05-25 10:00:00",
        status="present"
    )
    result = temp_db.add_attendance(record)
    assert result is True

def test_get_attendance_by_date(temp_db):
    """测试按日期获取签到记录"""
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    temp_db.add_student(student)
    
    record = AttendanceRecord(
        student_id="2021001",
        timestamp="2026-05-25 10:00:00",
        status="present"
    )
    temp_db.add_attendance(record)
    
    records = temp_db.get_attendance_by_date("2026-05-25")
    assert len(records) == 1
    assert records[0].student_id == "2021001"