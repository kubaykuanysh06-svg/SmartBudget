<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Лимиты и Бюджеты</h2>
        <p class="text-sm text-gray-500">Контролируйте свои траты по категориям</p>
      </div>
      <UButton
        icon="i-heroicons-plus"
        color="emerald"
        label="Создать бюджет"
        @click="openModal"
      />
    </div>

    <div v-if="budgets.budgets.value.length === 0" class="p-12 text-center border border-dashed rounded-2xl dark:border-gray-800">
      <UIcon name="i-heroicons-chart-pie" class="w-12 h-12 mx-auto mb-2 text-gray-400" />
      <h3 class="font-medium text-base">Бюджеты ещё не настроены</h3>
      <p class="text-sm text-gray-500 mt-1">Установите лимиты на месяц, чтобы избежать перерасхода</p>
      <UButton class="mt-4" color="emerald" label="Установить первый лимит" @click="openModal" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <UCard
        v-for="b in budgets.budgets.value"
        :key="b.id"
        class="relative overflow-hidden"
      >
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ b.category?.icon || categoryFor(b.category_id)?.icon || '📦' }}</span>
              <div>
                <h3 class="font-semibold">{{ b.category?.name || categoryFor(b.category_id)?.name || 'Общий бюджет' }}</h3>
                <p class="text-[11px] text-gray-400">{{ periodLabel(b.period) }}</p>
              </div>
            </div>
            <div class="flex items-center gap-1.5">
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
                title="Удалить бюджет"
                @click="budgets.deleteBudget(b.id)"
              />
            </div>
          </div>

          <div class="space-y-1">
            <div class="flex justify-between text-xs text-gray-500">
              <span>Потрачено: {{ formatCurrency(b.spent) }}</span>
              <span>Лимит: {{ formatCurrency(b.limit_amount) }}</span>
            </div>
            <UProgress
              :value="Math.min(b.percentage, 100)"
              :color="b.percentage > 100 ? 'rose' : b.percentage > 80 ? 'amber' : 'emerald'"
              size="md"
            />
          </div>

          <div class="text-xs text-gray-500 flex justify-between pt-2 border-t border-gray-100 dark:border-gray-800">
            <span>Остаток:</span>
            <span
              class="font-semibold"
              :class="b.remaining < 0 ? 'text-rose-600' : 'text-emerald-600'"
            >
              {{ formatCurrency(b.remaining) }}
            </span>
          </div>
        </div>
      </UCard>
    </div>

    <!-- Create Modal -->
    <UModal v-model="isModalOpen">
      <div class="p-6 space-y-4">
        <h3 class="text-lg font-bold">Установить лимит бюджета</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium mb-1">Категория</label>
            <USelect v-model="newCategoryId" :options="categoryOptions" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Сумма лимита ({{ currency }})</label>
            <UInput v-model="newLimit" type="number" step="0.01" min="0.01" placeholder="20000" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Период</label>
            <USelect
              v-model="newPeriod"
              :options="[
                { label: 'Месячный', value: 'monthly' },
                { label: 'Недельный', value: 'weekly' },
                { label: 'Годовой', value: 'yearly' },
              ]"
            />
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
          <UButton color="emerald" label="Создать" :loading="isSubmitting" @click="handleCreate" />
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { CategoryTree } from '~~/shared/types'

const budgets = useBudgets()
const api = useApi()
const categoryTree = ref<CategoryTree[]>([])
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
  { label: 'Общий бюджет (все расходы)', value: '' },
  ...categories.value
    .filter(c => c.type === 'expense')
    .map(c => ({ label: `${c.icon || '📦'} ${c.name}`, value: c.id })),
])

const categoryFor = (id?: string | null) => categories.value.find(c => c.id === id)

const periodLabel = (period: string) => {
  if (period === 'weekly') return 'Недельный лимит'
  if (period === 'yearly') return 'Годовой лимит'
  return 'Месячный лимит'
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
    formError.value = formatApiError(err, 'Не удалось создать бюджет')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  const [, catRes] = await Promise.allSettled([
    budgets.fetchBudgets(),
    api.fetch<CategoryTree[]>('/categories/tree'),
  ])
  if (catRes.status === 'fulfilled') categoryTree.value = catRes.value
})
</script>
