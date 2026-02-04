# 古玩字画智能对比系统 - 前端 Dockerfile

# ==================== 构建阶段 ====================
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package.json 和 pnpm-lock.yaml（如果使用 pnpm）
COPY package.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# ==================== 运行阶段 ====================
FROM nginx:alpine

# 复制构建产物到 Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
