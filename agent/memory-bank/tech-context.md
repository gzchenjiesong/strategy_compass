# 技术环境 (Tech Context)

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 后端语言 | Python | 3.12+ | 主力开发语言 |
| Web 框架 | Flask | 3.0+ | 轻量灵活 |
| WSGI 服务器 | Gunicorn | 22.0+ | 生产环境运行 |
| 数据库 | SQLite | 3.x | 初期方案 |
| HTTP 客户端 | httpx | 0.27+ | 异步 HTTP 请求 |
| JWT | PyJWT | 2.8+ | 用户认证 |
| 前端语言 | TypeScript | 5.x | 类型安全 |
| 前端框架 | Vue 3 | 3.x | Composition API |
| 构建工具 | Vite | 5.x | 快速 HMR |
| CSS | Tailwind CSS | 3.x | 原子化 CSS |
| 图表 | ECharts | 5.x | 数据可视化 |
| 容器 | Docker | 26.x | 容器化部署 |
| 反向代理 | Nginx | 1.25 | 静态文件 + SSL |
| 服务器 | 腾讯云轻量 | 4C8G/10M | 广州地域 |
| 域名 | i-strategy-compass.com | - | .com 备案中 |

## 本地开发环境

- **操作系统：** macOS（开发机） / Debian（服务器）
- **Python：** 3.12+
- **Node.js：** 22.x
- **Docker Desktop：** 已安装

## 外部 API / 数据源

| 数据源 | 用途 | 免费额度 |
|--------|------|----------|
| AKShare | A 股行情、基金数据 | 完全免费 |
| 东方财富 API | 板块数据、资金流向 | 免费（有频率限制） |
| Marketaux | 国际财经资讯 | 免费 100 次/天 |
| 微信开放平台 | OAuth 登录 | 免费 |

## 已知限制

- SQLite 不支持高并发写入（WAL 模式下并发读没问题）
- 免费行情数据有延迟（15 分钟或收盘后）
- 微信 OAuth 需要备案域名才能正式使用
- 服务器 10Mbps 带宽，静态资源建议上 CDN（后期）
