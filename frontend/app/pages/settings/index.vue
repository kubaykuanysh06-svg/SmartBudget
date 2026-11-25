<template>
  <div class="max-w-2xl space-y-6">
    <div>
      <h2 class="text-xl font-bold">Настройки профиля</h2>
      <p class="text-sm text-gray-500">Управление именем, валютой аккаунта и параметрами ИИ</p>
    </div>

    <UCard>
      <form class="space-y-4" @submit.prevent="handleSave">
        <div>
          <label class="block text-xs font-medium mb-1">Имя пользователя</label>
          <UInput v-model="name" placeholder="Ваше имя" required />
        </div>

        <div>
          <label class="block text-xs font-medium mb-1">Основная валюта</label>
          <USelect
            v-model="selectedCurrency"
            :options="[
              { label: 'Казахстанский тенге (₸)', value: 'KZT' },
              { label: 'Доллар США ($)', value: 'USD' },
              { label: 'Евро (€)', value: 'EUR' },
              { label: 'Российский рубль (₽)', value: 'RUB' },
            ]"
          />
        </div>

        <div class="p-3 rounded-xl bg-gray-50 dark:bg-gray-800/60 text-xs text-gray-500">
          Ключ Google Gemini API (<code class="font-mono">GEMINI_API_KEY</code>) хранится только на сервере в
          <code class="font-mono">backend/.env</code> и никогда не передаётся в браузер.
        </div>

        <div v-if="statusMsg" class="text-xs" :class="isError ? 'text-rose-600' : 'text-emerald-600'">
          {{ statusMsg }}
        </div>

        <div class="pt-2">
          <UButton type="submit" color="emerald" label="Сохранить изменения" :loading="isSaving" />
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
    statusMsg.value = 'Имя не может быть пустым'
    return
  }
  isSaving.value = true
  try {
    await auth.updateProfile({
      name: name.value.trim(),
      currency: selectedCurrency.value,
    })
    statusMsg.value = 'Настройки профиля сохранены'
  } catch (err: any) {
    isError.value = true
    statusMsg.value = formatApiError(err, 'Не удалось сохранить настройки')
  } finally {
    isSaving.value = false
  }
}
</script>
