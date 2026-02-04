# Docker 使用指南

> 古玩字画智能对比系统
> 最后更新：2026-02-03

---

## 目录

- [快速开始](#快速开始)
- [生产环境部署](#生产环境部署)
- [开发环境](#开发环境)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

---

## 快速开始

### 1. 前置要求

确保已安装：
- Docker Desktop (Windows/macOS) 或 Docker Engine (Linux)
- Docker Compose

### 2. 启动所有服务

```bash
# 克隆项目后，在项目根目录执行
docker-compose up -d
```

### 3. 访问应用

- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 5. 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（⚠️ 会删除数据库数据）
docker-compose down -v
```

---

## 生产环境部署

### 构建生产镜像

```bash
# 构建所有服务镜像
docker-compose build

# 构建特定服务镜像
docker-compose build backend
docker-compose build frontend
```

### 启动生产环境

```bash
# 使用生产配置启动
docker-compose -f docker-compose.yml up -d
```

### 生产环境配置

修改 `docker-compose.yml` 中的环境变量：

```yaml
environment:
  - SECRET_KEY=your-production-secret-key
  - DEBUG=False
  - ENVIRONMENT=production
  - DB_PASSWORD=your-secure-password
```

---

## 开发环境

### 启动开发环境

开发环境支持代码热重载，建议使用：

```bash
# 使用开发配置启动
docker-compose -f docker-compose.dev.yml up -d
```

### 仅启动数据库

如果在宿主机运行前后端：

```bash
# 只启动 PostgreSQL
docker-compose up -d postgres

# 后端（在宿主机）
cd backend
uvicorn main:app --reload

# 前端（在宿主机）
cd frontend
npm run dev
```

### 代码修改后

开发环境支持自动热重载：
- 后端：修改 Python 代码后自动重启
- 前端：修改 Vue 代码后浏览器自动刷新

---

## 常用命令

### 容器管理

```bash
# 查看运行中的容器
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d antique_comparison

# 重启服务
docker-compose restart backend

# 重建并启动
docker-compose up -d --build
```

### 数据库操作

```bash
# 连接到 PostgreSQL
docker-compose exec postgres psql -U postgres -d antique_comparison

# 备份数据库
docker-compose exec postgres pg_dump -U postgres antique_comparison > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U postgres antique_comparison < backup.sql
```

### 数据库迁移

```bash
# 在 backend 容器中执行迁移
docker-compose exec backend alembic upgrade head

# 创建新的迁移
docker-compose exec backend alembic revision --autogenerate -m "描述"
```

### 清理系统

```bash
# 停止并删除容器、网络
docker-compose down

# 删除未使用的镜像
docker image prune -a

# 删除未使用的卷
docker volume prune

# 清理所有未使用的 Docker 资源
docker system prune -a --volumes
```

---

## 故障排查

### 问题 1: 端口被占用

**错误信息**: `Bind for 0.0.0.0:5432 failed: port is already allocated`

**解决方案**:
```bash
# 查看占用端口的进程
netstat -ano | findstr :5432

# 修改 docker-compose.yml 中的端口映射
ports:
  - "5433:5432"  # 使用 5433 端口
```

### 问题 2: 数据库连接失败

**错误信息**: `could not connect to server: Connection refused`

**解决方案**:
```bash
# 等待数据库完全启动
docker-compose logs postgres
docker-compose ps

# 检查数据库健康状态
docker-compose exec postgres pg_isready
```

### 问题 3: 后端无法启动

**错误信息**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 重新构建镜像
docker-compose build backend

# 查看详细日志
docker-compose logs backend
```

### 问题 4: 前端无法访问后端

**解决方案**:
- 确保后端和前端在同一网络中
- 检查 nginx 配置中的 proxy_pass 设置
- 查看容器日志: `docker-compose logs frontend`

### 问题 5: 权限问题（Linux）

**错误信息**: `Permission denied`

**解决方案**:
```bash
# 调整文件权限
sudo chown -R $USER:$USER ./backend
sudo chown -R $USER:$USER ./frontend

# 或使用 Docker 管理器
sudo usermod -aG docker $USER
```

---

## 数据持久化

### 数据卷

- `postgres_data`: PostgreSQL 数据
- `./uploads`: 上传的文件
- `./backups`: 数据库备份
- `./logs`: 应用日志

### 备份和恢复

```bash
# 备份数据卷
docker run --rm -v antique_postgres_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/postgres-backup.tar.gz -C /data .

# 恢复数据卷
docker run --rm -v antique_postgres_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/postgres-backup.tar.gz -C /data
```

---

## 性能优化

### 限制资源使用

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 使用多阶段构建

生产环境的前端 Dockerfile 已经使用多阶段构建，减小镜像大小。

---

## 安全建议

1. **修改默认密码**
   - 修改数据库密码
   - 修改 SECRET_KEY

2. **使用环境变量文件**
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   # 编辑敏感信息
   ```

3. **限制网络访问**
   - 生产环境不要暴露所有端口
   - 使用防火墙规则

4. **定期更新**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

---

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [PostgreSQL Docker 镜像](https://hub.docker.com/_/postgres)
