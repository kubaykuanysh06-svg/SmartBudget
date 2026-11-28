<template>
  <div class="sb-dashboard">
    <section class="sb-overview-head">
      <div>
        <h1 class="sb-page-title">{{ t('Қаржы шолуы') }}</h1>
        <p class="sb-page-caption">{{ t('Осы айдағы кіріс, шығыс және бюджет жағдайы') }}</p>
      </div>
      <span class="sb-date"><UIcon name="i-heroicons-calendar-days" class="h-4 w-4" />{{ currentMonthLabel }}</span>
    </section>

    <div class="sb-overview-grid">
      <section class="sb-balance" aria-labelledby="balance-title">
        <div class="sb-orbit" aria-hidden="true" />
        <div class="sb-orbit-small" aria-hidden="true" />
        <p id="balance-title" class="sb-balance-label"><UIcon name="i-heroicons-wallet" class="h-4 w-4" /> {{ t('Айлық таза қалдық') }}</p>
        <p class="sb-balance-amount" :class="{ 'text-rose-100': Number(summary.net) < 0 }">
          {{ isLoading ? '—' : formatCurrency(summary.net) }}
        </p>
        <div class="sb-hero-actions">
          <NuxtLink to="/transactions?action=upload" class="sb-hero-action sb-hero-action-main">
            <UIcon name="i-heroicons-document-arrow-up" class="h-4 w-4" /> {{ t('Чек жүктеу') }}
          </NuxtLink>
          <NuxtLink to="/budgets" class="sb-hero-action">
            <UIcon name="i-heroicons-chart-pie" class="h-4 w-4" /> {{ t('Бюджет орнату') }}
          </NuxtLink>
        </div>
      </section>
      <section class="sb-panel sb-movement" aria-labelledby="movement-title">
        <div class="mb-2.5 flex items-start justify-between gap-3">
          <div>
            <h2 id="movement-title" class="sb-section-title">{{ t('Ақша қозғалысы') }}</h2>
            <p class="sb-muted mt-0.5 text-xs">{{ t('Соңғы алты ай') }}</p>
          </div>
          <NuxtLink to="/analytics" class="sb-text-link mt-1">{{ t('Аналитика') }} <UIcon name="i-heroicons-arrow-up-right" class="h-3.5 w-3.5" /></NuxtLink>
        </div>
        <ClientOnly v-if="hasMovement">
          <ChartsTrendsBarChart :points="trends" :height="177" compact />
        </ClientOnly>
        <div v-else class="sb-chart-idle">
          <span>{{ isLoading ? t('Деректер жүктелуде…') : t('График операция қосылғанда шығады') }}</span>
        </div>
      </section>
    </div>

    <div class="sb-kpi-grid" :aria-label="t('Айлық көрсеткіштер')">
      <section v-for="metric in metrics" :key="metric.label" class="sb-panel sb-kpi">
        <span class="sb-icon-box" :data-tone="metric.tone"><UIcon :name="metric.icon" class="h-[18px] w-[18px]" /></span>
        <div class="min-w-0">
          <p class="sb-kpi-label">{{ metric.label }}</p>
          <p class="sb-kpi-value mt-0.5">{{ isLoading ? '—' : metric.value }}</p>
        </div>
      </section>
    </div>

    <p v-if="loadError" role="alert" class="rounded-xl bg-amber-50 px-4 py-3 text-sm font-medium text-amber-900 dark:bg-amber-950 dark:text-amber-200">
      {{ t('Айлық деректерді жүктеу мүмкін болмады.') }}
      <button type="button" class="underline" @click="loadDashboard">{{ t('Қайталау') }}</button>
    </p>

    <div class="sb-detail-grid">
      <div class="grid gap-4">
        <section v-if="aiInsights.insights.value[0]" class="sb-panel flex items-start gap-3 p-4">
          <span class="sb-icon-box"><UIcon name="i-heroicons-sparkles" class="h-5 w-5" /></span>
          <div class="min-w-0 flex-1">
            <h2 class="sb-section-title">{{ aiInsights.insights.value[0].title }}</h2>
            <p class="sb-muted mt-1 text-sm">{{ aiInsights.insights.value[0].content }}</p>
            <NuxtLink to="/ai" class="sb-text-link mt-2">{{ t('ЖИ көмекшіге ашу') }} <UIcon name="i-heroicons-arrow-right" class="h-3.5 w-3.5" /></NuxtLink>
          </div>
        </section>
        <section class="sb-panel" aria-labelledby="recent-title">
          <div class="sb-panel-head">
            <h2 id="recent-title" class="sb-section-title">{{ t('Соңғы операциялар') }}</h2>
            <NuxtLink to="/transactions" class="sb-text-link">{{ t('Барлығын көру') }} <UIcon name="i-heroicons-arrow-right" class="h-3.5 w-3.5" /></NuxtLink>
          </div>
          <div v-if="!transactions.transactions.value.length" class="sb-empty">
            <span class="sb-icon-box"><UIcon name="i-heroicons-arrows-right-left" class="h-5 w-5" /></span>
            <p class="text-sm font-semibold">{{ isLoading ? t('Операциялар жүктелуде…') : t('Әзірге операциялар жоқ') }}</p>
            <NuxtLink v-if="!isLoading" to="/transactions?action=new" class="sb-text-link">{{ t('Операция қосу') }} <UIcon name="i-heroicons-plus" class="h-3.5 w-3.5" /></NuxtLink>
          </div>
          <div v-else>
            <div v-for="item in transactions.transactions.value.slice(0, 6)" :key="item.id" class="sb-row">
              <div class="flex min-w-0 items-center gap-3">
                <span class="grid h-9 w-9 shrink-0 place-items-center rounded-xl" :class="getCategoryVisual(item.category?.name, item.type).badgeClass">
                  <UIcon :name="getCategoryVisual(item.category?.name, item.type).icon" class="h-[17px] w-[17px]" />
                </span>
                <div class="min-w-0">
                  <p class="truncate text-sm font-bold">{{ descriptionLabel(item) || t('Сипаттамасыз') }}</p>
                  <p class="sb-muted truncate text-xs">{{ item.merchant || categoryLabel(item.category?.name, 'Санатсыз') }}</p>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-sm font-bold tabular-nums" :class="item.type === 'income' ? 'text-emerald-700 dark:text-emerald-300' : ''">
                  {{ item.type === 'income' ? '+' : item.type === 'expense' ? '−' : '' }}{{ formatCurrency(item.amount) }}
                </p>
                <p class="sb-muted mt-0.5 text-xs">{{ dateLabel(item.transaction_date) }}</p>
              </div>
            </div>
          </div>
        </section>
      </div>

      <div class="grid gap-4">
        <section class="sb-panel" aria-labelledby="distribution-title">
          <div class="sb-panel-head">
            <h2 id="distribution-title" class="sb-section-title">{{ t('Шығыс санаттары') }}</h2>
            <NuxtLink to="/analytics" class="sb-text-link">{{ t('Толығырақ') }} <UIcon name="i-heroicons-arrow-right" class="h-3.5 w-3.5" /></NuxtLink>
          </div>
          <div v-if="!categoryBreakdown.length" class="sb-empty">
            <div class="sb-empty-ring" aria-hidden="true"><UIcon name="i-heroicons-chart-pie" class="relative h-7 w-7 text-violet-500" /></div>
            <p class="text-xs">{{ isLoading ? t('Деректер жүктелуде…') : t('Осы айда шығыс тіркелмеген') }}</p>
          </div>
          <div v-else class="grid gap-4 p-4 sm:grid-cols-[minmax(0,.9fr)_minmax(0,1.1fr)] sm:items-center">
            <ClientOnly><ChartsCategoryDoughnutChart :items="categoryBreakdown" :height="152" /></ClientOnly>
            <div class="space-y-2">
              <div v-for="category in categoryBreakdown.slice(0, 5)" :key="category.category_id || 'none'" class="flex items-center gap-2 text-xs">
                <span class="h-2 w-2 shrink-0 rounded-full" :style="{ backgroundColor: getCategoryVisual(category.category_name, 'expense').hex }" />
                <span class="sb-muted min-w-0 flex-1 truncate">{{ categoryLabel(category.category_name, 'Санатсыз') }}</span>
                <strong class="tabular-nums">{{ category.percentage.toFixed(0) }}%</strong>
              </div>
            </div>
          </div>
        </section>
        <section class="sb-panel" aria-labelledby="budgets-title">
          <div class="sb-panel-head">
            <h2 id="budgets-title" class="sb-section-title">{{ t('Бюджет лимиттері') }}</h2>
            <NuxtLink to="/budgets" class="sb-text-link">{{ t('Басқару') }} <UIcon name="i-heroicons-arrow-right" class="h-3.5 w-3.5" /></NuxtLink>
          </div>
          <div v-if="!budgets.budgets.value.length" class="flex items-center gap-3 p-4">
            <span class="sb-icon-box"><UIcon name="i-heroicons-adjustments-horizontal" class="h-5 w-5" /></span>
            <div><p class="sb-muted text-xs">{{ isLoading ? t('Жүктелуде…') : t('Әзірге бюджет лимиті жоқ') }}</p>
              <NuxtLink v-if="!isLoading" to="/budgets" class="sb-text-link mt-1">{{ t('Лимит қосу') }}</NuxtLink></div>
          </div>
          <div v-else class="space-y-4 p-4">
            <div v-for="budget in budgets.budgets.value.slice(0, 4)" :key="budget.id" class="space-y-2">
              <div class="flex items-center justify-between gap-2 text-xs">
                <span class="truncate font-bold">{{ categoryLabel(budget.category?.name, 'Жалпы бюджет') }}</span>
                <span class="sb-muted shrink-0 tabular-nums">{{ formatCurrency(budget.spent) }} / {{ formatCurrency(budget.limit_amount) }}</span>
              </div>
              <div class="sb-budget-track" role="progressbar" :aria-label="categoryLabel(budget.category?.name, 'Жалпы бюджет')" :aria-valuenow="Math.min(budget.percentage, 100)" aria-valuemin="0" aria-valuemax="100">
                <span :data-over="budget.percentage > 100" :style="{ width: `${Math.min(budget.percentage, 100)}%` }" />
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { CategoryBreakdown, TrendPoint } from '~~/shared/types'

const { t, categoryLabel, dateLabel, monthLabel, descriptionLabel } = useLanguage()
const transactions = useTransactions()
const budgets = useBudgets()
const aiInsights = useAiInsights()
const analytics = useAnalytics()
const { formatCurrency } = useCurrencyFormat()
const summary = ref({ total_income: 0, total_expense: 0, net: 0, transactions_count: 0 })
const categories = ref<CategoryBreakdown[]>([])
const trendRows = ref<TrendPoint[]>([])
const isLoading = ref(true)
const loadError = ref(false)
const categoryBreakdown = computed(() => categories.value.filter(item => Number(item.total) > 0))
const trends = computed(() => {
  const byMonth = new Map(trendRows.value.map(point => [point.month, point]))
  const now = dayjs().startOf('month')
  return Array.from({ length: 6 }, (_, index) => {
    const month = now.subtract(5 - index, 'month').format('YYYY-MM')
    return byMonth.get(month) || { month, income: 0, expense: 0 }
  })
})
const hasMovement = computed(() => trends.value.some(point => Number(point.income) || Number(point.expense)))
const savingsRate = computed(() => Number(summary.value.total_income) > 0 ? Number(summary.value.net) / Number(summary.value.total_income) * 100 : 0)
const currentMonthLabel = computed(() => monthLabel(dayjs().format('YYYY-MM')))
const metrics = computed(() => [
  { label: t('Айлық кіріс'), value: formatCurrency(summary.value.total_income), icon: 'i-heroicons-arrow-down-left', tone: 'mint' },
  { label: t('Айлық шығыс'), value: formatCurrency(summary.value.total_expense), icon: 'i-heroicons-arrow-up-right', tone: 'peach' },
  { label: t('Жинақ нормасы'), value: `${savingsRate.value.toFixed(1)}%`, icon: 'i-heroicons-chart-bar-square', tone: 'blue' },
  { label: t('Операциялар'), value: String(summary.value.transactions_count), icon: 'i-heroicons-rectangle-stack', tone: 'violet' },
])

async function loadDashboard() {
  isLoading.value = true
  loadError.value = false
  const now = dayjs()
  const date_from = now.startOf('month').format('YYYY-MM-DD')
  const date_to = now.endOf('month').format('YYYY-MM-DD')
  const [summaryResult, categoryResult, trendsResult] = await Promise.allSettled([
    analytics.getSummary({ date_from, date_to }),
    analytics.getByCategory({ date_from, date_to }),
    analytics.getTrends({ months: 6 }),
    transactions.fetchTransactions({ per_page: 10 }),
    budgets.fetchBudgets(),
    aiInsights.fetchInsights(),
  ])
  if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value
  else loadError.value = true
  if (categoryResult.status === 'fulfilled') categories.value = categoryResult.value
  if (trendsResult.status === 'fulfilled') trendRows.value = trendsResult.value
  isLoading.value = false
}
onMounted(loadDashboard)
</script>
