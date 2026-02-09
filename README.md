# 人脸识别考勤系统

基于 Python FastAPI + Vue 3 + MySQL 的人脸识别考勤管理系统。

## 功能特性

- 🔐 用户认证（JWT）
- 👤 员工管理（增删改查、人脸录入）
- 🏢 部门管理
- 📷 人脸识别打卡（签到/签退）
- 📊 考勤记录查询与统计
- 🖼️ 打卡照片记录

## 技术栈

### 后端

- Python 3.11
- FastAPI
- SQLAlchemy
- face_recognition（人脸识别）
- MySQL 8.0
- JWT 认证

### 前端

- Vue 3
- Vite
- Element Plus
- Pinia
- Vue Router

## 快速开始

### 环境要求

- Docker
- Docker Compose

### 启动项目

```bash
# 克隆项目后，在项目根目录执行
docker-compose up --build -d

# 查看日志
docker-compose logs -f
```

### 访问地址

- 前端: http://localhost:8081
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 测试账号

| 账号     | 密码     | 角色     |
| -------- | -------- | -------- |
| admin    | admin123 | 管理员   |
| zhangsan | 123456   | 普通员工 |

## 项目结构

```
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   └── services/       # 业务逻辑
│   ├── Dockerfile
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt
├── frontend-admin/          # 前端代码
│   ├── src/
│   │   ├── api/            # API接口
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # Pinia状态
│   │   └── router/         # 路由配置
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Docker编排
└── README.md
```

## 使用说明

### 人脸打卡

1. 访问 http://localhost:8081/attendance 进入打卡页面
2. 允许浏览器访问摄像头
3. 将面部对准摄像头，点击"签到"或"签退"
4. 系统自动识别身份并记录打卡

### 员工管理

1. 使用管理员账号登录
2. 进入"员工管理"页面
3. 添加员工信息
4. 点击"录入人脸"为员工录入人脸照片

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 重新构建并启动
docker-compose up --build -d

# 停止服务
docker-compose down

# 停止并清除数据
docker-compose down -v

# 查看日志
docker-compose logs -f backend
```

## 端口说明

| 服务  | 端口 |
| ----- | ---- |
| 前端  | 8081 |
| 后端  | 8000 |
| MySQL | 3306 |
