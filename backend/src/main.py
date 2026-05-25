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