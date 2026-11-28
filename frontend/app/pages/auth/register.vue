<template>
  <div class="space-y-6">
    <div class="space-y-1.5">
      <h2 class="sb-page-title">
        {{ t('Жаңа аккаунт ашу') }}
      </h2>
      <p class="text-sm text-slate-500 dark:text-slate-400">
        {{ t('Бір минутта тіркеліп, бюджетіңізді теңгемен (₸) жүргізуді бастаңыз') }}
      </p>
    </div>

    <form class="space-y-4" @submit.prevent="handleRegister">
      <div>
        <label for="register-name" class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          {{ t('Аты-жөніңіз') }}
        </label>
        <UInput
          id="register-name"
          autocomplete="name"
          v-model="name"
          size="lg"
          icon="i-heroicons-user"
          :placeholder="t('Мысалы: Айдос')"
          required
        />
      </div>

      <div>
        <label for="register-email" class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          {{ t('Электрондық пошта') }}
        </label>
        <UInput
          id="register-email"
          autocomplete="email"
          v-model="email"
          type="email"
          size="lg"
          icon="i-heroicons-envelope"
          placeholder="name@example.com"
          required
        />
      </div>

      <div>
        <label for="register-password" class="block text-xs font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-300 mb-1.5">
          {{ t('Құпиясөз') }}
        </label>
        <UInput
          id="register-password"
          autocomplete="new-password"
          v-model="password"
          type="password"
          size="lg"
          icon="i-heroicons-lock-closed"
          :placeholder="t('Кемінде 8 таңба')"
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
        color="primary"
        size="lg"
        block
        :label="t('Тіркелу')"
        trailing-icon="i-heroicons-sparkles"
        :loading="isLoading"
      />
    </form>

    <div class="pt-4 border-t border-slate-100 dark:border-slate-800 text-center text-sm text-slate-500 dark:text-slate-400">
      {{ t('Аккаунтыңыз бар ма?') }}
      <NuxtLink to="/auth/login" class="sb-text-link ml-1">
        {{ t('Жүйеге кіру') }}
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'auth',
})

const { t } = useLanguage()
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
    errorMsg.value = t(formatApiError(err, t('Тіркелу кезінде қате шықты')))
  } finally {
    isLoading.value = false
  }
}
</script>
