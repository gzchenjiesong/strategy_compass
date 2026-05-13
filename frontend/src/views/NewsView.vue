<template>
  <AppLayout>
    <!-- 统计栏 -->
    <div class="flex items-center justify-between bg-white rounded-lg p-3 shadow-sm mb-3">
      <div class="flex items-center space-x-4 text-xs text-gray-500">
        <span>今日 <b class="text-gray-800">{{ stats.today }}</b></span>
        <span>重要 <b class="text-red-500">{{ stats.important }}</b></span>
        <span>宏观 <b class="text-blue-500">{{ stats.macro }}</b></span>
      </div>
      <button
        @click="refresh"
        class="text-xs text-blue-500 flex items-center space-x-1"
        :class="{ 'opacity-50': loading }"
        :disabled="loading"
      >
        <svg class="w-3 h-3" :class="{ 'animate-spin': loading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span>{{ loading ? '刷新中' : '刷新' }}</span>
      </button>
    </div>

    <!-- 分类筛选 -->
    <div class="flex space-x-2 mb-3 overflow-x-auto pb-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
        :class="activeTab === tab.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 宏观：卡片式利率展示 -->
    <div v-if="activeTab === 'macro'" class="space-y-4">
      <div v-for="group in groupedMacroEvents" :key="group.country" class="bg-white rounded-lg shadow-sm overflow-hidden">
        <!-- 国家头部 -->
        <div class="px-4 py-2.5 bg-gray-50 border-b border-gray-100 flex items-center gap-2">
          <span class="text-lg">{{ group.flag }}</span>
          <span class="text-sm font-semibold text-gray-800">{{ group.countryName }}</span>
        </div>
        <!-- 利率事件列表 -->
        <div
          v-for="event in group.events"
          :key="event.id"
          class="px-4 py-3 border-b border-gray-50 last:border-b-0 cursor-pointer active:bg-gray-50"
          @click="openDetail(event)"
        >
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-sm font-medium text-gray-800">{{ event.event_name }}</span>
            <span
              v-if="!event.is_released"
              class="shrink-0 px-1.5 py-0.5 bg-red-50 text-red-500 text-[10px] rounded font-medium"
            >
              预计
            </span>
          </div>
          <!-- 已发布：显示实际值 -->
          <div v-if="event.is_released" class="flex items-baseline gap-1">
            <span class="text-2xl font-bold text-gray-900">{{ event.actual_value || '-' }}</span>
            <span v-if="event.unit" class="text-sm text-gray-400">{{ event.unit }}</span>
          </div>
          <!-- 已发布：预测值 / 前值 -->
          <div v-if="event.is_released" class="mt-1.5 flex items-center gap-4 text-xs text-gray-500">
            <span>预测 <b class="text-gray-700">{{ event.forecast_value || '-' }}</b></span>
            <span>前值 <b class="text-gray-700">{{ event.previous_value || '-' }}</b></span>
          </div>
          <!-- 未发布：预计时间 -->
          <div v-else class="flex items-center gap-1 text-xs text-red-400">
            <span>📅 {{ formatEventDate(event) }}</span>
            <span class="text-gray-300 mx-1">·</span>
            <span class="text-gray-400">前值 <b class="text-gray-700">{{ event.previous_value || '-' }}</b></span>
          </div>
          <!-- 已发布日期 -->
          <div v-if="event.is_released" class="mt-1 text-[11px] text-gray-400">
            更新于 {{ event.event_date }}
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="groupedMacroEvents.length === 0 && !loading" class="text-center text-gray-400 py-8">
        暂无利率数据
      </div>
    </div>

    <!-- 资讯列表（全部 / 重要） -->
    <div v-else class="space-y-2">
      <div
        v-for="item in newsList"
        :key="item.id"
        class="bg-white rounded-lg p-3 shadow-sm cursor-pointer active:scale-[0.99] transition-transform"
        :class="cardBorderClass(item)"
        @click="openDetail(item)"
      >
        <div class="flex items-start justify-between gap-2">
          <p
            class="text-sm leading-relaxed flex-1 line-clamp-3"
            :class="(item.importance || 0) >= 3 ? 'text-gray-900 font-medium' : 'text-gray-700'"
            v-html="highlightKeywords(item.title)"
          />
          <span
            v-if="(item.importance || 0) >= 3"
            class="shrink-0 px-1.5 py-0.5 bg-red-50 text-red-500 text-[10px] rounded font-medium"
          >
            重要
          </span>
        </div>
        <div class="mt-2 flex items-center justify-between">
          <span class="text-[11px] text-gray-400">{{ formatTime(item.publish_time) }}</span>
          <span class="text-[11px] text-gray-300">{{ formatSource(item.source) }}</span>
        </div>
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="text-center py-3">
        <button
          @click="loadMore"
          class="text-xs text-blue-500"
          :class="{ 'opacity-50': loadingMore }"
          :disabled="loadingMore"
        >
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>

      <!-- 空状态 -->
      <div v-if="newsList.length === 0 && !loading" class="text-center text-gray-400 py-8">
        暂无资讯
      </div>
    </div>

    <!-- 详情浮窗 -->
    <DetailModal
      :visible="modalVisible"
      :title="modalTitle"
      @close="modalVisible = false"
    >
      <div v-if="selectedItem" class="space-y-3">
        <!-- 宏观事件详情 -->
        <template v-if="selectedItem.is_macro">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span v-if="!selectedItem.is_released" class="px-2 py-0.5 bg-red-50 text-red-500 text-xs rounded">预计</span>
              <span class="text-xs text-gray-400">{{ eventTypeLabel(selectedItem.event_type) }} · {{ countryLabel(selectedItem.country) }}</span>
            </div>
            <p class="text-sm leading-relaxed text-gray-800 font-medium">{{ selectedItem.event_name }}</p>
            <div class="grid grid-cols-3 gap-2 text-center py-2 bg-gray-50 rounded">
              <div>
                <div class="text-[10px] text-gray-400">实际值</div>
                <div class="text-sm font-medium text-gray-800">{{ selectedItem.actual_value || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-400">预测值</div>
                <div class="text-sm font-medium text-gray-800">{{ selectedItem.forecast_value || '-' }}</div>
              </div>
              <div>
                <div class="text-[10px] text-gray-400">前值</div>
                <div class="text-sm font-medium text-gray-800">{{ selectedItem.previous_value || '-' }}</div>
              </div>
            </div>
            <p class="text-xs text-gray-400">发布时间: {{ selectedItem.event_date }}</p>
          </div>
        </template>

        <!-- 新闻详情 -->
        <template v-else>
          <p
            class="text-sm leading-relaxed text-gray-800"
            v-html="highlightKeywords(selectedItem.title)"
          />
          <div class="flex items-center justify-between pt-2 border-t border-gray-100">
            <span class="text-xs text-gray-400">来源：{{ formatSource(selectedItem.source) }}</span>
            <span
              v-if="(selectedItem.importance || 0) >= 3"
              class="px-1.5 py-0.5 bg-red-50 text-red-500 text-[10px] rounded font-medium"
            >
              重要
            </span>
          </div>
        </template>
      </div>
    </DetailModal>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import DetailModal from '@/components/DetailModal.vue'
import { newsApi } from '@/api/news'

interface NewsItem {
  id: string
  type: string
  source: string
  title: string
  content?: string
  url?: string
  publish_time: string
  importance?: number
  is_macro: boolean
  is_released?: boolean
  event_date?: string
  event_name?: string
  event_type?: string
  country?: string
  actual_value?: string
  forecast_value?: string
  previous_value?: string
  unit?: string
}

interface CountryGroup {
  country: string
  countryName: string
  flag: string
  events: NewsItem[]
}

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'important', label: '重要' },
  { key: 'macro', label: '宏观' },
]

const activeTab = ref('all')
const newsList = ref<NewsItem[]>([])
const macroEvents = ref<NewsItem[]>([])
const hasMore = ref(false)
const nextBeforeId = ref<string | null>(null)
const loading = ref(false)
const loadingMore = ref(false)
const stats = ref({ total: 0, today: 0, important: 0, macro: 0 })

const modalVisible = ref(false)
const selectedItem = ref<NewsItem | null>(null)

const modalTitle = computed(() => {
  if (!selectedItem.value) return ''
  if (selectedItem.value.is_macro) {
    return selectedItem.value.event_date || ''
  }
  return formatTime(selectedItem.value.publish_time)
})

// 国家分组：国旗 + 中文名
const countryMeta: Record<string, { name: string; flag: string }> = {
  USA: { name: '美国', flag: '🇺🇸' },
  CHN: { name: '中国', flag: '🇨🇳' },
  EUR: { name: '欧元区', flag: '🇪🇺' },
  JPN: { name: '日本', flag: '🇯🇵' },
  GBR: { name: '英国', flag: '🇬🇧' },
}

// 按国家分组宏观事件
const groupedMacroEvents = computed<CountryGroup[]>(() => {
  const map = new Map<string, NewsItem[]>()
  for (const item of macroEvents.value) {
    const key = item.country || 'UNKNOWN'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(item)
  }
  const groups: CountryGroup[] = []
  for (const [country, events] of map) {
    const meta = countryMeta[country] || { name: country, flag: '🏳️' }
    // 已发布排前面，未发布排后面
    events.sort((a, b) => {
      if (a.is_released && !b.is_released) return -1
      if (!a.is_released && b.is_released) return 1
      return 0
    })
    groups.push({ country, countryName: meta.name, flag: meta.flag, events })
  }
  return groups
})

function cardBorderClass(item: NewsItem): string {
  return item.importance && item.importance >= 3 ? 'border-l-4 border-red-400' : ''
}

function eventTypeLabel(type?: string): string {
  const map: Record<string, string> = {
    interest_rate: '央行',
    economic_data: '数据',
    policy: '政策',
  }
  return map[type || ''] || type || ''
}

function countryLabel(country?: string): string {
  return countryMeta[country || '']?.name || country || ''
}

function formatEventDate(item: NewsItem): string {
  const date = item.event_date || ''
  if (!item.is_released) {
    const d = new Date(date)
    const now = new Date()
    const diff = d.getTime() - now.getTime()
    const days = Math.ceil(diff / 86400000)
    if (days <= 0) return '今天'
    if (days === 1) return '明天'
    return `预计 ${days}天后`
  }
  const d = new Date(date)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

async function fetchNews(isLoadMore = false) {
  if (isLoadMore) {
    loadingMore.value = true
  } else {
    loading.value = true
  }

  try {
    const params: any = { limit: 30, filter: activeTab.value }
    if (isLoadMore && nextBeforeId.value) {
      params.before_id = nextBeforeId.value
    }

    const res: any = await newsApi.getNews(params)
    const data = res.data

    if (isLoadMore) {
      newsList.value.push(...(data.items || []))
    } else {
      newsList.value = data.items || []
    }

    hasMore.value = data.has_more
    nextBeforeId.value = data.next_before_id
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function fetchMacroEvents() {
  loading.value = true
  try {
    const res: any = await newsApi.getMacroEvents({ limit: 30 })
    macroEvents.value = res.data?.items || []
  } catch (e) {
    console.error('fetchMacroEvents failed:', e)
    macroEvents.value = []
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res: any = await newsApi.getStats()
    stats.value = res.data
  } catch (e) {
    console.error(e)
  }
}

function loadMore() {
  if (!hasMore.value || loadingMore.value) return
  fetchNews(true)
}

function refresh() {
  nextBeforeId.value = null
  if (activeTab.value === 'macro') {
    fetchMacroEvents()
  } else {
    fetchNews(false)
  }
  fetchStats()
}

function openDetail(item: NewsItem) {
  selectedItem.value = item
  modalVisible.value = true
}

function formatSource(source: string) {
  const map: Record<string, string> = {
    jin10: '金十',
    akshare: '数据',
    predicted: '预测',
  }
  return map[source] || source
}

function formatTime(time: string) {
  if (!time) return ''
  const d = new Date(time.replace(' ', 'T'))
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${d.getMonth() + 1}-${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function highlightKeywords(text: string) {
  return text || ''
}

watch(activeTab, (val) => {
  nextBeforeId.value = null
  if (val === 'macro') {
    fetchMacroEvents()
  } else {
    fetchNews(false)
  }
})

onMounted(() => {
  fetchNews(false)
  fetchStats()
})
</script>
