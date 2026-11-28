<template>
  <div class="space-y-6">
    <!-- Header & Segmented Period Selector -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="sb-page-title">{{ t('Қаржылық аналитика') }}</h2>
        <p class="sb-page-caption">{{ t('Шығыстар құрылымын, үнемдеу деңгейін және айлық динамиканы талдау') }}</p>
      </div>

      <div class="inline-flex max-w-full flex-wrap self-start rounded-xl bg-[var(--sb-surface)] p-1 ring-1 ring-[var(--sb-line)]" :aria-label="t('Есеп кезеңі')">
        <button
          v-for="opt in periodOptions"
          :key="opt.value"
          type="button"
          :aria-pressed="selectedPeriod === opt.value"
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all"
          :class="
            selectedPeriod === opt.value
              ? 'bg-[var(--sb-accent-soft)] text-[var(--sb-accent)]'
              : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
          "
          @click="selectedPeriod = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('Кезеңдегі кіріс') }}</p>
        <p class="text-xl xl:text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1.5 tabular-nums truncate">
          +{{ formatCurrency(summary.total_income) }}
        </p>
      </UCard>

      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('Кезеңдегі шығыс') }}</p>
        <p class="text-xl xl:text-2xl font-extrabold text-rose-600 dark:text-rose-400 mt-1.5 tabular-nums truncate">
          -{{ formatCurrency(summary.total_expense) }}
        </p>
      </UCard>

      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('Таза үнем (дельта)') }}</p>
        <p
          class="text-xl xl:text-2xl font-extrabold mt-1.5 tabular-nums truncate"
          :class="Number(summary.net) < 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'"
        >
          {{ formatCurrency(summary.net) }}
        </p>
      </UCard>

      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('Жинақ нормасы') }}</p>
        <p class="text-xl xl:text-2xl font-extrabold text-teal-600 dark:text-teal-400 mt-1.5 tabular-nums truncate">
          {{ savingsRate.toFixed(1) }}%
        </p>
      </UCard>
    </div>

    <DeepReceiptAnalytics :month="receiptMonth" />

    <!-- Charts Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Monthly Income vs Expense Bar Chart -->
      <UCard class="lg:col-span-7">
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-bold text-base text-slate-900 dark:text-white">{{ t('Айлар бойынша кіріс пен шығыс') }}</h3>
              <p class="text-xs text-slate-500">{{ t('Айлық ақша ағынының салыстырмалы динамикасы') }}</p>
            </div>
          </div>
        </template>

        <div v-if="trends.length === 0" class="py-16 text-center text-sm text-slate-400">
          {{ t('Көрсетілген кезең бойынша айлық деректер жоқ') }}
        </div>
        <div v-else class="space-y-4">
          <ClientOnly>
            <ChartsTrendsBarChart :points="trends" :height="275" />
          </ClientOnly>
        </div>
      </UCard>

      <!-- Category Doughnut + Detailed List -->
      <UCard class="lg:col-span-5">
        <template #header>
          <div>
            <h3 class="font-bold text-base text-slate-900 dark:text-white">{{ t('Санаттар бойынша шығыс құрылымы') }}</h3>
            <p class="text-xs text-slate-500">{{ t('Ең көп жұмсалған бағыттар') }}</p>
          </div>
        </template>

        <div v-if="categories.length === 0" class="py-16 text-center text-sm text-slate-400">
          {{ t('Таңдалған кезеңде шығыстар тіркелмеген') }}
        </div>
        <div v-else class="space-y-5">
          <ClientOnly>
            <ChartsCategoryDoughnutChart :items="categories" :height="200" />
          </ClientOnly>

          <div class="space-y-3 pt-2 border-t border-slate-100 dark:border-slate-800">
            <div v-for="cat in categories" :key="cat.category_id || 'uncategorized'" class="space-y-1.5">
              <div class="flex items-center justify-between text-xs gap-2">
                <div class="flex items-center gap-2 min-w-0">
                  <span
                    class="w-2.5 h-2.5 rounded-full shrink-0"
                    :style="{ backgroundColor: getCategoryVisual(cat.category_name, 'expense').hex }"
                  />
                  <span class="font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {{ categoryLabel(cat.category_name, 'Санатсыз') }}
                  </span>
                </div>
                <span class="tabular-nums text-slate-500 shrink-0">
                  <strong class="text-slate-800 dark:text-slate-200">{{ formatCurrency(cat.total) }}</strong>
                  ({{ cat.percentage.toFixed(1) }}%)
                </span>
              </div>
              <UProgress :value="cat.percentage" color="primary" size="xs" />
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

const { t, categoryLabel, monthLabel } = useLanguage()
const analytics = useAnalytics()
const route = useRoute()
type AnalyticsPeriod = 'month' | '3months' | 'year' | 'receipt-month'
const receiptMonth = computed(() => {
  const month = route.query.month
  return typeof month === 'string' && /^[1-9]\d{3}-(0[1-9]|1[0-2])$/.test(month) ? month : ''
})
const selectedPeriod = ref<AnalyticsPeriod>(receiptMonth.value ? 'receipt-month' : 'month')

const periodOptions = computed<{ label: string; value: AnalyticsPeriod }[]>(() => [
  { label: t('Осы ай'), value: 'month' },
  { label: t('Соңғы 3 ай'), value: '3months' },
  { label: t('Осы жыл'), value: 'year' },
  ...(receiptMonth.value ? [{ label: monthLabel(receiptMonth.value), value: 'receipt-month' as const }] : []),
])

const categories = ref<CategoryBreakdown[]>([])
const trends = ref<TrendPoint[]>([])
let loadVersion = 0
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

function periodRange(period: AnalyticsPeriod) {
  const now = dayjs()
  if (period === 'receipt-month' && receiptMonth.value) {
    const date = dayjs(`${receiptMonth.value}-01`)
    return { date_from: date.format('YYYY-MM-DD'), date_to: date.endOf('month').format('YYYY-MM-DD'), months: 6 }
  }
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
  const version = ++loadVersion
  const { date_from, date_to, months } = periodRange(selectedPeriod.value)
  const [sumRes, catRes, trendRes] = await Promise.allSettled([
    analytics.getSummary({ date_from, date_to }),
    analytics.getByCategory({ date_from, date_to }),
    analytics.getTrends({ months }),
  ])
  if (version !== loadVersion) return
  if (sumRes.status === 'fulfilled') summary.value = sumRes.value
  if (catRes.status === 'fulfilled') categories.value = catRes.value
  if (trendRes.status === 'fulfilled') trends.value = trendRes.value
}

watch(receiptMonth, month => { selectedPeriod.value = month ? 'receipt-month' : 'month' })
watch([selectedPeriod, receiptMonth], loadAnalytics)
onMounted(loadAnalytics)
</script>
