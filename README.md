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