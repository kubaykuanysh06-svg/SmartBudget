<template>
  <div class="space-y-6">
    <div class="space-y-1.5">
      <h2 class="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">
        Жүйеге кіру
      </h2>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        Жеке қаржы панеліне өту үшін деректеріңізді енгізіңіз
      </p>
    </div>

    <form class="space-y-4" @submit.prevent="handleLogin">
      <div>
        <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          Электрондық пошта
        </label>
        <UInput
          v-model="email"
          type="email"
          size="lg"
          icon="i-heroicons-envelope"
          placeholder="name@example.com"
          required
        />
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          Құпиясөз
        </label>
        <UInput
          v-model="password"
          type="password"
          size="lg"
          icon="i-heroicons-lock-closed"
          placeholder="••••••••"
          required
        />
      </div>

      <div
        v-if="errorMsg"
        role="alert"
        class="flex items-center gap-2 text-xs font-medium text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 ring-1 ring-rose-200 dark:ring-rose-900/70 rounded-xl px-3.5 py-2.5"
      >
        <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 shrink-0" />
        <span>{{ errorMsg }}</span>
      </div>

      <UButton
        type="submit"
        color="emerald"
        size="lg"
        block
        label="Кіру"
        trailing-icon="i-heroicons-arrow-right"
        :loading="isLoading"
      />
    </form>

    <div class="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-sm text-slate-500 dark:text-slate-400">
      Аккаунтыңыз жоқ па?
      <NuxtLink to="/auth/register" class="text-emerald-600 dark:text-emerald-400 font-semibold hover:underline ml-1">
        Тіркелу
      </NuxtLink>
    </div>
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
    await auth.login({ email: email.value.trim(), password: password.value })
    navigateTo('/')
  } catch (err: any) {
    errorMsg.value = formatApiError(err, 'Email немесе құпиясөз қате')
  } finally {
    isLoading.value = false
  }
}
</script>
