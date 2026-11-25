<template>
  <div>
    <h2 class="text-xl font-bold mb-1 text-center">Создать аккаунт</h2>
    <p class="text-xs text-gray-500 mb-6 text-center">Начните вести умный бюджет уже сегодня</p>

    <form class="space-y-4" @submit.prevent="handleRegister">
      <div>
        <label class="block text-xs font-medium mb-1">Ваше имя</label>
        <UInput v-model="name" placeholder="Иван" required />
      </div>

      <div>
        <label class="block text-xs font-medium mb-1">Email</label>
        <UInput v-model="email" type="email" placeholder="user@example.com" required />
      </div>

      <div>
        <label class="block text-xs font-medium mb-1">Пароль</label>
        <UInput v-model="password" type="password" placeholder="••••••••" required />
      </div>

      <div v-if="errorMsg" class="text-xs text-rose-500">
        {{ errorMsg }}
      </div>

      <UButton
        type="submit"
        color="emerald"
        block
        label="Зарегистрироваться"
        :loading="isLoading"
      />
    </form>

    <p class="text-xs text-center text-gray-500 mt-6">
      Уже есть аккаунт?
      <NuxtLink to="/auth/login" class="text-emerald-600 font-semibold hover:underline">
        Войти
      </NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const auth = useAuth()
const name = ref('')
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMsg = ref('')

const handleRegister = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    await auth.register({
      name: name.value,
      email: email.value,
      password: password.value,
      currency: 'KZT',
    })
    navigateTo('/')
  } catch (err: any) {
    errorMsg.value = formatApiError(err, 'Ошибка при регистрации')
  } finally {
    isLoading.value = false
  }
}
</script>
