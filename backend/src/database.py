import sqlite3
from typing import List, Optional
from datetime import datetime
from src.models import User, FaceData, SignTask, SignRecord


class Database:
    """
    数据库操作类
    
    用于管理用户、人脸数据、签到任务和签到记录的SQLite数据库操作
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
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
                    student_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建人脸数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS face_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    face_encoding TEXT NOT NULL,
                    image_path TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # 创建签到任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sign_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'ended')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ended_at DATETIME,
                    FOREIGN KEY (teacher_id) REFERENCES users(id)
                )
            ''')
            
            # 创建签到记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sign_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    confidence REAL,
                    signed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES sign_tasks(id),
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    UNIQUE(task_id, student_id)
                )
            ''')
            
            conn.commit()
    
    # ==================== 用户操作 ====================
    
    def add_user(self, user: User) -> Optional[int]:
        """
        添加用户
        
        Args:
            user: 用户对象
            
        Returns:
            int: 用户ID，失败返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, name, role, student_id) VALUES (?, ?, ?, ?, ?)",
                    (user.username, user.password_hash, user.name, user.role, user.student_id)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加用户失败: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, name, role, student_id, created_at FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        password_hash=row[2],
                        name=row[3],
                        role=row[4],
                        student_id=row[5],
                        created_at=row[6]
                    )
                return None
        except sqlite3.Error as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, name, role, student_id, created_at FROM users WHERE id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        password_hash=row[2],
                        name=row[3],
                        role=row[4],
                        student_id=row[5],
                        created_at=row[6]
                    )
                return None
        except sqlite3.Error as e:
            print(f"获取用户失败: {e}")
            return None
    
    def get_students(self) -> List[User]:
        """
        获取所有学生列表
        
        Returns:
            List[User]: 学生列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, password_hash, name, role, student_id, created_at FROM users WHERE role = 'student'"
                )
                rows = cursor.fetchall()
                students = []
                for row in rows:
                    students.append(User(
                        id=row[0],
                        username=row[1],
                        password_hash=row[2],
                        name=row[3],
                        role=row[4],
                        student_id=row[5],
                        created_at=row[6]
                    ))
                return students
        except sqlite3.Error as e:
            print(f"获取学生列表失败: {e}")
            return []
    
    # ==================== 人脸数据操作 ====================
    
    def add_face_data(self, face_data: FaceData) -> Optional[int]:
        """
        添加人脸数据
        
        Args:
            face_data: 人脸数据对象
            
        Returns:
            int: 记录ID，失败返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 如果已有数据，先删除
                cursor.execute(
                    "DELETE FROM face_data WHERE user_id = ?",
                    (face_data.user_id,)
                )
                cursor.execute(
                    "INSERT INTO face_data (user_id, face_encoding, image_path) VALUES (?, ?, ?)",
                    (face_data.user_id, str(face_data.face_encoding), face_data.image_path)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加人脸数据失败: {e}")
            return None
    
    def get_face_data_by_user_id(self, user_id: int) -> Optional[FaceData]:
        """
        根据用户ID获取人脸数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            FaceData: 人脸数据对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, face_encoding, image_path FROM face_data WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    face_encoding = eval(row[2])
                    return FaceData(
                        id=row[0],
                        user_id=row[1],
                        face_encoding=face_encoding,
                        image_path=row[3]
                    )
                return None
        except sqlite3.Error as e:
            print(f"获取人脸数据失败: {e}")
            return None
    
    def get_all_face_data(self) -> List[FaceData]:
        """
        获取所有人脸数据
        
        Returns:
            List[FaceData]: 人脸数据列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, user_id, face_encoding, image_path FROM face_data"
                )
                rows = cursor.fetchall()
                face_data_list = []
                for row in rows:
                    face_encoding = eval(row[2])
                    face_data_list.append(FaceData(
                        id=row[0],
                        user_id=row[1],
                        face_encoding=face_encoding,
                        image_path=row[3]
                    ))
                return face_data_list
        except sqlite3.Error as e:
            print(f"获取所有人脸数据失败: {e}")
            return []
    
    # ==================== 签到任务操作 ====================
    
    def add_sign_task(self, task: SignTask) -> Optional[int]:
        """
        添加签到任务
        
        Args:
            task: 签到任务对象
            
        Returns:
            int: 任务ID，失败返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sign_tasks (teacher_id, title, status) VALUES (?, ?, ?)",
                    (task.teacher_id, task.title, task.status)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"添加签到任务失败: {e}")
            return None
    
    def get_sign_task_by_id(self, task_id: int) -> Optional[SignTask]:
        """
        根据任务ID获取签到任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            SignTask: 签到任务对象，如果不存在则返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, teacher_id, title, status, created_at, ended_at FROM sign_tasks WHERE id = ?",
                    (task_id,)
                )
                row = cursor.fetchone()
                if row:
                    return SignTask(
                        id=row[0],
                        teacher_id=row[1],
                        title=row[2],
                        status=row[3],
                        created_at=row[4],
                        ended_at=row[5]
                    )
                return None
        except sqlite3.Error as e:
            print(f"获取签到任务失败: {e}")
            return None
    
    def get_active_sign_tasks(self) -> List[SignTask]:
        """
        获取所有进行中的签到任务
        
        Returns:
            List[SignTask]: 签到任务列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, teacher_id, title, status, created_at, ended_at FROM sign_tasks WHERE status = 'active'"
                )
                rows = cursor.fetchall()
                tasks = []
                for row in rows:
                    tasks.append(SignTask(
                        id=row[0],
                        teacher_id=row[1],
                        title=row[2],
                        status=row[3],
                        created_at=row[4],
                        ended_at=row[5]
                    ))
                return tasks
        except sqlite3.Error as e:
            print(f"获取进行中签到任务失败: {e}")
            return []
    
    def get_sign_tasks_by_teacher(self, teacher_id: int) -> List[SignTask]:
        """
        获取老师发布的所有签到任务
        
        Args:
            teacher_id: 老师ID
            
        Returns:
            List[SignTask]: 签到任务列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, teacher_id, title, status, created_at, ended_at FROM sign_tasks WHERE teacher_id = ? ORDER BY created_at DESC",
                    (teacher_id,)
                )
                rows = cursor.fetchall()
                tasks = []
                for row in rows:
                    tasks.append(SignTask(
                        id=row[0],
                        teacher_id=row[1],
                        title=row[2],
                        status=row[3],
                        created_at=row[4],
                        ended_at=row[5]
                    ))
                return tasks
        except sqlite3.Error as e:
            print(f"获取签到任务列表失败: {e}")
            return []
    
    def end_sign_task(self, task_id: int) -> bool:
        """
        结束签到任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 操作是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sign_tasks SET status = 'ended', ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (task_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"结束签到任务失败: {e}")
            return False
    
    # ==================== 签到记录操作 ====================
    
    def add_sign_record(self, record: SignRecord) -> Optional[int]:
        """
        添加签到记录
        
        Args:
            record: 签到记录对象
            
        Returns:
            int: 记录ID，失败返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sign_records (task_id, student_id, confidence) VALUES (?, ?, ?)",
                    (record.task_id, record.student_id, record.confidence)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            print("学生已签到")
            return None
        except sqlite3.Error as e:
            print(f"添加签到记录失败: {e}")
            return None
    
    def get_sign_records_by_task(self, task_id: int) -> List[dict]:
        """
        获取签到任务的所有签到记录
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[dict]: 签到记录列表（包含学生信息）
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT sr.id, sr.task_id, sr.student_id, sr.confidence, sr.signed_at,
                           u.name, u.student_id
                    FROM sign_records sr
                    JOIN users u ON sr.student_id = u.id
                    WHERE sr.task_id = ?
                    ORDER BY sr.signed_at DESC
                ''', (task_id,))
                rows = cursor.fetchall()
                records = []
                for row in rows:
                    records.append({
                        "id": row[0],
                        "task_id": row[1],
                        "student_id": row[2],
                        "confidence": row[3],
                        "signed_at": row[4],
                        "student_name": row[5],
                        "student_number": row[6]
                    })
                return records
        except sqlite3.Error as e:
            print(f"获取签到记录失败: {e}")
            return []
    
    def has_signed(self, task_id: int, student_id: int) -> bool:
        """
        检查学生是否已签到
        
        Args:
            task_id: 任务ID
            student_id: 学生ID
            
        Returns:
            bool: 是否已签到
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM sign_records WHERE task_id = ? AND student_id = ?",
                    (task_id, student_id)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except sqlite3.Error as e:
            print(f"检查签到状态失败: {e}")
            return False
    
    def get_student_sign_count(self, task_id: int) -> int:
        """
        获取签到任务的学生签到数量
        
        Args:
            task_id: 任务ID
            
        Returns:
            int: 签到学生数量
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM sign_records WHERE task_id = ?",
                    (task_id,)
                )
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"获取签到数量失败: {e}")
            return 0