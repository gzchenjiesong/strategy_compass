<template>
  <div class="space-y-4">
    <!-- Price Header -->
    <div class="flex items-baseline gap-3">
      <span class="text-2xl font-bold text-gray-900">{{ quote?.price?.toFixed(2) }}</span>
      <span
        :class="quote?.change_pct >= 0 ? 'text-up' : 'text-down'"
        class="text-sm font-medium"
      >
        {{ quote?.change_pct >= 0 ? '+' : '' }}{{ quote?.change_pct?.toFixed(2) }}%
      </span>
    </div>

    <!-- Valuation Metrics -->
    <div v-if="valuation" class="grid grid-cols-3 gap-2">
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-xs text-gray-500 mb-1">PE-TTM</div>
        <div class="text-sm font-bold text-gray-800">{{ valuation.pe_ttm?.toFixed(2) || '-' }}</div>
        <div class="text-xs text-gray-400">百分位 {{ valuation.pe_percentile?.toFixed(1) || '-' }}%</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-xs text-gray-500 mb-1">PB</div>
        <div class="text-sm font-bold text-gray-800">{{ valuation.pb?.toFixed(2) || '-' }}</div>
        <div class="text-xs text-gray-400">百分位 {{ valuation.pb_percentile?.toFixed(1) || '-' }}%</div>
      </div>
      <div class="bg-gray-50 rounded-lg p-3 text-center">
        <div class="text-xs text-gray-500 mb-1">估值区间</div>
        <div
          class="text-xs px-2 py-1 rounded-full inline-block"
          :class="zoneClass(valuation.zone)"
        >
          {{ zoneLabel(valuation.zone) }}
        </div>
      </div>
    </div>

    <!-- Risk Metrics -->
    <div v-if="risk" class="grid grid-cols-3 gap-2">
      <div class="text-center">
        <div class="text-xs text-gray-500">最大回撤</div>
        <div class="text-sm font-bold text-gray-800">{{ risk.max_drawdown?.toFixed(1) || '-' }}%</div>
      </div>
      <div class="text-center">
        <div class="text-xs text-gray-500">当前回撤</div>
        <div class="text-sm font-bold text-gray-800">{{ risk.current_drawdown?.toFixed(1) || '-' }}%</div>
      </div>
      <div class="text-center">
        <div class="text-xs text-gray-500">年化波动</div>
        <div class="text-sm font-bold text-gray-800">{{ risk.annualized_volatility?.toFixed(1) || '-' }}%</div>
      </div>
    </div>

    <!-- K-line Chart -->
    <div v-if="klines.length > 0" class="h-64">
      <v-chart :option="chartOption" autoresize />
    </div>
    <div v-else class="h-64 flex items-center justify-center text-gray-400 text-sm">
      加载图表中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CandlestickChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, DataZoomComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { marketApi } from '@/api/market'
import { valuationApi } from '@/api/valuation'

use([CanvasRenderer, CandlestickChart, LineChart, GridComponent, TooltipComponent, DataZoomComponent])

interface Props {
  symbol: string
  market: string
  name: string
}

const props = defineProps<Props>()

const quote = ref<any>(null)
const valuation = ref<any>(null)
const risk = ref<any>(null)
const klines = ref<any[]>([])

const chartOption = computed(() => {
  const dates = klines.value.map((k) => k.date)
  const data = klines.value.map((k) => [k.open, k.close, k.low, k.high])

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%',
      top: '5%',
    },
    xAxis: {
      type: 'category',
      data: dates,
      scale: true,
      boundaryGap: false,
      axisLine: { onZero: false },
      splitLine: { show: false },
      axisLabel: { show: false },
    },
    yAxis: {
      scale: true,
      splitLine: { show: true, lineStyle: { color: '#f0f0f0' } },
    },
    dataZoom: [
      { type: 'inside', start: 50, end: 100 },
    ],
    series: [
      {
        type: 'candlestick',
        data: data,
        itemStyle: {
          color: '#ef4444',
          color0: '#22c55e',
          borderColor: '#ef4444',
          borderColor0: '#22c55e',
        },
      },
    ],
  }
})

function zoneClass(zone: string) {
  switch (zone) {
    case 'undervalued': return 'bg-green-100 text-green-700'
    case 'overvalued': return 'bg-red-100 text-red-700'
    default: return 'bg-yellow-100 text-yellow-700'
  }
}

function zoneLabel(zone: string) {
  switch (zone) {
    case 'undervalued': return '低估'
    case 'overvalued': return '高估'
    default: return '适中'
  }
}

async function loadData() {
  try {
    const [quoteRes, klineRes, valRes] = await Promise.all([
      marketApi.getIndexQuote(props.symbol, props.market),
      marketApi.getIndexKlines(props.symbol, props.market, 500),
      valuationApi.getIndexValuation(props.symbol, 10),
    ])
    quote.value = quoteRes.data
    klines.value = klineRes.data?.items || []
    valuation.value = valRes.data?.valuation
    risk.value = valRes.data?.risk
  } catch (e) {
    console.error('Failed to load index detail:', e)
  }
}

watch(() => props.symbol, loadData, { immediate: true })
</script>
