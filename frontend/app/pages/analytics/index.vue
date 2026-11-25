<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Финансовая аналитика</h2>
        <p class="text-sm text-gray-500">Глубокий анализ структуры трат и динамики накоплений</p>
      </div>
      <div class="flex gap-2">
        <USelect
          v-model="selectedPeriod"
          :options="[
            { label: 'Текущий месяц', value: 'month' },
            { label: 'Последние 3 месяца', value: '3months' },
            { label: 'Текущий год', value: 'year' },
          ]"
        />
      </div>
    </div>

    <!-- Analytics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard>
        <p class="text-sm text-gray-500">Всего доходов за период</p>
        <p class="text-2xl font-bold text-green-600 mt-1">{{ formatCurrency(summary.total_income) }}</p>
      </UCard>
      <UCard>
        <p class="text-sm text-gray-500">Всего расходов за период</p>
        <p class="text-2xl font-bold text-rose-600 mt-1">{{ formatCurrency(summary.total_expense) }}</p>
      </UCard>
      <UCard>
        <p class="text-sm text-gray-500">Чистая экономия (дельта)</p>
        <p class="text-2xl font-bold text-emerald-600 mt-1">{{ formatCurrency(summary.net) }}</p>
      </UCard>
      <UCard>
        <p class="text-sm text-gray-500">Норма сбережений</p>
        <p class="text-2xl font-bold text-teal-600 mt-1">{{ savingsRate.toFixed(1) }}%</p>
      </UCard>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Category Breakdown Table -->
      <UCard>
        <template #header>
          <h3 class="font-bold text-base">Структура расходов по категориям</h3>
        </template>
        <div v-if="categories.length === 0" class="py-8 text-center text-gray-400">
          Нет данных за выбранный период
        </div>
        <div v-else class="space-y-4">
          <div v-for="cat in categories" :key="cat.category_id || 'uncategorized'" class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="font-medium">{{ cat.category_name || 'Без категории' }}</span>
              <span class="text-gray-500">{{ formatCurrency(cat.total) }} ({{ cat.percentage.toFixed(1) }}%)</span>
            </div>
            <UProgress :value="cat.percentage" color="emerald" size="sm" />
          </div>
        </div>
      </UCard>

      <!-- Monthly Trends -->
      <UCard>
        <template #header>
          <h3 class="font-bold text-base">Тренды доходов и расходов по месяцам</h3>
        </template>
        <div v-if="trends.length === 0" class="py-8 text-center text-gray-400">
          Нет данных по месяцам
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="point in trends"
            :key="point.month"
            class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60 flex items-center justify-between text-sm"
          >
            <span class="font-semibold">{{ point.month }}</span>
            <div class="flex items-center gap-4 text-xs sm:text-sm">
              <span class="text-green-600 font-medium">+{{ formatCurrency(point.income) }}</span>
              <span class="text-rose-600 font-medium">-{{ formatCurrency(point.expense) }}</span>
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { CategoryBreakdown, TrendPoint } from '~~/shared/types'

const analytics = useAnalytics()
const selectedPeriod = ref<'month' | '3months' | 'year'>('month')
const categories = ref<CategoryBreakdown[]>([])
const trends = ref<TrendPoint[]>([])
const summary = ref({
  total_income: 0,
  total_expense: 0,
  net: 0,
  transactions_count: 0,
})

const savingsRate = computed(() => {
  const income = Number(summary.value.total_income)
  return income > 0 ? (Number(summary.value.net) / income) * 100 : 0
})

const { formatCurrency } = useCurrencyFormat()

function periodRange(period: 'month' | '3months' | 'year') {
  const now = dayjs()
  if (period === '3months') {
    return {
      date_from: now.subtract(2, 'month').startOf('month').format('YYYY-MM-DD'),
      date_to: now.endOf('month').format('YYYY-MM-DD'),
      months: 3,
    }
  }
  if (period === 'year') {
    return {
      date_from: now.startOf('year').format('YYYY-MM-DD'),
      date_to: now.endOf('year').format('YYYY-MM-DD'),
      months: 12,
    }
  }
  return {
    date_from: now.startOf('month').format('YYYY-MM-DD'),
    date_to: now.endOf('month').format('YYYY-MM-DD'),
    months: 6,
  }
}

const loadAnalytics = async () => {
  const { date_from, date_to, months } = periodRange(selectedPeriod.value)
  const [sumRes, catRes, trendRes] = await Promise.allSettled([
    analytics.getSummary({ date_from, date_to }),
    analytics.getByCategory({ date_from, date_to }),
    analytics.getTrends({ months }),
  ])
  if (sumRes.status === 'fulfilled') summary.value = sumRes.value
  if (catRes.status === 'fulfilled') categories.value = catRes.value
  if (trendRes.status === 'fulfilled') trends.value = trendRes.value
}

watch(selectedPeriod, loadAnalytics)
onMounted(loadAnalytics)
</script>
