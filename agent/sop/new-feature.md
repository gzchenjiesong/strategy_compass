# 新功能开发流程 (SOP)

> 当 Agent 被要求开发一个新功能时，按此流程执行。

## 流程概览

```
需求理解 → 设计对齐 → 数据模型 → API 设计 → 后端实现 → 前端实现 → 测试 → 文档更新 → 技能沉淀
```

## 步骤详解

### 1. 需求理解

- [ ] 确认功能边界：做什么、不做什么
- [ ] 确认归属模块（Module 0/1/2/3/4）
- [ ] 确认上下游依赖：需要调用哪些已有接口、暴露哪些新接口
- [ ] 确认输入/输出：用户怎么操作、看到什么结果
- [ ] 有疑问就问，不要猜

### 2. 设计对齐

- [ ] 检查已有模块设计文档是否覆盖该功能
- [ ] 如需新增/修改接口，先更新对应模块设计文档
- [ ] 如需新增数据表，先更新 Module 1 数据模型
- [ ] **先写文档再写代码**

> 设计文档位置：`docs/modules/module-N-*.md`

### 3. 数据模型

- [ ] 确定需要哪些表/字段
- [ ] 在对应模块设计文档中记录表结构
- [ ] 编写 DDL（CREATE TABLE / ALTER TABLE）
- [ ] 确认索引策略
- [ ] 确认去重规则（INSERT OR IGNORE / REPLACE）

> 参考：`agent/specs/database.md`（数据库设计规范）

### 4. API 设计

- [ ] 按 `agent/specs/api-design.md` 规范设计接口
- [ ] 在对应模块设计文档中记录接口定义
- [ ] 考虑错误处理和边界情况
- [ ] 确认与上下游模块的接口契约

### 5. 后端实现

分层实现顺序：

```
Model（数据层）→ Service（业务逻辑层）→ Route（API 路由层）
```

- [ ] Model：定义 SQLAlchemy 模型或数据访问函数
- [ ] Service：实现核心业务逻辑（估值计算、数据聚合等）
- [ ] Route：实现 Flask Blueprint 路由，调用 Service
- [ ] 添加 `@auth_required` 认证装饰器（如需要）
- [ ] 运行 `./scripts/api-check.sh` 验证（如脚本已存在）

> 参考：`agent/specs/backend-architecture.md`（后端分层规范）

### 6. 前端实现

- [ ] 在 `frontend/src/views/` 或 `frontend/src/components/` 中创建组件
- [ ] 使用 Composition API + `<script setup>` 语法
- [ ] 组件命名使用 PascalCase
- [ ] Props 使用 camelCase 定义，kebab-case 使用
- [ ] API 调用封装在 `frontend/src/api/` 下的模块文件中
- [ ] 如需要截图验收，运行 `./scripts/screenshot.py`

> 参考：`agent/specs/frontend-architecture.md`（前端组件规范）

### 7. 测试

- [ ] API 接口测试（curl / Postman / 自动化脚本）
- [ ] 业务逻辑单元测试（关键计算函数）
- [ ] 前端组件功能测试
- [ ] 手动走一遍用户流程（如果涉及复杂交互）
- [ ] 边界情况测试（空数据、超时、错误响应）

### 8. 文档更新

- [ ] 更新对应模块设计文档（如有接口/表变更）
- [ ] 更新 `agent/memory-bank/progress.md` 标记完成
- [ ] 更新 `agent/memory-bank/active-context.md` 更新当前焦点
- [ ] 写开发日志 `agent/memory/YYYY-MM-DD.md`

### 9. 技能沉淀（如适用）

- [ ] 如果开发过程中发现可复用的模式/工具/脚本，沉淀到 `agent/skills/`
- [ ] 如果踩了坑或发现更好的做法，更新对应 SOP/Spec

### 10. Git 提交

- [ ] 按 `agent/specs/git-flow.md` 规范提交
- [ ] commit message：`类型: 简要描述`（中文）
- [ ] 从 feature 分支向 develop 发 PR

## 模块开发顺序参考

按依赖关系排序：

```
Module 0 用户系统（基础）
  ↓
Module 1 数据底座（数据层）
  ↓
Module 4 估值分析（计算引擎）
  ↓
Module 2 新闻聚合（加工层）
  ↓
Module 3 市场概览（聚合层）
```

## 检查清单

每个功能开发完，过一遍这个清单：

- [ ] 功能按设计文档实现了吗？
- [ ] 接口契约与上下游对齐了吗？
- [ ] API 响应格式符合 `agent/specs/api-design.md` 吗？
- [ ] 数据表有合适的索引吗？
- [ ] 没有硬编码的密钥/密码？
- [ ] 没有魔法数字（用常量或配置替代）？
- [ ] 错误处理覆盖了边界情况？
- [ ] 文档更新了吗？
- [ ] Git commit 规范吗？
