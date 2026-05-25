# 人脸识别签到系统设计文档

## 项目概述

类似学习通的课堂签到系统，支持老师发布人脸签到任务，学生实时接收通知并进行人脸签到。

## 技术栈

- **后端**: Flask + Flask-SocketIO + SQLite
- **通信**: REST API + WebSocket
- **人脸识别**: face_recognition

## 数据库设计

### users 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 自增ID |
| username | TEXT UNIQUE | 用户名 |
| password_hash | TEXT | 密码哈希 |
| name | TEXT | 姓名 |
| role | TEXT | 角色: teacher/student |
| student_id | TEXT | 学号（学生才有） |
| created_at | DATETIME | 创建时间 |

### face_data 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 自增ID |
| user_id | INTEGER | 关联用户ID |
| face_encoding | TEXT | 人脸编码（JSON） |
| image_path | TEXT | 原始图片路径 |

### sign_tasks 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 自增ID |
| teacher_id | INTEGER | 发布老师ID |
| title | TEXT | 签到标题 |
| status | TEXT | active/ended |
| created_at | DATETIME | 创建时间 |
| ended_at | DATETIME | 结束时间 |

### sign_records 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PRIMARY KEY | 自增ID |
| task_id | INTEGER | 签到任务ID |
| student_id | INTEGER | 签到学生ID |
| confidence | REAL | 识别置信度 |
| signed_at | DATETIME | 签到时间 |

## 接口设计

### 认证接口

#### POST /api/auth/register

注册新用户

**请求参数:**
```json
{
    "username": "string",
    "password": "string",
    "name": "string",
    "role": "teacher|student",
    "student_id": "string"  // 学生必填
}
```

**响应:**
```json
{
    "success": true,
    "message": "注册成功",
    "user": {
        "id": 1,
        "username": "zhangsan",
        "name": "张三",
        "role": "student"
    }
}
```

#### POST /api/auth/login

用户登录

**请求参数:**
```json
{
    "username": "string",
    "password": "string"
}
```

**响应:**
```json
{
    "success": true,
    "token": "jwt_token_string",
    "user": {
        "id": 1,
        "username": "zhangsan",
        "name": "张三",
        "role": "student"
    }
}
```

#### GET /api/auth/me

获取当前用户信息（需要Token）

**响应:**
```json
{
    "id": 1,
    "username": "zhangsan",
    "name": "张三",
    "role": "student",
    "student_id": "2021001"
}
```

### 老师接口

#### POST /api/students

添加学生账号（老师权限）

**请求参数:**
```json
{
    "username": "string",
    "password": "string",
    "name": "string",
    "student_id": "string"
}
```

**响应:**
```json
{
    "success": true,
    "message": "学生添加成功",
    "student": {
        "id": 2,
        "username": "zhangsan",
        "name": "张三",
        "student_id": "2021001"
    }
}
```

#### POST /api/students/{id}/face

上传学生人脸照片（老师权限）

**请求:** multipart/form-data，包含 image 文件

**响应:**
```json
{
    "success": true,
    "message": "人脸数据上传成功"
}
```

#### GET /api/students

获取学生列表（老师权限）

**响应:**
```json
{
    "students": [
        {
            "id": 2,
            "username": "zhangsan",
            "name": "张三",
            "student_id": "2021001",
            "has_face": true
        }
    ],
    "total": 1
}
```

#### POST /api/sign-tasks

创建签到任务（老师权限）

**请求参数:**
```json
{
    "title": "第一节人脸签到"
}
```

**响应:**
```json
{
    "success": true,
    "message": "签到任务创建成功",
    "task": {
        "id": 1,
        "title": "第一节人脸签到",
        "status": "active",
        "created_at": "2026-05-25 10:00:00"
    }
}
```

#### PUT /api/sign-tasks/{id}/end

结束签到（老师权限）

**响应:**
```json
{
    "success": true,
    "message": "签到已结束"
}
```

#### GET /api/sign-tasks

查看签到任务列表（老师权限）

**响应:**
```json
{
    "tasks": [
        {
            "id": 1,
            "title": "第一节人脸签到",
            "status": "ended",
            "created_at": "2026-05-25 10:00:00",
            "ended_at": "2026-05-25 10:05:00",
            "signed_count": 25,
            "total_students": 30
        }
    ],
    "total": 1
}
```

#### GET /api/sign-tasks/{id}/records

查看某次签到记录（老师权限）

**响应:**
```json
{
    "task": {
        "id": 1,
        "title": "第一节人脸签到",
        "status": "ended"
    },
    "records": [
        {
            "student_id": "2021001",
            "student_name": "张三",
            "confidence": 0.95,
            "signed_at": "2026-05-25 10:01:30"
        }
    ],
    "total_signed": 25,
    "total_students": 30
}
```

### 学生接口

#### GET /api/sign-tasks/active

获取当前进行中的签到（学生权限）

**响应:**
```json
{
    "has_active": true,
    "task": {
        "id": 1,
        "title": "第一节人脸签到",
        "teacher_name": "李老师",
        "created_at": "2026-05-25 10:00:00"
    }
}
```

#### POST /api/sign-tasks/{id}/sign

人脸签到（学生权限）

**请求:** multipart/form-data，包含 image 文件

**响应:**
```json
{
    "success": true,
    "message": "签到成功",
    "confidence": 0.95,
    "signed_at": "2026-05-25 10:01:30"
}
```

### WebSocket 接口

连接地址: `ws://localhost:5000/ws`

#### 事件类型

**1. 老师创建签到 → 推送给所有学生**
```json
{
    "event": "new_sign_task",
    "data": {
        "task_id": 1,
        "title": "第一节人脸签到",
        "teacher_name": "李老师"
    }
}
```

**2. 学生签到成功 → 推送给老师**
```json
{
    "event": "student_signed",
    "data": {
        "task_id": 1,
        "student_id": "2021001",
        "student_name": "张三",
        "confidence": 0.95
    }
}
```

**3. 老师结束签到 → 推送给所有学生**
```json
{
    "event": "sign_task_ended",
    "data": {
        "task_id": 1,
        "title": "第一节人脸签到"
    }
}
```

## 错误响应格式

所有接口错误响应格式统一:
```json
{
    "success": false,
    "message": "错误信息"
}
```

常见HTTP状态码:
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器内部错误

## 项目结构

```
backend/
├── app.py                 # Flask应用入口
├── src/
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   ├── database.py        # 数据库操作
│   ├── auth.py            # 认证相关
│   ├── face_recognizer.py # 人脸识别
│   └── websocket.py       # WebSocket处理
├── tests/
├── docs/
│   └── API.md             # 接口文档
└── requirements.txt
```