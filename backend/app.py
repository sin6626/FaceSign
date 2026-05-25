"""
人脸识别签到系统 Flask API

提供RESTful接口供前端调用，支持WebSocket实时通知
"""
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room

from src.face_recognizer import FaceRecognizer
from src.database import Database
from src.models import User, FaceData, SignTask, SignRecord

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# 配置
app.config['JWT_SECRET_KEY'] = 'face-sign-secret-key-2026'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# 初始化扩展
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化组件
db = Database()
recognizer = FaceRecognizer()

# 临时文件上传目录
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 在线用户存储
online_users = {}


# ==================== 工具函数 ====================

def load_face_data_to_recognizer():
    """加载所有已知人脸数据到识别器"""
    face_data_list = db.get_all_face_data()
    for face_data in face_data_list:
        user = db.get_user_by_id(face_data.user_id)
        if user and face_data.face_encoding:
            recognizer.known_encodings[str(user.id)] = face_data.face_encoding
            recognizer.known_names[str(user.id)] = user.name


# 初始化时加载人脸数据
load_face_data_to_recognizer()


# ==================== 认证接口 ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """
    用户注册
    
    请求参数:
        - username: 用户名
        - password: 密码
        - name: 姓名
        - role: 角色 (teacher/student)
        - student_id: 学号（学生必填）
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '缺少请求数据'}), 400
        
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role')
        student_id = data.get('student_id')
        
        # 参数验证
        if not all([username, password, name, role]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        if role not in ['teacher', 'student']:
            return jsonify({'success': False, 'message': '角色必须是teacher或student'}), 400
        
        if role == 'student' and not student_id:
            return jsonify({'success': False, 'message': '学生必须提供学号'}), 400
        
        # 检查用户名是否已存在
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建用户
        from werkzeug.security import generate_password_hash
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            role=role,
            student_id=student_id
        )
        
        user_id = db.add_user(user)
        if user_id:
            user.id = user_id
            return jsonify({
                'success': True,
                'message': '注册成功',
                'user': user.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': '注册失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    用户登录
    
    请求参数:
        - username: 用户名
        - password: 密码
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '缺少请求数据'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'success': False, 'message': '缺少用户名或密码'}), 400
        
        # 获取用户
        user = db.get_user_by_username(username)
        if not user:
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 验证密码
        from werkzeug.security import check_password_hash
        if not check_password_hash(user.password_hash, password):
            return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
        
        # 生成JWT Token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': '登录成功',
            'token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500


@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """获取当前用户信息"""
    try:
        user_id = int(get_jwt_identity())
        user = db.get_user_by_id(user_id)
        
        if user:
            return jsonify(user.to_dict())
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500


# ==================== 老师接口 ====================

@app.route('/api/students', methods=['POST'])
@jwt_required()
def add_student():
    """
    添加学生账号（老师权限）
    
    请求参数:
        - username: 用户名
        - password: 密码
        - name: 姓名
        - student_id: 学号
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        student_id = data.get('student_id')
        
        if not all([username, password, name, student_id]):
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        # 检查用户名是否已存在
        existing_user = db.get_user_by_username(username)
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建学生账号
        from werkzeug.security import generate_password_hash
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            name=name,
            role='student',
            student_id=student_id
        )
        
        new_user_id = db.add_user(user)
        if new_user_id:
            user.id = new_user_id
            return jsonify({
                'success': True,
                'message': '学生添加成功',
                'student': user.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': '添加学生失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'添加学生失败: {str(e)}'}), 500


@app.route('/api/students/<int:student_user_id>/face', methods=['POST'])
@jwt_required()
def upload_student_face(student_user_id):
    """
    上传学生人脸照片（老师权限）
    
    路径参数:
        - student_user_id: 学生用户ID
    
    请求: multipart/form-data，包含 image 文件
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        # 检查学生是否存在
        student = db.get_user_by_id(student_user_id)
        if not student or student.role != 'student':
            return jsonify({'success': False, 'message': '学生不存在'}), 404
        
        # 获取上传的图片
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({'success': False, 'message': '缺少图片文件'}), 400
        
        # 保存临时图片
        filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        
        try:
            # 提取人脸编码
            import face_recognition
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                return jsonify({'success': False, 'message': '无法从图片中检测到人脸'}), 400
            
            # 保存人脸数据
            face_data = FaceData(
                user_id=student_user_id,
                face_encoding=face_encodings[0].tolist(),
                image_path=image_path
            )
            
            db.add_face_data(face_data)
            
            # 更新识别器
            recognizer.known_encodings[str(student_user_id)] = face_encodings[0].tolist()
            recognizer.known_names[str(student_user_id)] = student.name
            
            return jsonify({
                'success': True,
                'message': '人脸数据上传成功'
            })
            
        finally:
            # 保留图片用于备份，不删除
            pass
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'上传人脸数据失败: {str(e)}'}), 500


@app.route('/api/students', methods=['GET'])
@jwt_required()
def get_students():
    """
    获取学生列表（老师权限）
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        students = db.get_students()
        
        students_data = []
        for student in students:
            # 检查是否有人脸数据
            face_data = db.get_face_data_by_user_id(student.id) if student.id else None
            students_data.append({
                'id': student.id,
                'username': student.username,
                'name': student.name,
                'student_id': student.student_id,
                'has_face': face_data is not None
            })
        
        return jsonify({
            'students': students_data,
            'total': len(students_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取学生列表失败: {str(e)}'}), 500


@app.route('/api/sign-tasks', methods=['POST'])
@jwt_required()
def create_sign_task():
    """
    创建签到任务（老师权限）
    
    请求参数:
        - title: 签到标题
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'success': False, 'message': '缺少签到标题'}), 400
        
        # 创建签到任务
        task = SignTask(
            teacher_id=user_id,
            title=title,
            status='active'
        )
        
        task_id = db.add_sign_task(task)
        if task_id:
            task.id = task_id
            task.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 通过WebSocket通知所有学生
            socketio.emit('new_sign_task', {
                'task_id': task_id,
                'title': title,
                'teacher_name': current_user.name
            }, namespace='/')
            
            return jsonify({
                'success': True,
                'message': '签到任务创建成功',
                'task': task.to_dict()
            })
        else:
            return jsonify({'success': False, 'message': '创建签到任务失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建签到任务失败: {str(e)}'}), 500


@app.route('/api/sign-tasks/<int:task_id>/end', methods=['PUT'])
@jwt_required()
def end_sign_task(task_id):
    """
    结束签到（老师权限）
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        # 检查任务是否存在
        task = db.get_sign_task_by_id(task_id)
        if not task:
            return jsonify({'success': False, 'message': '签到任务不存在'}), 404
        
        if task.teacher_id != user_id:
            return jsonify({'success': False, 'message': '无权操作此签到任务'}), 403
        
        if task.status == 'ended':
            return jsonify({'success': False, 'message': '签到已结束'}), 400
        
        # 结束签到
        if db.end_sign_task(task_id):
            # 通过WebSocket通知所有学生
            socketio.emit('sign_task_ended', {
                'task_id': task_id,
                'title': task.title
            }, namespace='/')
            
            return jsonify({
                'success': True,
                'message': '签到已结束'
            })
        else:
            return jsonify({'success': False, 'message': '结束签到失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'结束签到失败: {str(e)}'}), 500


@app.route('/api/sign-tasks', methods=['GET'])
@jwt_required()
def get_sign_tasks():
    """
    获取签到任务列表（老师权限）
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        tasks = db.get_sign_tasks_by_teacher(user_id)
        
        tasks_data = []
        total_students = len(db.get_students())
        
        for task in tasks:
            signed_count = db.get_student_sign_count(task.id)
            tasks_data.append({
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'created_at': task.created_at,
                'ended_at': task.ended_at,
                'signed_count': signed_count,
                'total_students': total_students
            })
        
        return jsonify({
            'tasks': tasks_data,
            'total': len(tasks_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取签到任务列表失败: {str(e)}'}), 500


@app.route('/api/sign-tasks/<int:task_id>/records', methods=['GET'])
@jwt_required()
def get_sign_records(task_id):
    """
    获取签到记录（老师权限）
    """
    try:
        # 验证是否是老师
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'teacher':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        # 检查任务是否存在
        task = db.get_sign_task_by_id(task_id)
        if not task:
            return jsonify({'success': False, 'message': '签到任务不存在'}), 404
        
        records = db.get_sign_records_by_task(task_id)
        total_students = len(db.get_students())
        
        return jsonify({
            'task': {
                'id': task.id,
                'title': task.title,
                'status': task.status
            },
            'records': records,
            'total_signed': len(records),
            'total_students': total_students
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取签到记录失败: {str(e)}'}), 500


# ==================== 学生接口 ====================

@app.route('/api/sign-tasks/active', methods=['GET'])
@jwt_required()
def get_active_sign_tasks():
    """
    获取当前进行中的签到（学生权限）
    """
    try:
        tasks = db.get_active_sign_tasks()
        
        if tasks:
            task = tasks[0]  # 返回最新的一个
            teacher = db.get_user_by_id(task.teacher_id)
            return jsonify({
                'has_active': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'teacher_name': teacher.name if teacher else '未知',
                    'created_at': task.created_at
                }
            })
        else:
            return jsonify({
                'has_active': False,
                'task': None
            })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取签到信息失败: {str(e)}'}), 500


@app.route('/api/sign-tasks/<int:task_id>/sign', methods=['POST'])
@jwt_required()
def sign_task(task_id):
    """
    人脸签到（学生权限）
    
    请求: multipart/form-data，包含 image 文件
    """
    try:
        # 验证是否是学生
        user_id = int(get_jwt_identity())
        current_user = db.get_user_by_id(user_id)
        if not current_user or current_user.role != 'student':
            return jsonify({'success': False, 'message': '无权限'}), 403
        
        # 检查任务是否存在
        task = db.get_sign_task_by_id(task_id)
        if not task:
            return jsonify({'success': False, 'message': '签到任务不存在'}), 404
        
        if task.status != 'active':
            return jsonify({'success': False, 'message': '签到已结束'}), 400
        
        # 检查是否已签到
        if db.has_signed(task_id, user_id):
            return jsonify({'success': False, 'message': '您已签到'}), 400
        
        # 获取上传的图片
        image_file = request.files.get('image')
        if not image_file:
            return jsonify({'success': False, 'message': '缺少图片文件'}), 400
        
        # 保存临时图片
        filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        
        try:
            # 人脸识别
            student_id_str, confidence = recognizer.recognize_face(image_path)
            
            if student_id_str and int(student_id_str) == user_id:
                # 签到成功
                record = SignRecord(
                    task_id=task_id,
                    student_id=user_id,
                    confidence=confidence
                )
                
                record_id = db.add_sign_record(record)
                if record_id:
                    # 通过WebSocket通知老师
                    socketio.emit('student_signed', {
                        'task_id': task_id,
                        'student_id': current_user.student_id,
                        'student_name': current_user.name,
                        'confidence': round(confidence, 2)
                    }, namespace='/')
                    
                    return jsonify({
                        'success': True,
                        'message': '签到成功',
                        'confidence': round(confidence, 2),
                        'signed_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    return jsonify({'success': False, 'message': '签到失败'}), 500
            else:
                return jsonify({'success': False, 'message': '人脸识别失败，请确保是本人'}), 400
                
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'签到失败: {str(e)}'}), 500


# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


# ==================== WebSocket事件 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    print('客户端已连接')


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开"""
    print('客户端已断开')


@socketio.on('join')
def handle_join(data):
    """加入房间"""
    room = data.get('room', 'default')
    join_room(room)
    print(f'用户加入房间: {room}')


@socketio.on('leave')
def handle_leave(data):
    """离开房间"""
    room = data.get('room', 'default')
    leave_room(room)
    print(f'用户离开房间: {room}')


# ==================== 启动应用 ====================

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)