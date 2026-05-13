<template>
  <AppLayout>
    <!-- 顶部标签栏 -->
    <div class="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-4">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-1 py-2 text-sm font-medium rounded-md transition-colors"
        :class="activeTab === tab.key ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ========== 概览页 ========== -->
    <div v-if="activeTab === 'overview'" class="space-y-4">
      <!-- 估值区间分布 -->
      <section class="bg-white rounded-lg p-4 shadow-sm">
        <h3 class="text-sm font-semibold text-gray-700 mb-3">估值区间分布</h3>
        <div class="flex items-center justify-between">
          <div class="text-center flex-1">
            <div class="text-2xl font-bold text-green-600">{{ zoneSummary.undervalued }}</div>
            <div class="text-xs text-gray-500 mt-1">低估</div>
          </div>
          <div class="w-px h-10 bg-gray-100" />
          <div class="text-center flex-1">
            <div class="text-2xl font-bold text-yellow-600">{{ zoneSummary.neutral }}</div>
            <div class="text-xs text-gray-500 mt-1">适中</div>
          </div>
          <div class="w-px h-10 bg-gray-100" />
          <div class="text-center flex-1">
            <div class="text-2xl font-bold text-red-600">{{ zoneSummary.overvalued }}</div>
            <div class="text-xs text-gray-500 mt-1">高估</div>
          </div>
        </div>
      </section>

      <!-- 核心指数速览 -->
      <section>
        <h3 class="text-sm font-semibold text-gray-700 mb-2">核心指数</h3>
        <div class="grid grid-cols-2 gap-3">
          <div
            v-for="idx in coreIndices"
            :key="idx.symbol"
            class="bg-white rounded-lg p-3 shadow-sm cursor-pointer active:scale-[0.98] transition-transform"
            @click="openDetail(idx)"
          >
            <div class="flex justify-between items-center mb-1">
              <span class="text-sm font-medium text-gray-700">{{ idx.name }}</span>
              <span
                :class="idx.change_pct >= 0 ? 'text-up' : 'text-down'"
                class="text-sm font-bold"
              >
                {{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct?.toFixed(2) }}%
              </span>
            </div>
            <div class="text-lg font-bold text-gray-900">
              {{ formatPrice(idx.price) }}
            </div>
            <div class="mt-1.5 flex items-center gap-1.5 flex-wrap">
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :class="zoneClass(idx.zone)"
              >
                {{ zoneLabel(idx.zone) }}
              </span>
              <span v-if="idx.pe_percentile !== undefined && idx.pe_percentile !== null" class="text-[10px] text-gray-400">
                PE {{ idx.pe_percentile?.toFixed(0) }}%
              </span>
              <span v-else-if="idx.price_percentile !== undefined && idx.price_percentile !== null" class="text-[10px] text-gray-400">
                价格 {{ idx.price_percentile?.toFixed(0) }}%
              </span>
            </div>
          </div>
        </div>
      </section>

    </div>

    <!-- ========== 大盘页 ========== -->
    <div v-if="activeTab === 'indices'" class="space-y-5">
      <!-- A股 -->
      <section v-if="aShareIndices.length > 0">
        <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <span class="w-1 h-4 bg-red-500 rounded-full mr-2" />A股指数
        </h3>
        <div class="space-y-2">
          <div
            v-for="idx in aShareIndices"
            :key="idx.symbol"
            class="bg-white rounded-lg p-3 shadow-sm cursor-pointer active:scale-[0.98] transition-transform"
            @click="openDetail(idx)"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="text-sm font-medium text-gray-800">{{ idx.name }}</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  PE {{ idx.pe_ttm || '-' }} · PB {{ idx.pb || '-' }}
                </div>
              </div>
              <div class="text-right">
                <div class="text-base font-bold text-gray-900">{{ formatPrice(idx.price) }}</div>
                <div
                  :class="idx.change_pct >= 0 ? 'text-up' : 'text-down'"
                  class="text-xs font-medium"
                >
                  {{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct?.toFixed(2) }}%
                </div>
              </div>
            </div>
            <div class="mt-2 flex items-center gap-2">
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :class="zoneClass(idx.zone)"
              >
                {{ zoneLabel(idx.zone) }}
              </span>
              <span v-if="idx.pe_percentile !== null" class="text-[10px] text-gray-400">
                PE百分位 {{ idx.pe_percentile?.toFixed(1) }}%
              </span>
              <span v-if="idx.current_drawdown !== null" class="text-[10px] text-gray-400">
                回撤 {{ idx.current_drawdown?.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 港股 -->
      <section v-if="hkIndices.length > 0">
        <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <span class="w-1 h-4 bg-blue-500 rounded-full mr-2" />港股指数
        </h3>
        <div class="space-y-2">
          <div
            v-for="idx in hkIndices"
            :key="idx.symbol"
            class="bg-white rounded-lg p-3 shadow-sm cursor-pointer active:scale-[0.98] transition-transform"
            @click="openDetail(idx)"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="text-sm font-medium text-gray-800">{{ idx.name }}</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  价格百分位 {{ idx.price_percentile?.toFixed(1) || '-' }}%
                </div>
              </div>
              <div class="text-right">
                <div class="text-base font-bold text-gray-900">{{ formatPrice(idx.price) }}</div>
                <div
                  :class="idx.change_pct >= 0 ? 'text-up' : 'text-down'"
                  class="text-xs font-medium"
                >
                  {{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct?.toFixed(2) }}%
                </div>
              </div>
            </div>
            <div class="mt-2 flex items-center gap-2">
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :class="zoneClass(idx.zone)"
              >
                {{ zoneLabel(idx.zone) }}
              </span>
              <span v-if="idx.current_drawdown !== null" class="text-[10px] text-gray-400">
                回撤 {{ idx.current_drawdown?.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 美股 -->
      <section v-if="usIndices.length > 0">
        <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center">
          <span class="w-1 h-4 bg-purple-500 rounded-full mr-2" />美股指数
        </h3>
        <div class="space-y-2">
          <div
            v-for="idx in usIndices"
            :key="idx.symbol"
            class="bg-white rounded-lg p-3 shadow-sm cursor-pointer active:scale-[0.98] transition-transform"
            @click="openDetail(idx)"
          >
            <div class="flex justify-between items-center">
              <div>
                <div class="text-sm font-medium text-gray-800">{{ idx.name }}</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  价格百分位 {{ idx.price_percentile?.toFixed(1) || '-' }}%
                </div>
              </div>
              <div class="text-right">
                <div class="text-base font-bold text-gray-900">{{ formatPrice(idx.price) }}</div>
                <div
                  :class="idx.change_pct >= 0 ? 'text-up' : 'text-down'"
                  class="text-xs font-medium"
                >
                  {{ idx.change_pct >= 0 ? '+' : '' }}{{ idx.change_pct?.toFixed(2) }}%
                </div>
              </div>
            </div>
            <div class="mt-2 flex items-center gap-2">
              <span
                class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :class="zoneClass(idx.zone)"
              >
                {{ zoneLabel(idx.zone) }}
              </span>
              <span v-if="idx.current_drawdown !== null" class="text-[10px] text-gray-400">
                回撤 {{ idx.current_drawdown?.toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- ========== 板块页 ========== -->
    <div v-if="activeTab === 'boards'" class="space-y-4">
      <div class="bg-white rounded-lg p-8 shadow-sm text-center">
        <div class="text-4xl mb-3">📊</div>
        <h3 class="text-base font-medium text-gray-700">板块关注</h3>
        <p class="text-sm text-gray-400 mt-2">MVP 阶段，板块功能即将上线</p>
        <p class="text-xs text-gray-300 mt-1">行业板块与概念板块的估值分析</p>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <DetailModal
      :visible="detailVisible"
      :title="selectedIndex?.name || ''"
      @close="detailVisible = false"
    >
      <IndexDetail
        v-if="selectedIndex"
        :symbol="selectedIndex.symbol"
        :market="selectedIndex.market"
        :name="selectedIndex.name"
      />
    </DetailModal>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/AppLayout.vue'
import DetailModal from '@/components/DetailModal.vue'
import IndexDetail from '@/components/IndexDetail.vue'
import { marketApi } from '@/api/market'

const tabs = [
  { key: 'overview', label: '概览' },
  { key: 'indices', label: '大盘' },
  { key: 'boards', label: '板块' },
]

const activeTab = ref('overview')

// 概览页数据
const coreIndices = ref<any[]>([])
const zoneSummary = ref({ undervalued: 0, neutral: 0, overvalued: 0, total: 0 })

// 大盘页数据
const aShareIndices = ref<any[]>([])
const hkIndices = ref<any[]>([])
const usIndices = ref<any[]>([])

// 弹窗
const detailVisible = ref(false)
const selectedIndex = ref<any>(null)

onMounted(async () => {
  await fetchOverview()
  await fetchIndices()
})

async function fetchOverview() {
  try {
    const res: any = await marketApi.getOverview()
    const data = res.data
    coreIndices.value = data.core_indices || []
    zoneSummary.value = data.zone_summary || { undervalued: 0, neutral: 0, overvalued: 0, total: 0 }
  } catch (e) {
    console.error('fetchOverview error:', e)
  }
}

async function fetchIndices() {
  try {
    const res: any = await marketApi.getIndices()
    const data = res.data
    aShareIndices.value = data.a_share || []
    hkIndices.value = data.hk || []
    usIndices.value = data.us || []
  } catch (e) {
    console.error('fetchIndices error:', e)
  }
}

function openDetail(idx: any) {
  selectedIndex.value = idx
  detailVisible.value = true
}

function zoneClass(zone: string) {
  switch (zone) {
    case 'undervalued': return 'bg-green-50 text-green-600 border border-green-100'
    case 'overvalued': return 'bg-red-50 text-red-600 border border-red-100'
    default: return 'bg-yellow-50 text-yellow-600 border border-yellow-100'
  }
}

function zoneLabel(zone: string) {
  switch (zone) {
    case 'undervalued': return '低估'
    case 'overvalued': return '高估'
    default: return '适中'
  }
}

function formatPrice(price: number) {
  if (price === undefined || price === null) return '-'
  if (price >= 10000) return price.toFixed(0)
  if (price >= 1000) return price.toFixed(1)
  return price.toFixed(2)
}
</script>

<style scoped>
.text-up { color: #ef4444; }
.text-down { color: #22c55e; }
</style>
