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
    
    def get_all_students(self) -> List[Student]:
        """
        获取所有学生信息
        
        Returns:
            List[Student]: 学生列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT student_id, name, face_encoding FROM students"
                )
                rows = cursor.fetchall()
                students = []
                for row in rows:
                    face_encoding = eval(row[2])
                    students.append(Student(
                        student_id=row[0],
                        name=row[1],
                        face_encoding=face_encoding
                    ))
                return students
        except sqlite3.Error as e:
            print(f"获取学生列表失败: {e}")
            return []
    
    def delete_student(self, student_id: str) -> bool:
        """
        删除学生信息
        
        Args:
            student_id: 学号
            
        Returns:
            bool: 删除是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 先删除签到记录
                cursor.execute(
                    "DELETE FROM attendance WHERE student_id = ?",
                    (student_id,)
                )
                # 再删除学生
                cursor.execute(
                    "DELETE FROM students WHERE student_id = ?",
                    (student_id,)
                )
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"删除学生失败: {e}")
            return False