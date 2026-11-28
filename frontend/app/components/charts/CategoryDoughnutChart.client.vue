<template>
  <div class="relative flex items-center justify-center" :style="{ height: `${height}px` }">
    <Doughnut :data="chartData" :options="chartOptions" />
    <div class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center px-4">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">{{ t('Барлығы') }}</span>
      <span class="text-sm sm:text-base font-extrabold tabular-nums text-slate-900 dark:text-white mt-0.5">
        {{ formatCurrency(totalSum) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'
import { Doughnut } from 'vue-chartjs'
import type { CategoryBreakdown } from '~~/shared/types'

ChartJS.register(ArcElement, Tooltip, Legend)

const { categoryLabel } = useLanguage()
const props = withDefaults(
  defineProps<{
    items: CategoryBreakdown[]
    height?: number
  }>(),
  {
    height: 220,
  },
)

const { formatCurrency } = useCurrencyFormat()

const totalSum = computed(() =>
  props.items.reduce((acc, item) => acc + Number(item.total || 0), 0),
)

const chartData = computed(() => ({
  labels: props.items.map(i => categoryLabel(i.category_name, 'Санатсыз')),
  datasets: [
    {
      data: props.items.map(i => Number(i.total || 0)),
      backgroundColor: props.items.map(i => getCategoryVisual(i.category_name, 'expense').hex),
      borderWidth: 0,
      hoverOffset: 6,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '72%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      backgroundColor: '#0f172a',
      titleColor: '#f8fafc',
      bodyColor: '#cbd5e1',
      padding: 12,
      cornerRadius: 10,
      callbacks: {
        label: (ctx: any) => {
          const val = Number(ctx.parsed || 0)
          return ` ${formatCurrency(val)}`
        },
      },
    },
  },
}))
</script>
