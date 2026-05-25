"""
人脸识别签到系统 Flask API

提供RESTful接口供前端调用
"""
import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.face_recognizer import FaceRecognizer
from src.database import Database
from src.models import Student, AttendanceRecord

app = Flask(__name__)
CORS(app)

# 初始化组件
db = Database()
recognizer = FaceRecognizer()

# 临时文件上传目录
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok', 'message': '服务运行正常'})


@app.route('/api/students', methods=['POST'])
def add_student():
    """
    添加学生
    
    请求参数:
        - student_id: 学号 (form field)
        - name: 姓名 (form field)
        - image: 人脸图片 (file)
    
    返回:
        - success: bool
        - message: str
    """
    try:
        student_id = request.form.get('student_id')
        name = request.form.get('name')
        image_file = request.files.get('image')
        
        if not student_id or not name or not image_file:
            return jsonify({
                'success': False,
                'message': '缺少必要参数: student_id, name, image'
            }), 400
        
        # 保存临时图片
        filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        
        try:
            # 加载人脸
            success = recognizer.load_known_faces(image_path, student_id, name)
            
            if success:
                # 保存学生信息到数据库
                student = Student(
                    student_id=student_id,
                    name=name,
                    face_encoding=recognizer.known_encodings[student_id].tolist()
                )
                db.add_student(student)
                
                return jsonify({
                    'success': True,
                    'message': f'学生 {name} 添加成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '无法从图片中检测到人脸'
                }), 400
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'添加学生失败: {str(e)}'
        }), 500


@app.route('/api/checkin', methods=['POST'])
def checkin():
    """
    签到接口
    
    请求参数:
        - image: 人脸图片 (file)
    
    返回:
        - success: bool
        - student_id: str (识别成功时)
        - student_name: str (识别成功时)
        - confidence: float (识别成功时)
        - timestamp: str
        - message: str
    """
    try:
        image_file = request.files.get('image')
        
        if not image_file:
            return jsonify({
                'success': False,
                'message': '缺少图片文件'
            }), 400
        
        # 保存临时图片
        filename = f"{uuid.uuid4()}.jpg"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        
        try:
            # 人脸识别
            student_id, confidence = recognizer.recognize_face(image_path)
            
            if student_id:
                student = db.get_student(student_id)
                if student:
                    # 记录签到
                    record = AttendanceRecord(
                        student_id=student_id,
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        status="present"
                    )
                    db.add_attendance(record)
                    
                    return jsonify({
                        'success': True,
                        'student_id': student_id,
                        'student_name': student.name,
                        'confidence': round(confidence, 2),
                        'timestamp': record.timestamp,
                        'message': f'签到成功: {student.name}'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'message': '学生信息不存在'
                    }), 404
            else:
                return jsonify({
                    'success': False,
                    'message': '未识别到已知人脸'
                }), 400
        finally:
            # 清理临时文件
            if os.path.exists(image_path):
                os.remove(image_path)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'签到失败: {str(e)}'
        }), 500


@app.route('/api/records', methods=['GET'])
def get_records():
    """
    获取签到记录
    
    查询参数:
        - date: 日期 (YYYY-MM-DD)，默认今天
    
    返回:
        - date: str
        - records: list
        - total: int
    """
    try:
        date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
        
        records = db.get_attendance_by_date(date)
        
        record_list = []
        for record in records:
            student = db.get_student(record.student_id)
            record_list.append({
                'student_id': record.student_id,
                'student_name': student.name if student else '未知',
                'timestamp': record.timestamp,
                'status': record.status
            })
        
        return jsonify({
            'date': date,
            'records': record_list,
            'total': len(record_list)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取记录失败: {str(e)}'
        }), 500


@app.route('/api/students', methods=['GET'])
def get_students():
    """
    获取所有学生列表
    
    返回:
        - students: list
        - total: int
    """
    try:
        students = db.get_all_students()
        
        students_data = []
        for student in students:
            students_data.append({
                'student_id': student.student_id,
                'name': student.name
            })
        
        return jsonify({
            'students': students_data,
            'total': len(students_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取学生列表失败: {str(e)}'
        }), 500


@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    删除学生
    
    路径参数:
        - student_id: 学号
    
    返回:
        - success: bool
        - message: str
    """
    try:
        success = db.delete_student(student_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'学生 {student_id} 删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'删除学生失败'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除学生失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)