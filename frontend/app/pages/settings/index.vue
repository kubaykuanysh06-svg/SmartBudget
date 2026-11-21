<template>
  <div class="max-w-2xl space-y-6">
    <div>
      <h2 class="text-xl font-bold">Настройки профиля</h2>
      <p class="text-sm text-gray-500">Управление валютой, аккаунтом и параметрами ИИ</p>
    </div>

    <UCard>
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-medium mb-1">Основная валюта</label>
          <USelect
            v-model="currency"
            :options="[
              { label: 'Российский рубль (₽)', value: 'RUB' },
              { label: 'Доллар США ($)', value: 'USD' },
              { label: 'Евро (€)', value: 'EUR' },
              { label: 'Казахстанский тенге (₸)', value: 'KZT' },
            ]"
          />
        </div>

        <div>
          <label class="block text-xs font-medium mb-1">Google Gemini API Key</label>
          <UInput
            v-model="geminiKey"
            type="password"
            placeholder="AIzaSy..."
          />
          <p class="text-[11px] text-gray-400 mt-1">
            Ключ используется для генерации персональных инсайтов, проверки цен и распознавания чеков.
          </p>
        </div>

        <div class="pt-2">
          <UButton color="emerald" label="Сохранить изменения" @click="handleSave" />
        </div>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
const currency = ref('RUB')
const geminiKey = ref('')

const handleSave = () => {
  alert('Настройки сохранены!')
}
</script>
