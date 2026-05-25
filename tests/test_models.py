import pytest
from src.models import Student, AttendanceRecord

def test_student_creation():
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    assert student.student_id == "2021001"
    assert student.name == "张三"
    assert len(student.face_encoding) == 3

def test_student_to_dict():
    student = Student(
        student_id="2021001",
        name="张三",
        face_encoding=[0.1, 0.2, 0.3]
    )
    data = student.to_dict()
    assert data["student_id"] == "2021001"
    assert data["name"] == "张三"

def test_attendance_record_creation():
    record = AttendanceRecord(
        student_id="2021001",
        timestamp="2026-05-25 10:00:00",
        status="present"
    )
    assert record.student_id == "2021001"
    assert record.status == "present"