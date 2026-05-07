# 部署流程 (SOP)

> Strategy Compass 部署到腾讯云轻量服务器（4C8G，广州）。

## 1. 部署架构

```
┌─────────────────────────────────────┐
│           Nginx (反向代理)            │
│  ┌──────────┐      ┌────────────┐  │
│  │ 前端静态文件 │      │ API 请求转发 │  │
│  │ (Vue build)│      │  → Flask   │  │
│  └──────────┘      └────────────┘  │
└──────────┬──────────────────────────┘
           │
    ┌──────┴──────┐
    │   Docker    │
    │  Compose    │
    │             │
    │ ┌─────────┐ │
    │ │ 后端容器 │ │ Flask + Gunicorn
    │ │ (Python)│ │
    │ └─────────┘ │
    │ ┌─────────┐ │
    │ │ 前端容器 │ │ Nginx 静态文件服务
    │ │ (Nginx) │ │
    │ └─────────┘ │
    │ ┌─────────┐ │
    │ │ 数据卷  │ │ SQLite + 日志
    │ │ (持久化)│ │
    │ └─────────┘ │
    └─────────────┘
```

## 2. 环境准备

### 2.1 服务器要求

- OS: Ubuntu 22.04 LTS
- CPU: 4 核
- 内存: 8 GB
- 磁盘: 80 GB SSD
- 带宽: 6 Mbps

### 2.2 安装 Docker

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
sudo apt install -y docker.io docker-compose

# 启动 Docker
sudo systemctl enable docker
sudo systemctl start docker

# 添加当前用户到 docker 组
sudo usermod -aG docker $USER
```

## 3. 项目构建

### 3.1 后端构建

```bash
# Dockerfile (backend/Dockerfile)
FROM python:3.12-alpine

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

### 3.2 前端构建

```bash
# Dockerfile (frontend/Dockerfile)
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 3.3 Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: sc-backend
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///data/strategy_compass.db
      - SECRET_KEY=${SECRET_KEY}
      - WECHAT_APP_ID=${WECHAT_APP_ID}
      - WECHAT_APP_SECRET=${WECHAT_APP_SECRET}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - sc-network

  frontend:
    build: ./frontend
    container_name: sc-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - sc-network

  # 定时任务容器（可选，与 backend 共享代码）
  scheduler:
    build: ./backend
    container_name: sc-scheduler
    restart: unless-stopped
    command: python -m app.tasks.scheduler
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///data/strategy_compass.db
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    networks:
      - sc-network

networks:
  sc-network:
    driver: bridge

volumes:
  data:
  logs:
```

## 4. 部署流程

### 4.1 首次部署

```bash
# 1. 克隆代码
git clone https://github.com/gzchenjiesong/strategy_compass.git
cd strategy_compass

# 2. 创建环境变量文件
cat > .env << EOF
SECRET_KEY=your-secret-key-here
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
JIN10_API_KEY=your-jin10-api-key
EOF

# 3. 创建数据目录
mkdir -p data logs

# 4. 构建并启动
docker-compose up -d --build

# 5. 初始化数据库
docker-compose exec backend python scripts/init_db.py

# 6. 拉取核心指数历史数据
docker-compose exec backend python scripts/init_core_indices.py

# 7. 检查状态
docker-compose ps
docker-compose logs -f backend
```

### 4.2 更新部署

```bash
# 1. 拉取最新代码
git pull origin develop

# 2. 重新构建
docker-compose down
docker-compose up -d --build

# 3. 执行数据库迁移（如有）
docker-compose exec backend python scripts/migrations/apply.py

# 4. 检查状态
docker-compose ps
```

### 4.3 回滚

```bash
# 回滚到上一个版本
git log --oneline -5  # 查看历史
git checkout <commit-hash>
docker-compose down
docker-compose up -d --build
```

## 5. Nginx 配置

```nginx
# deploy/nginx.conf
server {
    listen 80;
    server_name i-strategy-compass.com;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API 请求转发到后端
    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 6. 监控与日志

### 6.1 查看日志

```bash
# 后端日志
docker-compose logs -f backend

# 前端日志
docker-compose logs -f frontend

# 所有日志
docker-compose logs -f
```

### 6.2 日志轮转

```bash
# 配置 logrotate
cat > /etc/logrotate.d/strategy-compass << EOF
/var/log/strategy-compass/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF
```

## 7. 备份

### 7.1 数据库备份

```bash
#!/bin/bash
# scripts/backup.sh
BACKUP_DIR="/backup/strategy-compass"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份 SQLite
sqlite3 data/strategy_compass.db ".backup '${BACKUP_DIR}/db_${DATE}.bak'"

# 保留最近 30 天的备份
find $BACKUP_DIR -name "db_*.bak" -mtime +30 -delete

# 备份配置文件
cp .env ${BACKUP_DIR}/env_${DATE}
```

### 7.2 定时备份

```bash
# 添加到 crontab
crontab -e
# 每天凌晨 3 点备份
0 3 * * * /path/to/strategy_compass/scripts/backup.sh
```

## 8. 故障排查

| 问题 | 排查命令 | 解决方案 |
|------|---------|---------|
| 容器无法启动 | `docker-compose logs` | 检查环境变量、端口冲突 |
| 数据库连接失败 | `docker-compose exec backend ls data/` | 检查数据卷挂载 |
| 前端 404 | `docker-compose exec frontend ls /usr/share/nginx/html` | 检查构建输出 |
| API 502 | `docker-compose ps` | 检查后端容器状态 |
| 内存不足 | `docker stats` | 限制容器内存或升级服务器 |

## 9. 环境变量清单

| 变量名 | 必填 | 说明 |
|--------|------|------|
| SECRET_KEY | 是 | Flask 密钥 |
| DATABASE_URL | 否 | 默认 `sqlite:///data/strategy_compass.db` |
| WECHAT_APP_ID | 是 | 微信 OAuth AppID |
| WECHAT_APP_SECRET | 是 | 微信 OAuth AppSecret |
| JIN10_API_KEY | 是 | 金十数据 API Key |
| FLASK_ENV | 否 | `development` / `production` |
| LOG_LEVEL | 否 | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
