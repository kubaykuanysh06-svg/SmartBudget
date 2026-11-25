<template>
  <div class="space-y-6">
    <!-- Header with Add Button -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Список покупок и доходов</h2>
        <p class="text-sm text-gray-500">Управляйте своими расходами и доходами</p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        color="emerald"
        label="Добавить операцию"
        @click="openModal"
      />
    </div>

    <!-- Filters Bar -->
    <UCard :ui="{ body: { padding: 'p-3 sm:p-4' } }">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <UInput
          v-model="searchQuery"
          icon="i-heroicons-magnifying-glass"
          placeholder="Поиск по описанию или магазину..."
        />
        <USelect
          v-model="selectedType"
          :options="[
            { label: 'Все типы', value: 'all' },
            { label: 'Расходы', value: 'expense' },
            { label: 'Доходы', value: 'income' },
          ]"
        />
        <UInput v-model="startDate" type="date" placeholder="С даты" />
        <UInput v-model="endDate" type="date" placeholder="По дату" />
      </div>
    </UCard>

    <!-- Transactions Table -->
    <UCard :ui="{ body: { padding: 'p-0 sm:p-0' } }">
      <div v-if="filteredTransactions.length === 0" class="py-16 text-center text-gray-400">
        <UIcon name="i-heroicons-inbox" class="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>Операций не найдено</p>
      </div>
      <div v-else class="divide-y divide-gray-100 dark:divide-gray-800">
        <div
          v-for="item in filteredTransactions"
          :key="item.id"
          class="p-4 flex items-center justify-between hover:bg-gray-50/50 dark:hover:bg-gray-800/40 transition-colors"
        >
          <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xl">
              {{ item.category?.icon || categoryFor(item.category_id)?.icon || (item.type === 'income' ? '💰' : '💳') }}
            </div>
            <div>
              <p class="font-medium text-sm">{{ item.description || 'Без описания' }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-xs text-gray-400">{{ item.merchant || 'Без магазина' }}</span>
                <span class="text-xs text-gray-300 dark:text-gray-600">•</span>
                <span class="text-xs text-emerald-600 font-medium">
                  {{ item.category?.name || categoryFor(item.category_id)?.name || 'Общая' }}
                </span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="text-right">
              <p
                class="font-semibold text-sm"
                :class="item.type === 'income' ? 'text-green-600' : 'text-rose-600'"
              >
                {{ item.type === 'income' ? '+' : '-' }}{{ formatCurrency(item.amount) }}
              </p>
              <p class="text-xs text-gray-400">{{ item.transaction_date }}</p>
            </div>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-heroicons-trash"
              size="xs"
              @click="handleDelete(item.id)"
            />
          </div>
        </div>
      </div>
    </UCard>

    <!-- Create Modal -->
    <UModal v-model="isModalOpen">
      <div class="p-6 space-y-4">
        <h3 class="text-lg font-bold">Новая операция</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium mb-1">Тип</label>
            <USelect
              v-model="newForm.type"
              :options="[
                { label: 'Расход', value: 'expense' },
                { label: 'Доход', value: 'income' },
              ]"
            />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" for="transaction-category">Категория</label>
            <USelect id="transaction-category" v-model="newForm.category_id" :options="categoryOptions" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Сумма ({{ currency }})</label>
            <UInput v-model="newForm.amount" type="number" step="0.01" min="0.01" placeholder="1000" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Описание / Товар</label>
            <UInput v-model="newForm.description" placeholder="Продукты в супермаркете" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Магазин / Место</label>
            <UInput v-model="newForm.merchant" placeholder="Magnum, Kaspi, Small" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Дата</label>
            <UInput v-model="newForm.transaction_date" type="date" />
          </div>
        </div>

        <div
          v-if="formError"
          role="alert"
          class="text-xs text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 rounded-lg px-3 py-2"
        >
          {{ formError }}
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <UButton color="gray" variant="ghost" label="Отмена" @click="isModalOpen = false" />
          <UButton color="emerald" label="Сохранить" :loading="isSubmitting" @click="handleSubmit" />
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { CategoryTree, TransactionType } from '~~/shared/types'

const route = useRoute()
const router = useRouter()
const transactions = useTransactions()
const api = useApi()
const categoryTree = ref<CategoryTree[]>([])
const isModalOpen = ref(false)
const isSubmitting = ref(false)
const formError = ref('')

const searchQuery = ref('')
const selectedType = ref('all')
const startDate = ref('')
const endDate = ref('')

const newForm = ref({
  type: 'expense' as TransactionType,
  amount: '' as string | number,
  description: '',
  merchant: '',
  category_id: '',
  transaction_date: dayjs().format('YYYY-MM-DD'),
})

const openModal = () => {
  formError.value = ''
  isModalOpen.value = true
}

function flattenCategories(tree: CategoryTree[]): CategoryTree[] {
  return tree.flatMap(category => [category, ...flattenCategories(category.children)])
}

const categories = computed(() => flattenCategories(categoryTree.value))
const categoryOptions = computed(() => [
  { label: 'Без категории', value: '' },
  ...categories.value.filter(category => category.type === newForm.value.type)
    .map(category => ({ label: category.name, value: category.id })),
])

watch(() => newForm.value.type, () => { newForm.value.category_id = '' })
watch(() => route.query.action, (action) => {
  if (action === 'new') {
    openModal()
    router.replace({ query: { ...route.query, action: undefined } })
  }
}, { immediate: true })

const categoryFor = (id: string | null) => categories.value.find(category => category.id === id)

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

const { currency, formatCurrency } = useCurrencyFormat()

const handleDelete = async (id: string) => {
  if (confirm('Удалить эту операцию?')) {
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
    formError.value = 'Введите описание операции'
    return
  }
  if (!newForm.value.transaction_date) {
    formError.value = 'Укажите дату операции'
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
    formError.value = formatApiError(err, 'Не удалось сохранить операцию')
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
