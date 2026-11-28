<template>
  <div class="max-w-2xl space-y-6">
    <div>
      <h2 class="sb-page-title">{{ t('Профиль баптаулары') }}</h2>
      <p class="sb-page-caption">{{ t('Жеке деректерді, есеп айырысу валютасын және қауіпсіздік параметрлерін басқару') }}</p>
    </div>

    <!-- Account Summary Header -->
    <UCard>
      <div class="flex items-center gap-4">
        <div class="sb-avatar !h-14 !w-14 !rounded-2xl text-xl">
          {{ userInitial }}
        </div>
        <div class="min-w-0">
          <h3 class="text-base font-bold text-slate-900 dark:text-white truncate">
            {{ auth.user.value?.name || t('Пайдаланушы') }}
          </h3>
          <p class="text-xs text-slate-500 truncate">{{ auth.user.value?.email }}</p>
        </div>
      </div>
    </UCard>

    <!-- Editable Profile Form -->
    <UCard>
      <UFormGroup :label="tr('Интерфейс тілі', 'Язык интерфейса', 'Interface language')" name="language">
        <USelect v-model="language" :options="languages" class="max-w-xs" />
      </UFormGroup>
    </UCard>
    <UCard>
      <form class="space-y-4" @submit.prevent="handleSave">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
            {{ t('Пайдаланушы аты') }}
          </label>
          <UInput v-model="name" size="lg" icon="i-heroicons-user" :placeholder="t('Аты-жөніңіз')" required />
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
            {{ t('Негізгі валюта') }}
          </label>
          <USelect
            v-model="selectedCurrency"
            size="lg"
            :options="[
              { label: t('Қазақстан теңгесі (₸ — KZT)'), value: 'KZT' },
              { label: t('АҚШ доллары ($ — USD)'), value: 'USD' },
              { label: t('Еуро (€ — EUR)'), value: 'EUR' },
              { label: t('Ресей рублі (₽ — RUB)'), value: 'RUB' },
            ]"
          />
        </div>

        <div class="p-4 rounded-2xl bg-slate-50 dark:bg-slate-800/60 ring-1 ring-slate-200/70 dark:ring-slate-700/60 flex items-start gap-3">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
          <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            {{ tr('Google Gemini API кілті (GEMINI_API_KEY) қауіпсіздік үшін тек сервердегі backend/.env файлында сақталады және браузерге жіберілмейді.', 'Ключ Google Gemini API (GEMINI_API_KEY) из соображений безопасности хранится только в файле backend/.env на сервере и не передаётся в браузер.', 'For security, the Google Gemini API key (GEMINI_API_KEY) is stored only in backend/.env on the server and is never sent to the browser.') }}
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
          <UButton type="submit" color="primary" size="md" :label="t('Өзгерістерді сақтау')" :loading="isSaving" />
        </div>
      </form>
    </UCard>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const { tr, language, t } = useLanguage()
const languages = [{ value: 'kk', label: 'Қазақша' }, { value: 'ru', label: 'Русский' }, { value: 'en', label: 'English' }]
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
    statusMsg.value = t('Пайдаланушы аты бос болмауы керек')
    return
  }
  isSaving.value = true
  try {
    await auth.updateProfile({
      name: name.value.trim(),
      currency: selectedCurrency.value,
    })
    statusMsg.value = t('Профиль баптаулары сәтті сақталды')
  } catch (err: any) {
    isError.value = true
    statusMsg.value = t(formatApiError(err, t('Баптауларды сақтау мүмкін болмады')))
  } finally {
    isSaving.value = false
  }
}
</script>
