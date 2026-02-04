# 古玩字画智能对比系统

> 基于人工智能的文物借出归还真伪识别系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目简介

古玩字画智能对比系统是为博物馆设计的文物管理系统，主要用于在文物借出和归还时进行真伪对比。系统通过 AI 图像对比技术，自动识别字画类古玩的真伪差异，为文物保护提供技术支持。

### 核心功能

- **借出存档**：文物借出时拍摄照片并记录信息
- **收回对比**：归还时通过 AI 对比判断真伪
- **智能分析**：6 维度对比（印章、笔触、纸张、题跋、构图、水印）
- **差异标注**：可视化标注差异区域
- **权限管理**：三种角色权限控制
- **导出报告**：生成 PDF 对比报告

---

## 技术栈

### 前端

- **框架**: Vue.js 3 + Vite
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **图片标注**: Fabric.js

### 后端

- **框架**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL
- **认证**: JWT
- **异步**: Uvicorn

### AI 服务

- **图像处理**: OpenCV + Pillow
- **对比算法**: OpenAI Vision API / 开源模型（CLIP、ResNet）

### 部署

- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx

---

## 项目结构

```
Project of Antique/
├── backend/          # FastAPI 后端
├── frontend/         # Vue 3 前端
├── ai_service/       # AI 对比服务
├── docs/            # 项目文档
├── uploads/         # 文件上传目录
└── docker-compose.yml
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose（可选）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd Project of Antique
```

#### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息
```

#### 3. 启动服务（使用 Docker）

```bash
docker-compose up -d
```

#### 4. 手动安装（开发环境）

**后端安装**：

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

**前端安装**：

```bash
cd frontend
npm install  # 或 pnpm install
npm run dev
```

#### 5. 访问系统

- 前端地址: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

#### 6. 默认账号

```
用户名: admin
密码: admin123
角色: 管理员
```

---

## 开发指南

### 后端开发

```bash
cd backend

# 运行测试
pytest

# 数据库迁移
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

### 前端开发

```bash
cd frontend

# 代码检查
npm run lint

# 代码格式化
npm run format

# 构建生产版本
npm run build
```

---

## 文档

- [PRD 文档](./docs/古玩字画智能对比系统PRD.md)
- [技术栈和架构设计](./docs/技术栈和架构设计.md)
- [开发任务列表](./docs/todo.md)
- [API 文档](./docs/api.md)（待完善）

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范

- Python: 遵循 PEP 8
- JavaScript: 使用 ESLint + Prettier
- Git 提交: 使用 Conventional Commits 格式

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: contact@antique-system.local

---

**感谢使用古玩字画智能对比系统！**
