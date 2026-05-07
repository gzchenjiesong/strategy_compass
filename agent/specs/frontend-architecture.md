# 前端架构规范

> Strategy Compass 前端采用 Vue 3 + Vite + TypeScript 架构。

## 1. 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/                # API 接口封装
│   │   ├── auth.ts         # Module 0 认证
│   │   ├── data.ts         # Module 1 数据
│   │   ├── news.ts         # Module 2 新闻
│   │   ├── market.ts       # Module 3 市场
│   │   └── valuation.ts    # Module 4 估值
│   ├── assets/             # 图片、字体等
│   ├── components/         # 公共组件
│   │   ├── AppLayout.vue       # 页面布局（顶部+底部导航）
│   │   ├── TopBar.vue          # 顶部固定栏
│   │   ├── BottomNav.vue       # 底部固定栏
│   │   ├── CardList.vue        # 卡片列表容器
│   │   ├── IndexCard.vue       # 指数卡片
│   │   ├── BoardCard.vue       # 板块卡片
│   │   ├── NewsCard.vue        # 新闻卡片
│   │   ├── DetailModal.vue     # 详情弹窗容器
│   │   ├── IndexDetail.vue     # 指数详情
│   │   ├── BoardDetail.vue     # 板块详情
│   │   ├── ZoneBadge.vue       # 估值区间标签
│   │   └── TimeAgo.vue         # 相对时间显示
│   ├── composables/        # 组合式函数
│   │   ├── useAuth.ts          # 认证状态
│   │   ├── useMarket.ts        # 市场数据
│   │   ├── useNews.ts          # 新闻数据
│   │   └── useValuation.ts     # 估值数据
│   ├── router/             # 路由配置
│   │   └── index.ts
│   ├── stores/             # Pinia 状态管理
│   │   ├── auth.ts             # 用户认证
│   │   ├── market.ts           # 市场数据缓存
│   │   └── news.ts             # 新闻数据缓存
│   ├── styles/             # 全局样式
│   │   └── global.css
│   ├── types/              # TypeScript 类型定义
│   │   └── index.ts
│   ├── utils/              # 工具函数
│   │   ├── request.ts          # Axios 封装
│   │   ├── format.ts           # 格式化（金额、百分比、时间）
│   │   └── constants.ts        # 常量
│   ├── views/              # 页面视图
│   │   ├── NewsView.vue        # 资讯页面（Module 2）
│   │   ├── MarketView.vue      # 市场页面（Module 3）
│   │   │   ├── OverviewTab.vue     # 概览标签
│   │   │   ├── IndicesTab.vue      # 大盘标签
│   │   │   └── BoardsTab.vue       # 板块标签
│   │   ├── WatchView.vue       # 关注页面（Module 5）
│   │   └── StrategyView.vue    # 策略页面（Module 6）
│   ├── App.vue             # 根组件
│   └── main.ts             # 入口文件
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

## 2. 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 前端框架 |
| TypeScript | ^5.3 | 类型系统 |
| Vite | ^5.0 | 构建工具 |
| Pinia | ^2.1 | 状态管理 |
| Vue Router | ^4.2 | 路由管理 |
| Axios | ^1.6 | HTTP 客户端 |
| Tailwind CSS | ^3.4 | 样式框架 |
| ECharts | ^5.4 | 图表库 |

## 3. 组件规范

### 3.1 单文件组件

使用 `<script setup>` 语法：

```vue
<!-- components/IndexCard.vue -->
<template>
  <div class="index-card" @click="onClick">
    <div class="header">
      <span class="name">{{ name }}</span>
      <span class="symbol">{{ symbol }}</span>
    </div>
    <div class="price-row">
      <span class="price">{{ formatPrice(price) }}</span>
      <span :class="['change', changePct >= 0 ? 'up' : 'down']">
        {{ formatChange(changePct) }}
      </span>
    </div>
    <div class="metrics">
      <span>PE: {{ pePercentile }}%</span>
      <span>回撤: {{ currentDrawdown }}%</span>
      <ZoneBadge :zone="zone" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ZoneBadge from './ZoneBadge.vue'
import { formatPrice, formatChange } from '@/utils/format'

interface Props {
  symbol: string
  name: string
  price: number
  changePct: number
  pePercentile?: number
  currentDrawdown: number
  zone: 'undervalued' | 'neutral' | 'overvalued'
}

const props = defineProps<Props>()
const emit = defineEmits<{
  click: [symbol: string]
}>()

const onClick = () => {
  emit('click', props.symbol)
}
</script>

<style scoped>
.index-card {
  @apply bg-white rounded-lg p-4 shadow-sm;
}
.price-row .up { @apply text-red-500; }
.price-row .down { @apply text-green-500; }
</style>
```

### 3.2 Props 命名

- 定义用 `camelCase`
- 使用用 `kebab-case`

```vue
<!-- 定义 -->
const props = defineProps<{ defaultMarket: string }>()

<!-- 使用 -->
<IndexCard :default-market="'A'" />
```

### 3.3 事件命名

使用 `kebab-case`：

```vue
<!-- 定义 -->
const emit = defineEmits<{ tabChange: [tab: string] }>()

<!-- 使用 -->
<TopBar @tab-change="onTabChange" />
```

## 4. API 封装

### 4.1 请求封装

```typescript
// utils/request.ts
import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

// 请求拦截器：添加 Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data?.error)
  }
)

export default request
```

### 4.2 API 模块

```typescript
// api/market.ts
import request from '@/utils/request'

export const marketApi = {
  getOverview: () => request.get('/v3/market/overview'),
  getIndices: () => request.get('/v3/market/indices'),
  getBoards: () => request.get('/v3/market/boards'),
  getIndexDetail: (symbol: string) => request.get(`/v3/market/index/${symbol}/detail`),
  getBoardDetail: (code: string) => request.get(`/v3/market/board/${code}/detail`),
}
```

## 5. 状态管理

### 5.1 Pinia Store

```typescript
// stores/market.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { marketApi } from '@/api/market'

export const useMarketStore = defineStore('market', () => {
  // State
  const overview = ref(null)
  const indices = ref(null)
  const boards = ref(null)
  const loading = ref(false)

  // Getters
  const aShareIndices = computed(() => indices.value?.a_share || [])
  const hkIndices = computed(() => indices.value?.hk || [])
  const usIndices = computed(() => indices.value?.us || [])

  // Actions
  async function fetchOverview() {
    loading.value = true
    try {
      overview.value = await marketApi.getOverview()
    } finally {
      loading.value = false
    }
  }

  async function fetchIndices() {
    loading.value = true
    try {
      indices.value = await marketApi.getIndices()
    } finally {
      loading.value = false
    }
  }

  return {
    overview, indices, boards, loading,
    aShareIndices, hkIndices, usIndices,
    fetchOverview, fetchIndices,
  }
})
```

## 6. 路由设计

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/market',
  },
  {
    path: '/news',
    component: () => import('@/views/NewsView.vue'),
    meta: { nav: 'news' },
  },
  {
    path: '/market',
    component: () => import('@/views/MarketView.vue'),
    meta: { nav: 'market' },
    children: [
      { path: '', redirect: '/market/overview' },
      { path: 'overview', component: () => import('@/views/market/OverviewTab.vue') },
      { path: 'indices', component: () => import('@/views/market/IndicesTab.vue') },
      { path: 'boards', component: () => import('@/views/market/BoardsTab.vue') },
    ],
  },
  {
    path: '/watch',
    component: () => import('@/views/WatchView.vue'),
    meta: { nav: 'watch' },
  },
  {
    path: '/strategy',
    component: () => import('@/views/StrategyView.vue'),
    meta: { nav: 'strategy' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

## 7. 样式规范

### 7.1 颜色变量

```css
/* styles/global.css */
:root {
  --color-up: #ef4444;        /* 涨 - 红色 */
  --color-down: #22c55e;      /* 跌 - 绿色 */
  --color-undervalued: #22c55e;  /* 低估 - 绿色 */
  --color-neutral: #eab308;      /* 适中 - 黄色 */
  --color-overvalued: #ef4444;   /* 高估 - 红色 */
  --color-bg: #f5f5f5;
  --color-card: #ffffff;
  --color-text: #1f2937;
  --color-text-secondary: #6b7280;
}
```

### 7.2 Tailwind 自定义配置

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        up: '#ef4444',
        down: '#22c55e',
        zone: {
          undervalued: '#22c55e',
          neutral: '#eab308',
          overvalued: '#ef4444',
        },
      },
    },
  },
}
```

## 8. 弹窗交互

使用 Vue Teleport + 自定义 Modal 组件：

```vue
<!-- DetailModal.vue -->
<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click="onClose">
      <div class="modal-content" @click.stop>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
```

## 9. 格式化工具

```typescript
// utils/format.ts
export function formatPrice(price: number): string {
  return price.toFixed(2)
}

export function formatChange(changePct: number): string {
  const sign = changePct >= 0 ? '+' : ''
  return `${sign}${changePct.toFixed(2)}%`
}

export function formatAmount(amount: number): string {
  if (amount >= 1e12) return `${(amount / 1e12).toFixed(2)}万亿`
  if (amount >= 1e8) return `${(amount / 1e8).toFixed(2)}亿`
  if (amount >= 1e4) return `${(amount / 1e4).toFixed(2)}万`
  return amount.toFixed(2)
}

export function formatTimeAgo(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}
```
