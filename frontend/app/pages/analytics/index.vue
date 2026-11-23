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
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
    </div>

    <!-- Category Breakdown Table -->
    <UCard>
      <template #header>
        <h3 class="font-bold text-base">Структура расходов по категориям</h3>
      </template>
      <div v-if="categories.length === 0" class="py-8 text-center text-gray-400">
        Нет данных за выбранный период
      </div>
      <div v-else class="space-y-4">
        <div v-for="cat in categories" :key="cat.category_id" class="space-y-1">
          <div class="flex justify-between text-sm">
            <span class="font-medium">{{ cat.category_name || 'Без категории' }}</span>
            <span class="text-gray-500">{{ formatCurrency(cat.total) }} ({{ cat.percentage.toFixed(1) }}%)</span>
          </div>
          <UProgress :value="cat.percentage" color="emerald" size="sm" />
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import type { CategoryBreakdown } from '~~/shared/types'

const analytics = useAnalytics()
const selectedPeriod = ref('month')
const categories = ref<CategoryBreakdown[]>([])
const summary = ref({
  total_income: 0,
  total_expense: 0,
  net: 0,
  transactions_count: 0,
})

const { formatCurrency } = useCurrencyFormat()

onMounted(async () => {
  try {
    const [sumData, catData] = await Promise.all([
      analytics.getSummary(),
      analytics.getByCategory(),
    ])
    if (sumData) summary.value = sumData
    if (catData) categories.value = catData
  } catch {
    // defaults
  }
})
</script>
