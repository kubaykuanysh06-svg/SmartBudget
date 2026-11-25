<template>
  <div class="space-y-6">
    <!-- Stat Cards Overview -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm text-gray-500 font-medium">Баланс за месяц</p>
            <p class="text-xl xl:text-2xl font-bold mt-1 text-emerald-600 dark:text-emerald-400 truncate">
              {{ formatCurrency(summary.net) }}
            </p>
          </div>
          <div class="p-3 shrink-0 bg-emerald-100 dark:bg-emerald-950/60 rounded-xl text-emerald-600">
            <UIcon name="i-heroicons-scale" class="w-6 h-6" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm text-gray-500 font-medium">Доходы</p>
            <p class="text-xl xl:text-2xl font-bold mt-1 text-green-600 truncate">
              +{{ formatCurrency(summary.total_income) }}
            </p>
          </div>
          <div class="p-3 shrink-0 bg-green-100 dark:bg-green-950/60 rounded-xl text-green-600">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-6 h-6" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm text-gray-500 font-medium">Расходы</p>
            <p class="text-xl xl:text-2xl font-bold mt-1 text-rose-600 truncate">
              -{{ formatCurrency(summary.total_expense) }}
            </p>
          </div>
          <div class="p-3 shrink-0 bg-rose-100 dark:bg-rose-950/60 rounded-xl text-rose-600">
            <UIcon name="i-heroicons-arrow-trending-down" class="w-6 h-6" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-sm text-gray-500 font-medium">Норма сбережений</p>
            <p class="text-xl xl:text-2xl font-bold mt-1 text-teal-600 truncate">
              {{ savingsRate.toFixed(1) }}%
            </p>
          </div>
          <div class="p-3 shrink-0 bg-teal-100 dark:bg-teal-950/60 rounded-xl text-teal-600">
            <UIcon name="i-heroicons-banknotes" class="w-6 h-6" />
          </div>
        </div>
      </UCard>
    </div>

    <!-- AI Insights Banner -->
    <div v-if="aiInsights.insights.value.length > 0" class="p-4 rounded-xl border border-teal-200 dark:border-teal-900 bg-teal-50/60 dark:bg-teal-950/30 flex items-start gap-4">
      <div class="p-2 rounded-lg bg-teal-500 text-white shrink-0 mt-0.5">
        <UIcon name="i-heroicons-sparkles" class="w-5 h-5" />
      </div>
      <div class="flex-1">
        <h3 class="font-semibold text-teal-900 dark:text-teal-200">
          {{ aiInsights.insights.value[0].title }}
        </h3>
        <p class="text-sm text-teal-700 dark:text-teal-300 mt-1">
          {{ aiInsights.insights.value[0].content }}
        </p>
      </div>
      <UButton
        size="xs"
        color="teal"
        variant="outline"
        label="Все советы"
        @click="navigateTo('/ai')"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Transactions -->
      <div class="lg:col-span-2 space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold">Последние покупки</h2>
          <NuxtLink to="/transactions" class="text-sm text-emerald-600 hover:underline">
            Смотреть все →
          </NuxtLink>
        </div>

        <UCard :ui="{ body: { padding: 'p-0 sm:p-0' } }">
          <div v-if="transactions.transactions.value.length === 0" class="py-12 text-center text-gray-400">
            <UIcon name="i-heroicons-receipt-percent" class="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Пока нет транзакций</p>
            <UButton
              class="mt-3"
              size="xs"
              color="emerald"
              label="Добавить первую"
              @click="navigateTo('/transactions')"
            />
          </div>
          <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
            <div
              v-for="item in transactions.transactions.value.slice(0, 5)"
              :key="item.id"
              class="p-4 flex items-center justify-between hover:bg-gray-50/50 dark:hover:bg-gray-800/40 transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xl">
                  {{ item.category?.icon || (item.type === 'income' ? '💰' : '🛒') }}
                </div>
                <div>
                  <p class="font-medium text-sm">{{ item.description || 'Без описания' }}</p>
                  <p class="text-xs text-gray-400">{{ item.merchant || item.category?.name || 'Без категории' }}</p>
                </div>
              </div>
              <div class="text-right">
                <p
                  class="font-semibold text-sm"
                  :class="item.type === 'income' ? 'text-green-600' : 'text-rose-600'"
                >
                  {{ item.type === 'income' ? '+' : '-' }}{{ formatCurrency(item.amount) }}
                </p>
                <p class="text-xs text-gray-400">{{ formatDate(item.transaction_date) }}</p>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Budgets Quick View -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold">Бюджеты</h2>
          <NuxtLink to="/budgets" class="text-sm text-emerald-600 hover:underline">
            Все бюджеты →
          </NuxtLink>
        </div>

        <UCard>
          <div v-if="budgets.budgets.value.length === 0" class="py-8 text-center text-gray-400">
            <p class="text-sm">Бюджеты ещё не настроены</p>
            <UButton
              class="mt-3"
              size="xs"
              color="emerald"
              variant="soft"
              label="Создать бюджет"
              @click="navigateTo('/budgets')"
            />
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="b in budgets.budgets.value.slice(0, 4)"
              :key="b.id"
              class="space-y-1.5"
            >
              <div class="flex items-center justify-between text-xs">
                <span class="font-medium">{{ b.category?.name || 'Общий' }}</span>
                <span class="text-gray-500">
                  {{ formatCurrency(b.spent) }} / {{ formatCurrency(b.limit_amount) }}
                </span>
              </div>
              <UProgress
                :value="Math.min(b.percentage, 100)"
                :color="b.percentage > 90 ? 'rose' : b.percentage > 70 ? 'amber' : 'emerald'"
                size="sm"
              />
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'

const transactions = useTransactions()
const budgets = useBudgets()
const aiInsights = useAiInsights()
const analytics = useAnalytics()

const summary = ref({
  total_income: 0,
  total_expense: 0,
  net: 0,
  transactions_count: 0,
})

const savingsRate = computed(() => {
  const income = Number(summary.value.total_income)
  return income ? Number(summary.value.net) / income * 100 : 0
})

const { formatCurrency } = useCurrencyFormat()

const formatDate = (val: string) => {
  return dayjs(val).format('DD MMM')
}

onMounted(async () => {
  const [summaryResult] = await Promise.allSettled([
    analytics.getSummary({
      date_from: dayjs().startOf('month').format('YYYY-MM-DD'),
      date_to: dayjs().endOf('month').format('YYYY-MM-DD'),
    }),
    transactions.fetchTransactions({ per_page: 10 }),
    budgets.fetchBudgets(),
    aiInsights.fetchInsights(),
  ])
  if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value
})
</script>
