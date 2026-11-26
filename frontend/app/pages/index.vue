<template>
  <div class="space-y-6">
    <!-- Hero Financial Banner -->
    <div class="relative overflow-hidden rounded-3xl bg-slate-900 dark:bg-slate-900 text-white p-6 sm:p-8 ring-1 ring-slate-800 shadow-xl fintech-hero-mesh">
      <div class="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 ring-1 ring-white/15 text-xs font-medium text-emerald-300">
            <UIcon name="i-heroicons-calendar-days" class="w-4 h-4" />
            <span>{{ currentMonthLabel }} шолуы</span>
          </div>
          <p class="text-sm text-slate-300 font-medium">Ағымдағы айдағы таза қалдық</p>
          <p
            class="text-3xl sm:text-4xl font-extrabold tracking-tight tabular-nums"
            :class="Number(summary.net) < 0 ? 'text-rose-300' : 'text-white'"
          >
            {{ formatCurrency(summary.net) }}
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <UButton
            color="emerald"
            size="md"
            icon="i-heroicons-plus"
            label="Операция қосу"
            @click="navigateTo('/transactions?action=new')"
          />
          <UButton
            color="white"
            variant="solid"
            size="md"
            icon="i-heroicons-chart-pie"
            label="Бюджет орнату"
            class="!bg-white/10 !text-white hover:!bg-white/20 !ring-white/20"
            @click="navigateTo('/budgets')"
          />
        </div>
      </div>
    </div>

    <!-- KPI Stat Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Айлық кіріс</p>
            <p class="text-xl xl:text-2xl font-extrabold mt-1.5 text-emerald-600 dark:text-emerald-400 tabular-nums truncate">
              +{{ formatCurrency(summary.total_income) }}
            </p>
          </div>
          <div class="w-11 h-11 shrink-0 rounded-2xl bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-down-left" class="w-5 h-5" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Айлық шығыс</p>
            <p class="text-xl xl:text-2xl font-extrabold mt-1.5 text-rose-600 dark:text-rose-400 tabular-nums truncate">
              -{{ formatCurrency(summary.total_expense) }}
            </p>
          </div>
          <div class="w-11 h-11 shrink-0 rounded-2xl bg-rose-500/12 text-rose-600 dark:text-rose-400 ring-1 ring-rose-500/20 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-up-right" class="w-5 h-5" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Жинақ нормасы</p>
            <p class="text-xl xl:text-2xl font-extrabold mt-1.5 text-teal-600 dark:text-teal-400 tabular-nums truncate">
              {{ savingsRate.toFixed(1) }}%
            </p>
          </div>
          <div class="w-11 h-11 shrink-0 rounded-2xl bg-teal-500/12 text-teal-600 dark:text-teal-400 ring-1 ring-teal-500/20 flex items-center justify-center">
            <UIcon name="i-heroicons-shield-check" class="w-5 h-5" />
          </div>
        </div>
      </UCard>

      <UCard>
        <div class="flex items-center justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Операция саны</p>
            <p class="text-xl xl:text-2xl font-extrabold mt-1.5 text-slate-900 dark:text-white tabular-nums truncate">
              {{ summary.transactions_count }}
            </p>
          </div>
          <div class="w-11 h-11 shrink-0 rounded-2xl bg-sky-500/12 text-sky-600 dark:text-sky-400 ring-1 ring-sky-500/20 flex items-center justify-center">
            <UIcon name="i-heroicons-receipt-percent" class="w-5 h-5" />
          </div>
        </div>
      </UCard>
    </div>

    <!-- AI Insights Callout -->
    <div
      v-if="aiInsights.insights.value.length > 0"
      class="p-4 sm:p-5 rounded-2xl ring-1 ring-teal-500/25 bg-gradient-to-r from-teal-500/10 via-emerald-500/5 to-transparent flex flex-col sm:flex-row sm:items-center gap-4"
    >
      <div class="w-10 h-10 rounded-xl bg-teal-500 text-white flex items-center justify-center shrink-0 shadow-sm">
        <UIcon name="i-heroicons-sparkles" class="w-5 h-5" />
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-sm text-slate-900 dark:text-white">
          {{ aiInsights.insights.value[0]?.title }}
        </h3>
        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 mt-0.5">
          {{ aiInsights.insights.value[0]?.content }}
        </p>
      </div>
      <UButton
        size="xs"
        color="teal"
        variant="soft"
        label="Барлық кеңестер"
        trailing-icon="i-heroicons-arrow-right"
        @click="navigateTo('/ai')"
      />
    </div>

    <!-- Main Dashboard Grid -->
    <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
      <!-- Left: Recent Operations -->
      <div class="xl:col-span-7 space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-base font-bold text-slate-900 dark:text-white">Соңғы операциялар</h2>
            <p class="text-xs text-slate-500">Жақында енгізілген кірістер мен шығыстар</p>
          </div>
          <NuxtLink to="/transactions" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline flex items-center gap-1">
            <span>Барлығын көру</span>
            <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
          </NuxtLink>
        </div>

        <UCard :ui="{ body: { padding: 'p-0 sm:p-0' } }">
          <div v-if="transactions.transactions.value.length === 0" class="py-14 px-6 text-center">
            <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
              <UIcon name="i-heroicons-arrows-right-left" class="w-6 h-6" />
            </div>
            <p class="text-sm font-semibold text-slate-700 dark:text-slate-200">Әзірге операциялар жоқ</p>
            <p class="text-xs text-slate-500 mt-1">Алғашқы кіріс немесе шығыс жазбасын қосып бастаңыз</p>
            <UButton
              class="mt-4"
              size="sm"
              color="emerald"
              icon="i-heroicons-plus"
              label="Алғашқы операцияны қосу"
              @click="navigateTo('/transactions?action=new')"
            />
          </div>

          <div v-else class="divide-y divide-slate-100 dark:divide-slate-800/80">
            <div
              v-for="item in transactions.transactions.value.slice(0, 6)"
              :key="item.id"
              class="p-4 flex items-center justify-between gap-4 hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
            >
              <div class="flex items-center gap-3.5 min-w-0">
                <div
                  class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  :class="getCategoryVisual(item.category?.name, item.type).badgeClass"
                >
                  <UIcon :name="getCategoryVisual(item.category?.name, item.type).icon" class="w-5 h-5" />
                </div>
                <div class="min-w-0">
                  <p class="font-semibold text-sm text-slate-900 dark:text-white truncate">
                    {{ item.description || 'Сипаттамасыз' }}
                  </p>
                  <div class="flex items-center gap-2 mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                    <span class="truncate">{{ translateCategoryName(item.category?.name, item.type === 'income' ? 'Кіріс' : 'Санатсыз') }}</span>
                    <template v-if="item.merchant">
                      <span class="text-slate-300 dark:text-slate-600">•</span>
                      <span class="truncate">{{ item.merchant }}</span>
                    </template>
                  </div>
                </div>
              </div>

              <div class="text-right shrink-0">
                <p
                  class="font-bold text-sm tabular-nums"
                  :class="item.type === 'income' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'"
                >
                  {{ item.type === 'income' ? '+' : '-' }}{{ formatCurrency(item.amount) }}
                </p>
                <p class="text-[11px] text-slate-400 mt-0.5">{{ formatKzDate(item.transaction_date) }}</p>
              </div>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Right: Expense Doughnut + Budgets -->
      <div class="xl:col-span-5 space-y-6">
        <!-- Doughnut Breakdown Card -->
        <UCard>
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-white">Шығыстар құрылымы</h2>
              <p class="text-xs text-slate-500">Осы айдағы санаттар үлесі</p>
            </div>
            <NuxtLink to="/analytics" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              Толығырақ
            </NuxtLink>
          </div>

          <div v-if="categoryBreakdown.length === 0" class="py-8 text-center text-xs text-slate-400">
            Диаграмманы көру үшін кемінде бір шығыс енгізіңіз
          </div>
          <div v-else class="space-y-4">
            <ClientOnly>
              <ChartsCategoryDoughnutChart :items="categoryBreakdown" :height="195" />
            </ClientOnly>
            <div class="grid grid-cols-2 gap-2 pt-1">
              <div
                v-for="cat in categoryBreakdown.slice(0, 4)"
                :key="cat.category_id || 'none'"
                class="flex items-center justify-between gap-2 px-2.5 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-xs"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <span
                    class="w-2.5 h-2.5 rounded-full shrink-0"
                    :style="{ backgroundColor: getCategoryVisual(cat.category_name, 'expense').hex }"
                  />
                  <span class="truncate text-slate-600 dark:text-slate-300">
                    {{ translateCategoryName(cat.category_name, 'Санатсыз') }}
                  </span>
                </div>
                <span class="font-bold tabular-nums text-slate-900 dark:text-white shrink-0">
                  {{ cat.percentage.toFixed(0) }}%
                </span>
              </div>
            </div>
          </div>
        </UCard>

        <!-- Budgets Quick View -->
        <UCard>
          <div class="flex items-center justify-between mb-4">
            <div>
              <h2 class="text-base font-bold text-slate-900 dark:text-white">Бюджет лимиттері</h2>
              <p class="text-xs text-slate-500">Лимиттердің орындалу барысы</p>
            </div>
            <NuxtLink to="/budgets" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
              Басқару
            </NuxtLink>
          </div>

          <div v-if="budgets.budgets.value.length === 0" class="py-6 text-center">
            <p class="text-xs text-slate-500">Бюджет лимиттері әлі орнатылмаған</p>
            <UButton
              class="mt-3"
              size="xs"
              color="emerald"
              variant="soft"
              icon="i-heroicons-plus"
              label="Лимит қосу"
              @click="navigateTo('/budgets')"
            />
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="b in budgets.budgets.value.slice(0, 4)"
              :key="b.id"
              class="space-y-2"
            >
              <div class="flex items-center justify-between text-xs gap-2">
                <span class="font-semibold text-slate-800 dark:text-slate-200 truncate">
                  {{ b.category?.name ? translateCategoryName(b.category.name) : 'Жалпы бюджет' }}
                </span>
                <span class="tabular-nums text-slate-500 shrink-0">
                  {{ formatCurrency(b.spent) }} / {{ formatCurrency(b.limit_amount) }}
                  <strong class="ml-1 text-slate-800 dark:text-slate-200">({{ b.percentage.toFixed(0) }}%)</strong>
                </span>
              </div>
              <UProgress
                :value="Math.min(b.percentage, 100)"
                :color="b.percentage > 100 ? 'rose' : b.percentage > 80 ? 'amber' : 'emerald'"
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
import type { CategoryBreakdown } from '~~/shared/types'

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
const categoryBreakdown = ref<CategoryBreakdown[]>([])

const savingsRate = computed(() => {
  const income = Number(summary.value.total_income)
  return income > 0 ? (Number(summary.value.net) / income) * 100 : 0
})

const currentMonthLabel = computed(() => formatKzMonth(dayjs().format('YYYY-MM')))

const { formatCurrency } = useCurrencyFormat()

onMounted(async () => {
  const date_from = dayjs().startOf('month').format('YYYY-MM-DD')
  const date_to = dayjs().endOf('month').format('YYYY-MM-DD')

  const [summaryResult, catResult] = await Promise.allSettled([
    analytics.getSummary({ date_from, date_to }),
    analytics.getByCategory({ date_from, date_to }),
    transactions.fetchTransactions({ per_page: 10 }),
    budgets.fetchBudgets(),
    aiInsights.fetchInsights(),
  ])
  if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value
  if (catResult.status === 'fulfilled') categoryBreakdown.value = catResult.value
})
</script>
