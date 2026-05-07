# Strategy Compass 长期记忆

## 技术栈
- 后端：Python (Flask + SQLite + Gunicorn)
- 前端：Vue 3 + Vite + ECharts
- 部署：Docker Compose + Nginx，腾讯云轻量 4C8G
- 数据库：SQLite WAL 模式，后期可迁 PostgreSQL
- 定时任务：APScheduler

## 核心数据源
- **AKShare**：免费开源金融数据接口库，覆盖 A 股/港股/ETF/指数/板块/财务/估值
- **腾讯财经 API** (qt.gtimg.cn)：实时行情辅助源，速度快无鉴权
- **金十数据**：7×24 财经快讯，MVP 唯一新闻源

## 数据深度约定（2026-05-07 确认）
- 大盘指数（上证/恒生/标普等）：**20 年**日 K
- 行业/概念板块：**15 年**日 K
- 个股/宽基基金：**10 年**日 K
- 数据粒度：日 K 存储，周 K 按需聚合

## 实时行情频率（2026-05-07 确认）
- **分钟级**（非量化交易，操作按天进行）

## 市场覆盖（2026-05-07 确认）
- A 股：MVP ✅
- 港股（含港股通个股）：MVP ✅
- 美股：MVP 后置
- 全球指数（恒生/标普/纳指）：MVP ✅

## 设计文件索引
- Module 0 用户系统：`docs/modules/module-0-user-system.md`（已确认冻结）
- Module 1 数据源分析：`docs/modules/module-1-data-source-analysis.md`（数据源分析完成）
- Module 1 接口+数据模型：`docs/modules/module-1-data-service.md`（初稿完成，待确认，14 张表）
- Module 4 估值分析：`docs/modules/module-4-valuation-analysis.md`（初稿完成，待确认，7 组 API）

## Module 4 估值分析 — 指标体系（2026-05-07 研究）
- **估值百分位是核心方法**：PE/PB/PS 历史百分位，≤30% 低估 / 30%-70% 适中 / ≥70% 高估
- 不同标的类型侧重不同：金融看PB、周期看PB+景气度、成长看PE+PEG、消费看PE
- 四维度：估值高低 + 热度 + 情绪 + 回撤风险
- 风险指标：最大回撤/当前回撤/年化波动率/夏普比率/卡玛比率/Beta

## Module 4 估值分析 — 设计完成（2026-05-07）
- 分标的类型指标体系：大盘指数/行业板块/概念板块/个股/ETF/市场整体各用不同指标组合
- 7 组 API：指数/板块/个股/ETF/市场整体/区间统计/历史曲线
- 核心计算：百分位 + 风险指标 + 估值区间标签
- 性能优化：内存预计算 + 增量更新 + 1 小时缓存
- ETF 估值通过 ETF→指数映射表实现

## Module 1 关键设计决策
- K 线按类型分三张表：stock_daily_kline / index_daily_kline / board_daily_kline（不同历史深度+查询模式）
- K 线只存日 K，周/月 K 按需聚合（减少存储冗余）
- 估值 INSERT OR REPLACE（当日可能修正），K 线 INSERT OR IGNORE（历史不改）
- 初始化：10 核心指数自动拉取，板块/个股按需触发（用户添加后异步）
- 新闻 TTL 72h 自动清理，金十单一来源
