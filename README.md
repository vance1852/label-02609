# 人脸识别考勤系统

基于 Python FastAPI + Vue 3 + Element Plus 的人脸识别考勤管理系统。

## How to Run

### Docker 方式（推荐）

```bash
# 启动所有服务
docker-compose up --build -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 本地开发

**后端：**

```bash
cd backend
pip install -r requirements.txt
python init_db.py  # 初始化数据库
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端：**

```bash
cd frontend-admin
npm install
npm run dev
```

## Services

| 服务         | 地址                       | 说明                 |
| ------------ | -------------------------- | -------------------- |
| 前端管理后台 | http://localhost:8081      | Vue 3 + Element Plus |
| 后端 API     | http://localhost:8000      | FastAPI              |
| API 文档     | http://localhost:8000/docs | Swagger UI           |
| MySQL        | localhost:3306             | 数据库               |

## 测试账号

| 角色     | 用户名   | 密码     |
| -------- | -------- | -------- |
| 管理员   | admin    | admin123 |
| 普通用户 | zhangsan | 123456   |

## 题目内容

帮我用python写一个人脸识别考勤网页系统

---

## 功能特性

- 🔐 JWT 身份认证
- 👤 员工管理（增删改查）
- 🏢 部门管理
- 📷 人脸录入与识别
- ⏰ 人脸签到/签退
- 📊 考勤记录查询与统计
- 🎨 响应式 UI 设计

## 技术栈

**后端：**

- Python 3.11
- FastAPI
- SQLAlchemy + PyMySQL
- face_recognition (dlib)
- JWT 认证

**前端：**

- Vue 3 + Vite
- Element Plus
- Pinia
- Axios
- SCSS

**数据库：**

- MySQL 8.0

## 项目结构

```
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic 模式
│   │   ├── services/       # 业务逻辑
│   │   └── main.py         # 应用入口
│   ├── Dockerfile
│   ├── requirements.txt
│   └── schema.sql          # 数据库脚本
├── frontend-admin/          # 前端项目
│   ├── src/
│   │   ├── api/            # API 封装
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态
│   │   ├── styles/         # 全局样式
│   │   └── views/          # 页面组件
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                    # 文档
│   └── project_design.md
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 使用说明

1. **登录系统**：使用管理员账号登录后台管理系统
2. **添加部门**：在部门管理中创建公司部门
3. **添加员工**：在员工管理中添加员工信息
4. **录入人脸**：为员工上传清晰的正面人脸照片
5. **人脸打卡**：员工通过摄像头进行人脸签到/签退
6. **查看记录**：在考勤记录中查看和统计考勤数据
