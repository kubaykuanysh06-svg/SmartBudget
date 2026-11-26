<template>
  <div class="space-y-6">
    <div class="space-y-1.5">
      <h2 class="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">
        Жаңа аккаунт ашу
      </h2>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        Бір минутта тіркеліп, бюджетіңізді теңгемен (₸) жүргізуді бастаңыз
      </p>
    </div>

    <form class="space-y-4" @submit.prevent="handleRegister">
      <div>
        <label class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          Аты-жөніңіз
        </label>
        <UInput
          v-model="name"
          size="lg"
          icon="i-heroicons-user"
          placeholder="Мысалы: Айдос"
          required
        />
      </div>

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
          placeholder="Кемінде 8 таңба"
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
        label="Тіркелу"
        trailing-icon="i-heroicons-sparkles"
        :loading="isLoading"
      />
    </form>

    <div class="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-sm text-slate-500 dark:text-slate-400">
      Аккаунтыңыз бар ма?
      <NuxtLink to="/auth/login" class="text-emerald-600 dark:text-emerald-400 font-semibold hover:underline ml-1">
        Жүйеге кіру
      </NuxtLink>
    </div>
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
      name: name.value.trim(),
      email: email.value.trim(),
      password: password.value,
      currency: 'KZT',
    })
    navigateTo('/')
  } catch (err: any) {
    errorMsg.value = formatApiError(err, 'Тіркелу кезінде қате шықты')
  } finally {
    isLoading.value = false
  }
}
</script>
