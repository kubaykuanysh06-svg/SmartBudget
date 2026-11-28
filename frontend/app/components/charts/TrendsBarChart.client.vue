<template>
  <div class="relative w-full" :style="{ height: `${height}px` }">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import type { TrendPoint } from '~~/shared/types'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const { t, locale, monthLabel } = useLanguage()
const props = withDefaults(
  defineProps<{
    points: TrendPoint[]
    height?: number
    compact?: boolean
  }>(),
  {
    height: 270,
  },
)

const colorMode = useColorMode()
const { formatCurrency } = useCurrencyFormat()
const tickNumber = computed(() => new Intl.NumberFormat(locale.value, { notation: 'compact', maximumFractionDigits: 1 }))

const chartData = computed(() => ({
  labels: props.points.map(p => monthLabel(p.month, props.compact)),
  datasets: [
    {
      label: t('Кіріс'),
      data: props.points.map(p => Number(p.income || 0)),
      backgroundColor: '#43b995',
      borderRadius: 5,
      maxBarThickness: 32,
    },
    {
      label: t('Шығыс'),
      data: props.points.map(p => Number(p.expense || 0)),
      backgroundColor: '#8960ed',
      borderRadius: 5,
      maxBarThickness: 32,
    },
  ],
}))

const chartOptions = computed(() => {
  const isDark = colorMode.value === 'dark'
  const tickColor = isDark ? '#aca5c3' : '#625e78'
  const gridColor = isDark ? '#ffffff13' : '#ece9f6'

  return {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        align: 'end' as const,
        labels: {
          color: tickColor,
          usePointStyle: true,
          pointStyle: 'circle',
          boxWidth: 8,
          font: { size: props.compact ? 10 : 12, weight: 600 },
        },
      },
      tooltip: {
        backgroundColor: '#0f172a',
        titleColor: '#f8fafc',
        bodyColor: '#e2e8f0',
        padding: 12,
        cornerRadius: 10,
        callbacks: {
          label: (ctx: any) => ` ${ctx.dataset.label}: ${formatCurrency(Number(ctx.parsed?.y || 0))}`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: { color: tickColor, font: { size: props.compact ? 9 : 11 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: gridColor },
        ticks: {
          color: tickColor,
          font: { size: props.compact ? 9 : 11 },
          maxTicksLimit: props.compact ? 4 : 7,
          callback: (val: string | number) => props.compact ? tickNumber.value.format(Number(val)) : formatCurrency(Number(val)),
        },
      },
    },
  }
})
</script>
