<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Лимиттер мен Бюджеттер</h2>
        <p class="text-sm text-slate-500">Айлық, апталық немесе жылдық шығыс шегін белгілеп, артық шығынның алдын алыңыз</p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        color="emerald"
        size="md"
        label="Бюджет қосу"
        @click="openModal"
      />
    </div>

    <!-- Summary Strip when budgets exist -->
    <div v-if="budgets.budgets.value.length > 0" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Белсенді лимиттер</p>
        <p class="text-xl font-extrabold text-slate-900 dark:text-white mt-1 tabular-nums">
          {{ budgets.budgets.value.length }}
        </p>
      </UCard>
      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Осы айдағы жалпы шығыс</p>
        <p class="text-xl font-extrabold text-rose-600 dark:text-rose-400 mt-1 tabular-nums">
          {{ formatCurrency(monthlyExpense) }}
        </p>
      </UCard>
      <UCard>
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Ең жоғары игерілуі</p>
        <p
          class="text-xl font-extrabold mt-1 tabular-nums"
          :class="maxPercentage > 100 ? 'text-rose-600 dark:text-rose-400' : maxPercentage > 80 ? 'text-amber-500' : 'text-emerald-600 dark:text-emerald-400'"
        >
          {{ maxPercentage.toFixed(0) }}%
        </p>
      </UCard>
    </div>

    <!-- Empty State -->
    <div
      v-if="budgets.budgets.value.length === 0"
      class="p-12 sm:p-16 text-center rounded-3xl bg-white dark:bg-slate-900/80 ring-1 ring-slate-200/80 dark:ring-slate-800"
    >
      <div class="w-14 h-14 rounded-2xl bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mx-auto mb-4">
        <UIcon name="i-heroicons-chart-pie" class="w-7 h-7" />
      </div>
      <h3 class="font-bold text-base text-slate-900 dark:text-white">Бюджет лимиттері әлі орнатылмаған</h3>
      <p class="text-sm text-slate-500 mt-1 max-w-md mx-auto">
        Жалпы айлық шығысқа немесе жеке санаттарға лимит қойып, қаржылық тәртіпті сақтаңыз
      </p>
      <UButton class="mt-5" color="emerald" icon="i-heroicons-plus" label="Алғашқы лимитті орнату" @click="openModal" />
    </div>

    <!-- Budget Cards Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <UCard
        v-for="b in budgets.budgets.value"
        :key="b.id"
        class="relative overflow-hidden"
      >
        <div class="space-y-4">
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3 min-w-0">
              <div
                class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0"
                :class="visualFor(b).badgeClass"
              >
                <UIcon :name="visualFor(b).icon" class="w-5 h-5" />
              </div>
              <div class="min-w-0">
                <h3 class="font-bold text-sm text-slate-900 dark:text-white truncate">
                  {{ budgetTitle(b) }}
                </h3>
                <p class="text-xs text-slate-400">{{ periodLabel(b.period) }}</p>
              </div>
            </div>

            <div class="flex items-center gap-1.5 shrink-0">
              <UBadge
                :color="b.percentage > 100 ? 'rose' : b.percentage > 80 ? 'amber' : 'emerald'"
                variant="subtle"
              >
                {{ b.percentage.toFixed(0) }}%
              </UBadge>
              <UButton
                color="gray"
                variant="ghost"
                icon="i-heroicons-trash"
                size="2xs"
                title="Лимитті өшіру"
                @click="budgets.deleteBudget(b.id)"
              />
            </div>
          </div>

          <div class="space-y-2">
            <div class="flex justify-between text-xs text-slate-500 tabular-nums">
              <span>Жұмсалды: <strong class="text-slate-800 dark:text-slate-200">{{ formatCurrency(b.spent) }}</strong></span>
              <span>Лимит: <strong class="text-slate-800 dark:text-slate-200">{{ formatCurrency(b.limit_amount) }}</strong></span>
            </div>
            <UProgress
              :value="Math.min(b.percentage, 100)"
              :color="b.percentage > 100 ? 'rose' : b.percentage > 80 ? 'amber' : 'emerald'"
              size="md"
            />
          </div>

          <div class="text-xs flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
            <span class="text-slate-500">{{ b.remaining < 0 ? 'Асып кеткені:' : 'Қалдық:' }}</span>
            <span
              class="font-extrabold text-sm tabular-nums"
              :class="b.remaining < 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'"
            >
              {{ formatCurrency(b.remaining) }}
            </span>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Create Budget Modal -->
    <UModal v-model="isModalOpen">
      <div class="p-6 space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-extrabold text-slate-900 dark:text-white">Бюджет лимитін орнату</h3>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" size="xs" @click="isModalOpen = false" />
        </div>

        <div class="space-y-3.5">
          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Санат</label>
            <USelect v-model="newCategoryId" :options="categoryOptions" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
              Лимит сомасы ({{ currency }})
            </label>
            <UInput v-model="newLimit" type="number" size="lg" step="0.01" min="0.01" placeholder="20000" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Кезең</label>
            <USelect
              v-model="newPeriod"
              :options="[
                { label: 'Айлық', value: 'monthly' },
                { label: 'Апталық', value: 'weekly' },
                { label: 'Жылдық', value: 'yearly' },
              ]"
            />
          </div>
        </div>

        <div
          v-if="formError"
          role="alert"
          class="flex items-center gap-2 text-xs font-medium text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 ring-1 ring-rose-200 dark:ring-rose-900/70 rounded-xl px-3.5 py-2.5"
        >
          <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 shrink-0" />
          <span>{{ formError }}</span>
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <UButton color="gray" variant="ghost" label="Бас тарту" @click="isModalOpen = false" />
          <UButton color="emerald" label="Құру" :loading="isSubmitting" @click="handleCreate" />
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { BudgetStatus, CategoryTree } from '~~/shared/types'

const budgets = useBudgets()
const analytics = useAnalytics()
const api = useApi()
const categoryTree = ref<CategoryTree[]>([])
const monthlyExpense = ref(0)
const isModalOpen = ref(false)
const isSubmitting = ref(false)
const formError = ref('')
const newCategoryId = ref('')
const newLimit = ref<string | number>(20000)
const newPeriod = ref('monthly')

const { currency, formatCurrency } = useCurrencyFormat()

function flattenCategories(tree: CategoryTree[]): CategoryTree[] {
  return tree.flatMap(category => [category, ...flattenCategories(category.children)])
}

const categories = computed(() => flattenCategories(categoryTree.value))
const categoryOptions = computed(() => [
  { label: 'Жалпы бюджет (барлық шығыстар)', value: '' },
  ...categories.value
    .filter(c => c.type === 'expense')
    .map(c => ({ label: translateCategoryName(c.name), value: c.id })),
])

const categoryFor = (id?: string | null) => categories.value.find(c => c.id === id)

const resolvedName = (b: BudgetStatus) => b.category?.name || categoryFor(b.category_id)?.name || null

const budgetTitle = (b: BudgetStatus) => {
  const n = resolvedName(b)
  return n ? translateCategoryName(n) : 'Жалпы бюджет'
}

const visualFor = (b: BudgetStatus) => {
  const n = resolvedName(b)
  if (!n) {
    return {
      label: 'Жалпы бюджет',
      icon: 'i-heroicons-chart-pie',
      badgeClass: 'bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20',
      hex: '#10b981',
    }
  }
  return getCategoryVisual(n, 'expense')
}

const maxPercentage = computed(() =>
  budgets.budgets.value.reduce((m, b) => Math.max(m, Number(b.percentage || 0)), 0),
)

const periodLabel = (period: string) => {
  if (period === 'weekly') return 'Апталық лимит'
  if (period === 'yearly') return 'Жылдық лимит'
  return 'Айлық лимит'
}

const openModal = () => {
  formError.value = ''
  isModalOpen.value = true
}

const handleCreate = async () => {
  formError.value = ''
  const errMsg = validateMoneyInput(newLimit.value)
  if (errMsg) {
    formError.value = errMsg
    return
  }

  isSubmitting.value = true
  try {
    await budgets.createBudget({
      category_id: newCategoryId.value || null,
      limit_amount: Number(String(newLimit.value).replace(',', '.')),
      period: newPeriod.value,
      start_date: dayjs().format('YYYY-MM-DD'),
    })
    isModalOpen.value = false
  } catch (err: any) {
    formError.value = formatApiError(err, 'Бюджетті құру мүмкін болмады')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  const date_from = dayjs().startOf('month').format('YYYY-MM-DD')
  const date_to = dayjs().endOf('month').format('YYYY-MM-DD')
  const [, catRes, sumRes] = await Promise.allSettled([
    budgets.fetchBudgets(),
    api.fetch<CategoryTree[]>('/categories/tree'),
    analytics.getSummary({ date_from, date_to }),
  ])
  if (catRes.status === 'fulfilled') categoryTree.value = catRes.value
  if (sumRes.status === 'fulfilled') monthlyExpense.value = Number(sumRes.value.total_expense || 0)
})
</script>
