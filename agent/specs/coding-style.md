# 代码风格约定 (Coding Style)

## Python

### 命名
- 变量/函数：`snake_case`
- 类名：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有：`_leading_underscore`
- 模块名：`snake_case`（短、小写、不用下划线分隔单词除非必要）

### 格式
- 缩进：4 空格
- 行宽：120 字符
- 字符串：优先双引号（与 JSON 一致）
- 导入：标准库 → 第三方 → 本地，各组之间空一行

### 注释
- 函数必须有 docstring（说明做什么，不是怎么做）
- 复杂逻辑必须有行内注释
- 不写显而易见的注释（如 `# 设置用户名` 在 `username = ...` 上方）

### 错误处理
- 不要用 bare `except:`
- 具体异常具体捕获
- 错误信息要包含上下文（如 `"Failed to fetch stock {code}: {error}"`）

### 禁止
- ❌ 魔法数字（用常量或配置替代）
- ❌ 深层嵌套（超过 3 层用 early return 或提取函数）
- ❌ 超长函数（超过 50 行考虑拆分）
- ❌ 全局可变状态

## TypeScript / Vue

### 命名
- 变量/函数：`camelCase`
- 类/接口/组件：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- CSS 类名：`kebab-case`

### Vue 组件
- 单文件组件：`PascalCase.vue`
- Props：`camelCase` 定义，`kebab-case` 使用
- Events：`kebab-case`

### 格式
- 使用 Prettier 默认配置
- ESLint + Vue recommended rules
- 不要手动格式化，让工具来

## SQL

- 关键字大写：`SELECT`, `FROM`, `WHERE`
- 表名/列名：`snake_case`
- 每个表必须有 `created_at` 字段
- 外键必须命名约束

## API

- 路径：`/api/v1/resource-name`（小写 + 连字符）
- 请求/响应：`snake_case` 字段名
- 错误响应统一格式：`{"error": "message", "code": "ERROR_CODE"}`
- 成功响应统一格式：`{"data": ..., "message": "success"}`
