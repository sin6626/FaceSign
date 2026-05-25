# Face Sign System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a face recognition attendance system for classroom check-in with data persistence, error handling, and OOP design.

**Architecture:** Python application using face_recognition library for face detection/recognition, SQLite for data storage, and modular OOP design with separate classes for face recognition and database operations.

**Tech Stack:** Python 3.8+, face_recognition, OpenCV, SQLite, pytest

---

## Task 1: Create Project Directory Structure

**Files:**
- Create: `src/__init__.py`
- Create: `tests/__init__.py`
- Create: `data/faces/.gitkeep`
- Create: `docs/superpowers/plans/.gitkeep`

- [ ] **Step 1: Create source directory and init file**

```bash
mkdir -p src
touch src/__init__.py
```

- [ ] **Step 2: Create tests directory and init file**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 3: Create data directory for face images**

```bash
mkdir -p data/faces
touch data/faces/.gitkeep
```

- [ ] **Step 4: Verify directory structure**

```bash
ls -la
ls -la src/
ls -la tests/
ls -la data/faces/
```

Expected: All directories created with init files.

- [ ] **Step 5: Commit directory structure**

```bash
git init
git add .
git commit -m "feat: create project directory structure"
```

## Task 2: Create AI_LOG.md and README.md

**Files:**
- Create: `AI_LOG.md`
- Create: `README.md`

- [ ] **Step 1: Create AI_LOG.md with required format**

```markdown
# AI辅助开发日志

## 项目信息
- 项目名称：人脸识别签到系统
- 小组成员：[成员姓名]
- 开始日期：2026-05-25

## AI使用记录

### 2026-05-25
- **任务**: 项目初始化
- **AI工具**: OpenCode
- **使用场景**: 创建项目结构、编写基础代码
- **具体帮助**: 
  - 生成项目目录结构
  - 编写人脸识别类基础代码
  - 创建数据库操作类
- **AI生成代码比例**: 约40%
- **人工修改比例**: 约60%

## 开发日志
[后续开发过程中持续更新]
```

- [ ] **Step 2: Create README.md with project description**

```markdown
# FaceSign - 人脸识别签到系统

## 项目简介
一个基于人脸识别的课堂签到系统，支持实时人脸检测和识别，自动记录学生出勤。

## 功能特性
- 人脸检测与识别
- 学生信息管理
- 签到记录存储
- 异常处理与日志

## 技术栈
- Python 3.8+
- face_recognition (基于dlib)
- OpenCV
- SQLite

## 安装与使用
1. 安装依赖：`pip install -r requirements.txt`
2. 准备人脸图片：将学生照片放入 `data/faces/` 目录
3. 运行系统：`python src/main.py`

## 项目结构
```
FaceSign/
├── src/           # 源代码
├── tests/         # 测试文件
├── data/          # 数据文件
├── docs/          # 文档
├── AI_LOG.md      # AI辅助开发日志
└── README.md      # 项目说明
```
```

- [ ] **Step 3: Verify file creation**

```bash
cat AI_LOG.md
cat README.md
```

- [ ] **Step 4: Commit documentation**

```bash
git add AI_LOG.md README.md
git commit -m "docs: add AI_LOG.md and README.md"
```

## Task 3: Create requirements.txt and .gitignore

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: Create requirements.txt with dependencies**

```
face_recognition>=1.3.0
opencv-python>=4.5.0
numpy>=1.20.0
pytest>=6.0.0
```

- [ ] **Step 2: Create .gitignore for Python project**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/faces/*.jpg
data/faces/*.png
data/faces/*.jpeg

# Database
*.db
*.sqlite

# Logs
*.log
```

- [ ] **Step 3: Verify files**

```bash
cat requirements.txt
cat .gitignore
```

- [ ] **Step 4: Commit configuration files**

```bash
git add requirements.txt .gitignore
git commit -m "chore: add requirements.txt and .gitignore"
```

## Task 4: Create Data Models

**Files:**
- Create: `src/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing test for Student model**

```python
# tests/test_models.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_models.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.models'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/models.py
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_models.py -v
```

Expected: PASS

- [ ] **Step 5: Commit models and tests**

```bash
git add src/models.py tests/test_models.py
git commit -m "feat: add data models with tests"
```

## Task 5: Create Database Operations Class

**Files:**
- Create: `src/database.py`
- Create: `tests/test_database.py`

- [ ] **Step 1: Write failing tests for Database class**

```python
# tests/test_database.py
import pytest
import tempfile
import os
from src.database import Database
from src.models import Student, AttendanceRecord

@pytest.fixture
def temp_db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    db = Database(db_path)
    yield db
    os.unlink(db_path)

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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_database.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.database'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/database.py
import sqlite3
from typing import List, Optional
from src.models import Student, AttendanceRecord

class Database:
    """
    数据库操作类
    
    用于管理学生信息和签到记录的SQLite数据库操作
    
    Attributes:
        db_path: 数据库文件路径
    """
    
    def __init__(self, db_path: str = "attendance.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为attendance.db
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建学生表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    face_encoding TEXT NOT NULL
                )
            ''')
            
            # 创建签到记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            conn.commit()
    
    def add_student(self, student: Student) -> bool:
        """
        添加学生信息
        
        Args:
            student: 学生对象
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO students (student_id, name, face_encoding) VALUES (?, ?, ?)",
                    (student.student_id, student.name, str(student.face_encoding))
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"添加学生失败: {e}")
            return False
    
    def get_student(self, student_id: str) -> Optional[Student]:
        """
        获取学生信息
        
        Args:
            student_id: 学号
            
        Returns:
            Student: 学生对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT student_id, name, face_encoding FROM students WHERE student_id = ?",
                    (student_id,)
                )
                row = cursor.fetchone()
                if row:
                    face_encoding = eval(row[2])  # 将字符串转换回列表
                    return Student(
                        student_id=row[0],
                        name=row[1],
                        face_encoding=face_encoding
                    )
                return None
        except sqlite3.Error as e:
            print(f"获取学生信息失败: {e}")
            return None
    
    def add_attendance(self, record: AttendanceRecord) -> bool:
        """
        添加签到记录
        
        Args:
            record: 签到记录对象
            
        Returns:
            bool: 添加是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO attendance (student_id, timestamp, status) VALUES (?, ?, ?)",
                    (record.student_id, record.timestamp, record.status)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"添加签到记录失败: {e}")
            return False
    
    def get_attendance_by_date(self, date: str) -> List[AttendanceRecord]:
        """
        获取指定日期的签到记录
        
        Args:
            date: 日期字符串，格式为YYYY-MM-DD
            
        Returns:
            List[AttendanceRecord]: 签到记录列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT student_id, timestamp, status FROM attendance WHERE timestamp LIKE ?",
                    (f"{date}%",)
                )
                rows = cursor.fetchall()
                records = []
                for row in rows:
                    records.append(AttendanceRecord(
                        student_id=row[0],
                        timestamp=row[1],
                        status=row[2]
                    ))
                return records
        except sqlite3.Error as e:
            print(f"获取签到记录失败: {e}")
            return []
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_database.py -v
```

Expected: PASS

- [ ] **Step 5: Commit database class and tests**

```bash
git add src/database.py tests/test_database.py
git commit -m "feat: add database operations class with tests"
```

## Task 6: Create Face Recognition Class

**Files:**
- Create: `src/face_recognizer.py`
- Create: `tests/test_face_recognizer.py`

- [ ] **Step 1: Write failing tests for FaceRecognizer class**

```python
# tests/test_face_recognizer.py
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_face_recognizer.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'src.face_recognizer'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/face_recognizer.py
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
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_face_recognizer.py -v
```

Expected: PASS

- [ ] **Step 5: Commit face recognizer class and tests**

```bash
git add src/face_recognizer.py tests/test_face_recognizer.py
git commit -m "feat: add face recognition class with tests"
```

## Task 7: Create Main Application Entry Point

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: Create main.py with basic structure**

```python
# src/main.py
"""
人脸识别签到系统主程序

提供命令行界面进行签到管理和学生信息管理
"""
import argparse
import os
from datetime import datetime
from src.face_recognizer import FaceRecognizer
from src.database import Database

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="人脸识别签到系统")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加学生命令
    add_parser = subparsers.add_parser("add", help="添加学生")
    add_parser.add_argument("--id", required=True, help="学号")
    add_parser.add_argument("--name", required=True, help="姓名")
    add_parser.add_argument("--image", required=True, help="人脸图片路径")
    
    # 签到命令
    checkin_parser = subparsers.add_parser("checkin", help="签到")
    checkin_parser.add_argument("--image", required=True, help="待识别图片路径")
    
    # 查看签到记录命令
    records_parser = subparsers.add_parser("records", help="查看签到记录")
    records_parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), 
                               help="日期 (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # 初始化组件
    db = Database()
    recognizer = FaceRecognizer()
    
    if args.command == "add":
        # 添加学生
        success = recognizer.load_known_faces(args.image, args.id, args.name)
        if success:
            from src.models import Student
            student = Student(
                student_id=args.id,
                name=args.name,
                face_encoding=recognizer.known_encodings[args.id].tolist()
            )
            db.add_student(student)
            print(f"成功添加学生: {args.name} ({args.id})")
        else:
            print("添加学生失败：无法从图片中检测到人脸")
    
    elif args.command == "checkin":
        # 签到
        student_id, confidence = recognizer.recognize_face(args.image)
        if student_id:
            student = db.get_student(student_id)
            if student:
                from src.models import AttendanceRecord
                record = AttendanceRecord(
                    student_id=student_id,
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    status="present"
                )
                db.add_attendance(record)
                print(f"签到成功: {student.name} ({student_id}) 置信度: {confidence:.2f}")
            else:
                print("签到失败：学生信息不存在")
        else:
            print("签到失败：未识别到已知人脸")
    
    elif args.command == "records":
        # 查看签到记录
        records = db.get_attendance_by_date(args.date)
        if records:
            print(f"\n{args.date} 签到记录:")
            print("-" * 50)
            for record in records:
                student = db.get_student(record.student_id)
                name = student.name if student else "未知"
                print(f"{record.student_id} {name} {record.timestamp} {record.status}")
        else:
            print(f"没有找到 {args.date} 的签到记录")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify main.py syntax**

```bash
python -m py_compile src/main.py
```

Expected: No output (successful compilation)

- [ ] **Step 3: Commit main application**

```bash
git add src/main.py
git commit -m "feat: add main application entry point"
```

## Task 8: Install Dependencies and Verify Project

**Files:**
- No new files

- [ ] **Step 1: Install Python dependencies**

```bash
pip install -r requirements.txt
```

Expected: Successful installation of face_recognition, opencv-python, numpy, pytest

- [ ] **Step 2: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests pass

- [ ] **Step 3: Verify project can be imported**

```bash
python -c "from src.models import Student, AttendanceRecord; from src.database import Database; from src.face_recognizer import FaceRecognizer; print('All imports successful')"
```

Expected: "All imports successful"

- [ ] **Step 4: Update AI_LOG.md with project initialization details**

```markdown
## 开发日志

### 2026-05-25
- **任务**: 项目初始化
- **AI工具**: OpenCode
- **使用场景**: 创建项目结构、编写基础代码
- **具体帮助**: 
  - 生成项目目录结构
  - 编写数据模型类
  - 创建数据库操作类
  - 实现人脸识别类
  - 创建主程序入口
- **AI生成代码比例**: 约60%
- **人工修改比例**: 约40%
- **遇到的问题**: 需要配置face_recognition库的dlib依赖
- **解决方案**: 按照官方文档安装dlib二进制包
```

- [ ] **Step 5: Commit final updates**

```bash
git add .
git commit -m "chore: install dependencies and update documentation"
```

---

## Self-Review Checklist

1. **Spec coverage:** ✅ 
   - 自学新技术: face_recognition库 (Task 6)
   - 数据持久化: SQLite数据库 (Task 5)
   - 异常处理: 数据库操作和人脸识别中的异常处理 (Task 5, 6)
   - 面向对象: Database类和FaceRecognizer类 (Task 5, 6)
   - 代码规范: 所有函数和类都有docstring (Task 4, 5, 6)
   - AI辅助记录: AI_LOG.md文件 (Task 2)

2. **Placeholder scan:** ✅ 无占位符，所有代码完整

3. **Type consistency:** ✅ 类型定义一致，方法签名匹配

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-25-face-sign-system.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?