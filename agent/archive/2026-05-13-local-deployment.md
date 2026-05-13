# 本地开发环境部署 (SOP)

> Strategy Compass 本地开发环境快速启动指南。
> 适用场景：开发调试、功能验收、Bug 复现。

## 环境要求

- macOS / Linux
- Python 3.12+ (后端)
- Node.js 20+ (前端)
- SQLite (已内置)

## 快速开始

### 1. 首次部署

```bash
# 1. 确保后端依赖已安装
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
cd ..

# 2. 初始化数据库
.venv/bin/python backend/scripts/init_db.py

# 3. 启动全部服务
./scripts/local-deploy.sh
```

### 2. 日常启动

```bash
# 启动全部（后端 + 前端）
./scripts/local-deploy.sh

# 只启动后端
./scripts/local-deploy.sh backend

# 只启动前端（后端已运行）
./scripts/local-deploy.sh frontend

# 先构建前端再启动全部
./scripts/local-deploy.sh --build
```

### 3. 停止服务

```bash
# 停止全部
./scripts/local-stop.sh

# 只停止后端
./scripts/local-stop.sh backend

# 只停止前端
./scripts/local-stop.sh frontend
```

### 4. 重启服务

```bash
# 重启全部
./scripts/local-restart.sh

# 重启后端
./scripts/local-restart.sh backend

# 重启前端
./scripts/local-restart.sh frontend

# 先构建再重启全部
./scripts/local-restart.sh --build
```

### 5. 查看状态

```bash
./scripts/local-status.sh
```

### 6. 更新 Mock Token

开发环境使用 mock token 绕过微信登录。token 有过期时间，过期后登录会失败。

```bash
# 自动生成新 token（365天有效期）
./scripts/update-mock-token.sh

# 检查当前 token 是否过期
./scripts/update-mock-token.sh --check

# 使用指定 token
./scripts/update-mock-token.sh <your-jwt-token>
```

更新 token 后需要重新构建前端：

```bash
# 方式1：手动构建
cd frontend && npm run build && cd ..
./scripts/local-restart.sh frontend

# 方式2：一键构建+重启
./scripts/local-restart.sh --build
```

## 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://127.0.0.1:8080 | 包含 API 代理 |
| 后端 API | http://127.0.0.1:5000 | Flask 服务 |
| API 代理 | http://127.0.0.1:8080/api/* | 前端代理到后端 |

## 文件说明

| 脚本 | 用途 |
|------|------|
| `scripts/local-deploy.sh` | 启动后端 + 前端 |
| `scripts/local-stop.sh` | 停止服务 |
| `scripts/local-restart.sh` | 重启服务 |
| `scripts/local-status.sh` | 查看运行状态 |
| `scripts/update-mock-token.sh` | 更新 mock token |
| `scripts/api-check.sh` | API 接口测试 |

## 常见问题

### Q: 点击「开发者登录」后没有跳转
**原因**: mock token 过期，后端验证 401 后跳回登录页。
**解决**: `./scripts/update-mock-token.sh && ./scripts/local-restart.sh --build`

### Q: 端口被占用
**原因**: 之前的服务未正常停止。
**解决**: `./scripts/local-stop.sh` 后再启动。

### Q: 前端 404
**原因**: `frontend/dist` 不存在或构建失败。
**解决**: `cd frontend && npm run build`

### Q: 后端数据库连接失败
**原因**: 数据库文件不存在或路径错误。
**解决**: `backend/.venv/bin/python backend/scripts/init_db.py`

## 技术细节

### 后端启动参数

```bash
FLASK_ENV=development
DATABASE_URL="sqlite:////absolute/path/to/backend/data/strategy_compass.db"
JWT_SECRET="dev-secret"
```

### 前端代理原理

前端使用内嵌 Python HTTP 服务器（`http.server`）：
- 静态文件请求 → 直接返回 `frontend/dist` 下的文件
- `/api/*` 请求 → 反向代理到 `http://127.0.0.1:5000`
- SPA 路由 → 所有未知路径返回 `index.html`

### Mock Token 机制

- `LoginView.vue`: 用户点击「开发者登录」时写入 `localStorage`
- `request.ts`: 开发环境自动注入 token 到请求头
- 后端 `auth_service.py`: 验证 JWT token 的签名和过期时间
