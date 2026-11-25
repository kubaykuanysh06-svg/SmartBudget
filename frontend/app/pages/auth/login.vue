<template>
  <div>
    <h2 class="text-xl font-bold mb-1 text-center">Вход в SmartBudget</h2>
    <p class="text-xs text-gray-500 mb-6 text-center">Управляйте расходами с подсказками ИИ</p>

    <form class="space-y-4" @submit.prevent="handleLogin">
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
        label="Войти"
        :loading="isLoading"
      />
    </form>

    <p class="text-xs text-center text-gray-500 mt-6">
      Нет аккаунта?
      <NuxtLink to="/auth/register" class="text-emerald-600 font-semibold hover:underline">
        Зарегистрироваться
      </NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const auth = useAuth()
const email = ref('')
const password = ref('')
const isLoading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  isLoading.value = true
  errorMsg.value = ''
  try {
    await auth.login({ email: email.value, password: password.value })
    navigateTo('/')
  } catch (err: any) {
    errorMsg.value = formatApiError(err, 'Неверный email или пароль')
  } finally {
    isLoading.value = false
  }
}
</script>
