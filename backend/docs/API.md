# 人脸识别签到系统 API 接口文档

## 基础信息

- 基础URL: `http://localhost:5000`
- WebSocket: `ws://localhost:5000`
- 认证方式: JWT Bearer Token
- Content-Type: application/json (除文件上传外)

## 认证说明

除登录注册外，所有接口需要在请求头中携带Token：

```
Authorization: Bearer <your_token>
```

---

## 一、认证接口

### 1.1 用户注册

**POST** `/api/auth/register`

请求参数：
```json
{
    "username": "zhangsan",
    "password": "123456",
    "name": "张三",
    "role": "student",
    "student_id": "2021001"
}
```

成功响应：
```json
{
    "success": true,
    "message": "注册成功",
    "user": {
        "id": 1,
        "username": "zhangsan",
        "name": "张三",
        "role": "student",
        "student_id": "2021001",
        "created_at": "2026-05-25 10:00:00"
    }
}
```

### 1.2 用户登录

**POST** `/api/auth/login`

请求参数：
```json
{
    "username": "zhangsan",
    "password": "123456"
}
```

成功响应：
```json
{
    "success": true,
    "message": "登录成功",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "zhangsan",
        "name": "张三",
        "role": "student",
        "student_id": "2021001"
    }
}
```

### 1.3 获取当前用户信息

**GET** `/api/auth/me`

需要认证：是

成功响应：
```json
{
    "id": 1,
    "username": "zhangsan",
    "name": "张三",
    "role": "student",
    "student_id": "2021001",
    "created_at": "2026-05-25 10:00:00"
}
```

---

## 二、老师接口

### 2.1 添加学生账号

**POST** `/api/students`

需要认证：是（老师角色）

请求参数：
```json
{
    "username": "lisi",
    "password": "123456",
    "name": "李四",
    "student_id": "2021002"
}
```

成功响应：
```json
{
    "success": true,
    "message": "学生添加成功",
    "student": {
        "id": 2,
        "username": "lisi",
        "name": "李四",
        "role": "student",
        "student_id": "2021002"
    }
}
```

### 2.2 上传学生人脸照片

**POST** `/api/students/{student_user_id}/face`

需要认证：是（老师角色）

请求：`multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | 是 | 学生人脸照片 |

成功响应：
```json
{
    "success": true,
    "message": "人脸数据上传成功"
}
```

### 2.3 获取学生列表

**GET** `/api/students`

需要认证：是（老师角色）

成功响应：
```json
{
    "students": [
        {
            "id": 2,
            "username": "lisi",
            "name": "李四",
            "student_id": "2021002",
            "has_face": true
        }
    ],
    "total": 1
}
```

### 2.4 创建签到任务

**POST** `/api/sign-tasks`

需要认证：是（老师角色）

请求参数：
```json
{
    "title": "第一节人脸签到"
}
```

成功响应：
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

### 2.5 结束签到

**PUT** `/api/sign-tasks/{task_id}/end`

需要认证：是（老师角色）

成功响应：
```json
{
    "success": true,
    "message": "签到已结束"
}
```

### 2.6 获取签到任务列表

**GET** `/api/sign-tasks`

需要认证：是（老师角色）

成功响应：
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

### 2.7 获取签到记录

**GET** `/api/sign-tasks/{task_id}/records`

需要认证：是（老师角色）

成功响应：
```json
{
    "task": {
        "id": 1,
        "title": "第一节人脸签到",
        "status": "ended"
    },
    "records": [
        {
            "id": 1,
            "task_id": 1,
            "student_id": 2,
            "confidence": 0.95,
            "signed_at": "2026-05-25 10:01:30",
            "student_name": "李四",
            "student_number": "2021002"
        }
    ],
    "total_signed": 25,
    "total_students": 30
}
```

---

## 三、学生接口

### 3.1 获取当前进行中的签到

**GET** `/api/sign-tasks/active`

需要认证：是

成功响应（有签到任务）：
```json
{
    "has_active": true,
    "task": {
        "id": 1,
        "title": "第一节人脸签到",
        "teacher_name": "王老师",
        "created_at": "2026-05-25 10:00:00"
    }
}
```

成功响应（无签到任务）：
```json
{
    "has_active": false,
    "task": null
}
```

### 3.2 人脸签到

**POST** `/api/sign-tasks/{task_id}/sign`

需要认证：是（学生角色）

请求：`multipart/form-data`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | 是 | 学生当前人脸照片 |

成功响应：
```json
{
    "success": true,
    "message": "签到成功",
    "confidence": 0.95,
    "signed_at": "2026-05-25 10:01:30"
}
```

---

## 四、WebSocket 接口

连接地址：`ws://localhost:5000`

### 4.1 事件类型

#### new_sign_task - 新签到任务通知（推送给学生）

```json
{
    "task_id": 1,
    "title": "第一节人脸签到",
    "teacher_name": "王老师"
}
```

#### student_signed - 学生签到成功通知（推送给老师）

```json
{
    "task_id": 1,
    "student_id": "2021001",
    "student_name": "张三",
    "confidence": 0.95
}
```

#### sign_task_ended - 签到结束通知（推送给学生）

```json
{
    "task_id": 1,
    "title": "第一节人脸签到"
}
```

---

## 五、错误响应

所有接口错误响应格式：

```json
{
    "success": false,
    "message": "错误信息"
}
```

HTTP状态码：
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器内部错误

---

## 六、测试流程

### 6.1 老师操作流程

1. 注册老师账号
2. 登录获取Token
3. 添加学生账号
4. 上传学生人脸照片
5. 创建签到任务
6. 查看签到记录
7. 结束签到

### 6.2 学生操作流程

1. 登录获取Token
2. 查询进行中的签到
3. 上传人脸照片进行签到
4. 查看签到结果