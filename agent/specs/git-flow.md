# Git 分支与提交规范

## 分支策略

```
main            ← 生产分支，始终保持可部署状态
  └── develop   ← 开发分支，日常开发在此进行
        ├── feature/grid-trading    ← 功能分支
        ├── feature/dca-strategy
        └── fix/xxx-bug             ← 修复分支
```

### 规则
- `main` — 只接受来自 `develop` 的合并，打 tag 发版
- `develop` — 日常开发的主战场
- `feature/*` — 每个新功能一个分支
- `fix/*` — 每个 Bug 修复一个分支
- **禁止直接 push 到 `main`**

## Commit Message 规范

格式：`类型: 简要描述`

### 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加网格交易 S 级网格定义` |
| `fix` | 修复 Bug | `fix: 修复价格计算精度问题` |
| `docs` | 文档更新 | `docs: 更新网格交易设计文档` |
| `refactor` | 重构 | `refactor: 提取行情数据获取为独立服务` |
| `test` | 测试 | `test: 添加网格计算单元测试` |
| `chore` | 构建/工具 | `chore: 更新 Dockerfile 基础镜像` |
| `style` | 格式调整 | `style: 格式化 views.py` |
| `perf` | 性能优化 | `perf: 优化 SQLite 查询使用索引` |

### 规则
- 用中文写描述（项目主要协作者是中文用户）
- 第一行不超过 50 字符
- 不以句号结尾
- 不要写 `Update xxx` 这种无信息量的描述

## PR 规范

- 从 feature/fix 分支向 develop 发 PR
- PR 标题 = commit message 格式
- PR 描述说明：做了什么、为什么做、怎么测试
- 自测通过后再发 PR
