<template>
  <div class="max-w-2xl space-y-6">
    <div>
      <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Профиль баптаулары</h2>
      <p class="text-sm text-slate-500">Жеке деректерді, есеп айырысу валютасын және қауіпсіздік параметрлерін басқару</p>
    </div>

    <!-- Account Summary Header -->
    <UCard>
      <div class="flex items-center gap-4">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-400 to-teal-600 text-white font-extrabold text-xl flex items-center justify-center shadow-md shadow-emerald-500/20">
          {{ userInitial }}
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-bold text-slate-900 dark:text-white truncate">
            {{ auth.user.value?.name || 'Пайдаланушы' }}
          </h3>
          <p class="text-xs text-slate-500 truncate">{{ auth.user.value?.email }}</p>
        </div>
      </div>
    </UCard>

    <!-- Editable Profile Form -->
    <UCard>
      <form class="space-y-4" @submit.prevent="handleSave">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
            Пайдаланушы аты
          </label>
          <UInput v-model="name" size="lg" icon="i-heroicons-user" placeholder="Аты-жөніңіз" required />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
            Негізгі валюта
          </label>
          <USelect
            v-model="selectedCurrency"
            size="lg"
            :options="[
              { label: 'Қазақстан теңгесі (₸ — KZT)', value: 'KZT' },
              { label: 'АҚШ доллары ($ — USD)', value: 'USD' },
              { label: 'Еуро (€ — EUR)', value: 'EUR' },
              { label: 'Ресей рублі (₽ — RUB)', value: 'RUB' },
            ]"
          />
        </div>

        <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 ring-1 ring-slate-200/70 dark:ring-slate-700/60 flex items-start gap-3">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Google Gemini API кілті (<code class="font-mono font-semibold">GEMINI_API_KEY</code>) қауіпсіздік мақсатында тек сервердегі <code class="font-mono font-semibold">backend/.env</code> файлында сақталады және браузерге жіберілмейді.
          </p>
        </div>

        <div
          v-if="statusMsg"
          role="status"
          class="flex items-center gap-2 text-xs font-medium rounded-xl px-3.5 py-2.5"
          :class="
            isError
              ? 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 ring-1 ring-rose-200 dark:ring-rose-900/70'
              : 'text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/40 ring-1 ring-emerald-200 dark:ring-emerald-900/70'
          "
        >
          <UIcon :name="isError ? 'i-heroicons-exclamation-circle' : 'i-heroicons-check-circle'" class="w-4 h-4 shrink-0" />
          <span>{{ statusMsg }}</span>
        </div>

        <div class="pt-2">
          <UButton type="submit" color="emerald" size="md" label="Өзгерістерді сақтау" :loading="isSaving" />
        </div>
      </form>
    </UCard>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const name = ref(auth.user.value?.name || '')
const selectedCurrency = ref(auth.user.value?.currency || 'KZT')
const isSaving = ref(false)
const statusMsg = ref('')
const isError = ref(false)

const userInitial = computed(() => {
  const n = auth.user.value?.name?.trim()
  return n ? n.charAt(0).toUpperCase() : 'S'
})

watch(
  () => auth.user.value,
  (u) => {
    if (u) {
      name.value = u.name
      selectedCurrency.value = u.currency
    }
  },
  { immediate: true },
)

const handleSave = async () => {
  statusMsg.value = ''
  isError.value = false
  if (!name.value.trim()) {
    isError.value = true
    statusMsg.value = 'Пайдаланушы аты бос болмауы керек'
    return
  }
  isSaving.value = true
  try {
    await auth.updateProfile({
      name: name.value.trim(),
      currency: selectedCurrency.value,
    })
    statusMsg.value = 'Профиль баптаулары сәтті сақталды'
  } catch (err: any) {
    isError.value = true
    statusMsg.value = formatApiError(err, 'Баптауларды сақтау мүмкін болмады')
  } finally {
    isSaving.value = false
  }
}
</script>
