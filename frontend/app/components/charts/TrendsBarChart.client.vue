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

const props = withDefaults(
  defineProps<{
    points: TrendPoint[]
    height?: number
  }>(),
  {
    height: 270,
  },
)

const colorMode = useColorMode()
const { formatCurrency } = useCurrencyFormat()

const chartData = computed(() => ({
  labels: props.points.map(p => formatKzMonth(p.month)),
  datasets: [
    {
      label: 'Кіріс',
      data: props.points.map(p => Number(p.income || 0)),
      backgroundColor: '#10b981',
      borderRadius: 8,
      maxBarThickness: 32,
    },
    {
      label: 'Шығыс',
      data: props.points.map(p => Number(p.expense || 0)),
      backgroundColor: '#f43f5e',
      borderRadius: 8,
      maxBarThickness: 32,
    },
  ],
}))

const chartOptions = computed(() => {
  const isDark = colorMode.value === 'dark'
  const tickColor = isDark ? '#94a3b8' : '#64748b'
  const gridColor = isDark ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)'

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
          font: { size: 12, weight: 600 },
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
        ticks: { color: tickColor, font: { size: 11 } },
      },
      y: {
        beginAtZero: true,
        grid: { color: gridColor },
        ticks: {
          color: tickColor,
          font: { size: 11 },
          callback: (val: any) => formatCurrency(Number(val)),
        },
      },
    },
  }
})
</script>
