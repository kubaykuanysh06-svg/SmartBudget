<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Кірістер мен шығыстар</h2>
        <p class="text-sm text-slate-500">Барлық қаржылық операцияларыңызды сүзгілеп, басқарыңыз</p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        color="emerald"
        size="md"
        label="Операция қосу"
        @click="openModal"
      />
    </div>

    <!-- Filtered Summary Strip -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <div class="rounded-2xl bg-white dark:bg-slate-900/90 ring-1 ring-slate-200/80 dark:ring-slate-800 px-4 py-3 flex items-center justify-between">
        <span class="text-xs font-medium text-slate-500">Табылған жазбалар</span>
        <span class="text-sm font-extrabold tabular-nums text-slate-900 dark:text-white">{{ filteredTransactions.length }}</span>
      </div>
      <div class="rounded-2xl bg-white dark:bg-slate-900/90 ring-1 ring-slate-200/80 dark:ring-slate-800 px-4 py-3 flex items-center justify-between">
        <span class="text-xs font-medium text-slate-500">Кірістер жиыны</span>
        <span class="text-sm font-extrabold tabular-nums text-emerald-600 dark:text-emerald-400">+{{ formatCurrency(filteredIncome) }}</span>
      </div>
      <div class="rounded-2xl bg-white dark:bg-slate-900/90 ring-1 ring-slate-200/80 dark:ring-slate-800 px-4 py-3 flex items-center justify-between">
        <span class="text-xs font-medium text-slate-500">Шығыстар жиыны</span>
        <span class="text-sm font-extrabold tabular-nums text-rose-600 dark:text-rose-400">-{{ formatCurrency(filteredExpense) }}</span>
      </div>
    </div>

    <!-- Filters Bar -->
    <UCard :ui="{ body: { padding: 'p-4 sm:p-4' } }">
      <div class="flex flex-col xl:flex-row gap-3 xl:items-center">
        <div class="flex-1 min-w-0">
          <UInput
            v-model="searchQuery"
            icon="i-heroicons-magnifying-glass"
            placeholder="Сипаттама немесе дүкен бойынша іздеу..."
          />
        </div>

        <div class="flex flex-wrap sm:flex-nowrap items-center gap-3">
          <div class="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 shrink-0">
            <button
              v-for="opt in typeFilterOptions"
              :key="opt.value"
              type="button"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all"
              :class="
                selectedType === opt.value
                  ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              "
              @click="selectedType = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>

          <div class="flex items-center gap-2 flex-1 sm:flex-initial">
            <UInput v-model="startDate" type="date" class="w-36 sm:w-40" title="Басталу күні" />
            <UInput v-model="endDate" type="date" class="w-36 sm:w-40" title="Аяқталу күні" />
            <UButton
              v-if="hasActiveFilters"
              color="gray"
              variant="ghost"
              icon="i-heroicons-x-mark"
              size="sm"
              title="Сүзгіні тазалау"
              @click="resetFilters"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Transactions List -->
    <UCard :ui="{ body: { padding: 'p-0 sm:p-0' } }">
      <div v-if="filteredTransactions.length === 0" class="py-16 px-6 text-center">
        <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
          <UIcon name="i-heroicons-inbox" class="w-6 h-6" />
        </div>
        <p class="text-sm font-semibold text-slate-700 dark:text-slate-200">Операциялар табылмады</p>
        <p class="text-xs text-slate-500 mt-1">Жаңа жазба қосыңыз немесе сүзгі шарттарын өзгертіңіз</p>
      </div>

      <div v-else class="divide-y divide-slate-100 dark:divide-slate-800/80">
        <div
          v-for="item in filteredTransactions"
          :key="item.id"
          class="p-4 sm:px-5 flex items-center justify-between gap-4 hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
        >
          <div class="flex items-center gap-3.5 min-w-0">
            <div
              class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
              :class="visualFor(item).badgeClass"
            >
              <UIcon :name="visualFor(item).icon" class="w-5 h-5" />
            </div>
            <div class="min-w-0">
              <p class="font-semibold text-sm text-slate-900 dark:text-white truncate">
                {{ item.description || 'Сипаттамасыз' }}
              </p>
              <div class="flex flex-wrap items-center gap-2 mt-1">
                <span class="text-[11px] font-semibold px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-300">
                  {{ resolvedCategoryLabel(item) }}
                </span>
                <span v-if="item.merchant" class="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {{ item.merchant }}
                </span>
              </div>
            </div>
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <div class="text-right">
              <p
                class="font-bold text-sm sm:text-base tabular-nums"
                :class="item.type === 'income' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'"
              >
                {{ item.type === 'income' ? '+' : '-' }}{{ formatCurrency(item.amount) }}
              </p>
              <p class="text-[11px] text-slate-400 tabular-nums">{{ item.transaction_date }}</p>
            </div>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-trash"
              size="xs"
              title="Операцияны өшіру"
              @click="handleDelete(item.id)"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Create Operation Modal -->
    <UModal v-model="isModalOpen">
      <div class="p-6 space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-extrabold text-slate-900 dark:text-white">Жаңа операция</h3>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" size="xs" @click="isModalOpen = false" />
        </div>

        <!-- Segmented Expense / Income Toggle -->
        <div class="grid grid-cols-2 gap-2 p-1 rounded-xl bg-slate-100 dark:bg-slate-800">
          <button
            type="button"
            class="py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            :class="
              newForm.type === 'expense'
                ? 'bg-white dark:bg-slate-900 text-rose-600 dark:text-rose-400 shadow-xs'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            "
            @click="newForm.type = 'expense'"
          >
            <UIcon name="i-heroicons-arrow-up-right" class="w-4 h-4" />
            <span>Шығыс</span>
          </button>
          <button
            type="button"
            class="py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5"
            :class="
              newForm.type === 'income'
                ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            "
            @click="newForm.type = 'income'"
          >
            <UIcon name="i-heroicons-arrow-down-left" class="w-4 h-4" />
            <span>Кіріс</span>
          </button>
        </div>

        <div class="space-y-3.5">
          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
              Сома ({{ currency }})
            </label>
            <UInput
              v-model="newForm.amount"
              type="number"
              size="lg"
              step="0.01"
              min="0.01"
              placeholder="Мысалы: 8000"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1" for="transaction-category">
              Санат
            </label>
            <USelect id="transaction-category" v-model="newForm.category_id" :options="categoryOptions" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
              Сипаттама / Тауар атауы
            </label>
            <UInput v-model="newForm.description" placeholder="Мысалы: Апталық азық-түлік" />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
                Дүкен / Орын
              </label>
              <UInput v-model="newForm.merchant" placeholder="Magnum, Kaspi, Small" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">
                Күні
              </label>
              <UInput v-model="newForm.transaction_date" type="date" />
            </div>
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
          <UButton color="emerald" label="Сақтау" :loading="isSubmitting" @click="handleSubmit" />
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { CategoryTree, Transaction, TransactionType } from '~~/shared/types'

const route = useRoute()
const router = useRouter()
const transactions = useTransactions()
const api = useApi()
const categoryTree = ref<CategoryTree[]>([])
const isModalOpen = ref(false)
const isSubmitting = ref(false)
const formError = ref('')

const searchQuery = ref('')
const selectedType = ref<'all' | 'expense' | 'income'>('all')
const startDate = ref('')
const endDate = ref('')

const typeFilterOptions: { label: string; value: 'all' | 'expense' | 'income' }[] = [
  { label: 'Барлығы', value: 'all' },
  { label: 'Шығыстар', value: 'expense' },
  { label: 'Кірістер', value: 'income' },
]

const newForm = ref({
  type: 'expense' as TransactionType,
  amount: '' as string | number,
  description: '',
  merchant: '',
  category_id: '',
  transaction_date: dayjs().format('YYYY-MM-DD'),
})

const hasActiveFilters = computed(
  () => Boolean(searchQuery.value || selectedType.value !== 'all' || startDate.value || endDate.value),
)

const resetFilters = () => {
  searchQuery.value = ''
  selectedType.value = 'all'
  startDate.value = ''
  endDate.value = ''
}

const openModal = () => {
  formError.value = ''
  isModalOpen.value = true
}

function flattenCategories(tree: CategoryTree[]): CategoryTree[] {
  return tree.flatMap(category => [category, ...flattenCategories(category.children)])
}

const categories = computed(() => flattenCategories(categoryTree.value))
const categoryOptions = computed(() => [
  { label: 'Санатсыз', value: '' },
  ...categories.value
    .filter(category => category.type === newForm.value.type)
    .map(category => ({
      label: translateCategoryName(category.name),
      value: category.id,
    })),
])

watch(() => newForm.value.type, () => { newForm.value.category_id = '' })
watch(() => route.query.action, (action) => {
  if (action === 'new') {
    openModal()
    router.replace({ query: { ...route.query, action: undefined } })
  }
}, { immediate: true })

const categoryFor = (id: string | null) => categories.value.find(category => category.id === id)

const resolvedCategoryName = (item: Transaction) =>
  item.category?.name || categoryFor(item.category_id)?.name || null

const resolvedCategoryLabel = (item: Transaction) =>
  translateCategoryName(resolvedCategoryName(item), item.type === 'income' ? 'Кіріс' : 'Жалпы')

const visualFor = (item: Transaction) =>
  getCategoryVisual(resolvedCategoryName(item), item.type)

const filteredTransactions = computed(() => {
  return transactions.transactions.value.filter((t) => {
    if (selectedType.value !== 'all' && t.type !== selectedType.value) return false
    if (startDate.value && t.transaction_date < startDate.value) return false
    if (endDate.value && t.transaction_date > endDate.value) return false
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const desc = (t.description || '').toLowerCase()
      const merch = (t.merchant || '').toLowerCase()
      if (!desc.includes(q) && !merch.includes(q)) return false
    }
    return true
  })
})

const filteredIncome = computed(() =>
  filteredTransactions.value
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + Number(t.amount || 0), 0),
)

const filteredExpense = computed(() =>
  filteredTransactions.value
    .filter(t => t.type === 'expense')
    .reduce((sum, t) => sum + Number(t.amount || 0), 0),
)

const { currency, formatCurrency } = useCurrencyFormat()

const handleDelete = async (id: string) => {
  if (confirm('Бұл операцияны өшіруді растайсыз ба?')) {
    await transactions.deleteTransaction(id)
  }
}

const handleSubmit = async () => {
  formError.value = ''
  const moneyErr = validateMoneyInput(newForm.value.amount)
  if (moneyErr) {
    formError.value = moneyErr
    return
  }
  if (!newForm.value.description.trim()) {
    formError.value = 'Операция сипаттамасын енгізіңіз'
    return
  }
  if (!newForm.value.transaction_date) {
    formError.value = 'Операция күнін көрсетіңіз'
    return
  }

  isSubmitting.value = true
  try {
    await transactions.createTransaction({
      type: newForm.value.type,
      amount: Number(String(newForm.value.amount).replace(',', '.')),
      description: newForm.value.description.trim(),
      merchant: newForm.value.merchant.trim() || null,
      category_id: newForm.value.category_id || null,
      transaction_date: newForm.value.transaction_date,
    })
    isModalOpen.value = false
    newForm.value.amount = ''
    newForm.value.description = ''
    newForm.value.merchant = ''
  } catch (err: any) {
    formError.value = formatApiError(err, 'Операцияны сақтау мүмкін болмады')
  } finally {
    isSubmitting.value = false
  }
}

watch([startDate, endDate], () => {
  const params: Record<string, any> = { per_page: 100 }
  if (startDate.value) params.date_from = startDate.value
  if (endDate.value) params.date_to = endDate.value
  transactions.fetchTransactions(params)
})

onMounted(async () => {
  const [, categoryResult] = await Promise.allSettled([
    transactions.fetchTransactions({ per_page: 100 }),
    api.fetch<CategoryTree[]>('/categories/tree'),
  ])
  if (categoryResult.status === 'fulfilled') categoryTree.value = categoryResult.value
})
</script>
