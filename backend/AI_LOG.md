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

### 2026-05-25
- **任务**: 项目初始化
- **AI工具**: OpenCode
- **使用场景**: 创建项目结构、编写基础代码
- **具体帮助**: 
  - 生成项目目录结构
  - 编写数据模型类 (Student, AttendanceRecord)
  - 创建数据库操作类 (Database)
  - 实现人脸识别类 (FaceRecognizer)
  - 创建主程序入口 (main.py)
- **AI生成代码比例**: 约60%
- **人工修改比例**: 约40%
- **遇到的问题**: 
  1. face_recognition库依赖dlib，在Windows上编译失败
  2. 临时数据库文件删除时出现权限错误
- **解决方案**: 
  1. 暂时跳过face_recognition安装，后续使用预编译版本或替代方案
  2. 修改测试fixture，处理文件权限问题
- **完成的工作**:
  1. 创建完整的项目目录结构
  2. 编写符合要求的AI_LOG.md文件
  3. 实现数据模型、数据库操作、人脸识别等核心模块
  4. 编写完整的单元测试
  5. 初始化Git仓库并提交所有代码

### 2026-05-25（下午）
- **任务**: 系统重构 - 实现完整签到系统
- **AI工具**: OpenCode
- **使用场景**: 设计系统架构、实现完整后端API
- **具体帮助**: 
  - 设计数据库结构（users, face_data, sign_tasks, sign_records）
  - 设计RESTful API接口
  - 实现JWT认证系统
  - 实现WebSocket实时通知
  - 编写API接口文档
- **AI生成代码比例**: 约90%
- **人工修改比例**: 约10%
- **遇到的问题**: 
  1. Python 3.13中pkg_resources模块缺失
  2. setuptools版本过高导致兼容性问题
- **解决方案**: 
  1. 降级setuptools到69.x版本
  2. 使用环境变量解决dlib编译编码问题
- **完成的工作**:
  1. 重构数据模型（User, FaceData, SignTask, SignRecord）
  2. 重写数据库操作类，支持用户、人脸、签到任务、签到记录
  3. 实现JWT认证系统（登录、注册、权限验证）
  4. 实现老师功能（添加学生、上传人脸、创建签到、查看记录）
  5. 实现学生功能（查看签到、人脸签到）
  6. 实现WebSocket实时通知
  7. 编写完整的API接口文档
- **接口清单**:
  - POST /api/auth/register - 用户注册
  - POST /api/auth/login - 用户登录
  - GET /api/auth/me - 获取当前用户
  - POST /api/students - 添加学生
  - POST /api/students/{id}/face - 上传人脸
  - GET /api/students - 获取学生列表
  - POST /api/sign-tasks - 创建签到任务
  - PUT /api/sign-tasks/{id}/end - 结束签到
  - GET /api/sign-tasks - 获取签到列表
  - GET /api/sign-tasks/{id}/records - 获取签到记录
  - GET /api/sign-tasks/active - 获取进行中签到
  - POST /api/sign-tasks/{id}/sign - 人脸签到
  - WebSocket: new_sign_task, student_signed, sign_task_ended