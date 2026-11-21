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
        @click="isModalOpen = true"
      />
    </div>

    <div v-if="budgets.budgets.value.length === 0" class="p-12 text-center border border-dashed rounded-2xl dark:border-gray-800">
      <UIcon name="i-heroicons-chart-pie" class="w-12 h-12 mx-auto mb-2 text-gray-400" />
      <h3 class="font-medium text-base">Бюджеты ещё не настроены</h3>
      <p class="text-sm text-gray-500 mt-1">Установите лимиты на месяц, чтобы избежать перерасхода</p>
      <UButton class="mt-4" color="emerald" label="Установить первый лимит" @click="isModalOpen = true" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <UCard
        v-for="b in budgets.budgets.value"
        :key="b.budget.id"
        class="relative overflow-hidden"
      >
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="text-2xl">{{ b.budget.category?.icon || '📦' }}</span>
              <h3 class="font-semibold">{{ b.budget.category?.name || 'Общий бюджет' }}</h3>
            </div>
            <UBadge
              :color="b.percentage > 100 ? 'rose' : b.percentage > 80 ? 'amber' : 'emerald'"
              variant="subtle"
            >
              {{ b.percentage.toFixed(0) }}%
            </UBadge>
          </div>

          <div class="space-y-1">
            <div class="flex justify-between text-xs text-gray-500">
              <span>Потрачено: {{ formatCurrency(b.spent) }}</span>
              <span>Лимит: {{ formatCurrency(b.budget.limit_amount) }}</span>
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
            <label class="block text-xs font-medium mb-1">Сумма лимита (₽)</label>
            <UInput v-model.number="newLimit" type="number" placeholder="25000" />
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
        <div class="flex justify-end gap-2 pt-2">
          <UButton color="gray" variant="ghost" label="Отмена" @click="isModalOpen = false" />
          <UButton color="emerald" label="Создать" @click="handleCreate" />
        </div>
      </div>
    </UModal>
  </div>
</template>

<script setup lang="ts">
const budgets = useBudgets()
const isModalOpen = ref(false)
const newLimit = ref(20000)
const newPeriod = ref('monthly')

const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(val || 0)
}

const handleCreate = async () => {
  if (!newLimit.value) return
  await budgets.createBudget({
    limit_amount: newLimit.value,
    period: newPeriod.value,
  })
  isModalOpen.value = false
}

onMounted(() => {
  budgets.fetchBudgets()
})
</script>
