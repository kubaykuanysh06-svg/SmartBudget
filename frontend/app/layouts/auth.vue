<template>
  <div class="sb-dual">
    <section class="sb-auth-display">
      <div class="sb-orbit" aria-hidden="true" />
      <div class="sb-orbit-small" aria-hidden="true" />
      <NuxtLink to="/" class="sb-brand">
        <span class="sb-brand-mark"><UIcon name="i-heroicons-wallet" class="h-5 w-5" /></span>
        SmartBudget
      </NuxtLink>
      <div class="sb-auth-visual">
        <h1>{{ t('Қаржыңыз бір жерде') }}<span class="text-violet-200">.</span></h1>
        <p class="mt-5">{{ t('Чектерді жүктеңіз, шығысты санаттарға бөліңіз және бюджет қалдығын бақылаңыз.') }}</p>
        <div class="relative mt-7 grid max-w-xs gap-2.5">
          <div v-for="feature in features" :key="feature.label" class="sb-auth-feature">
            <UIcon :name="feature.icon" class="h-5 w-5 shrink-0 text-violet-200" />
            {{ feature.label }}
          </div>
        </div>
      </div>
      <p class="text-xs text-violet-200">© {{ new Date().getFullYear() }} SmartBudget</p>
    </section>

    <main class="sb-auth-form">
      <div class="flex items-center justify-between">
        <div class="min-[760px]:invisible">
          <NuxtLink to="/" class="sb-brand">
            <span class="sb-brand-mark"><UIcon name="i-heroicons-wallet" class="h-5 w-5" /></span>
            SmartBudget
          </NuxtLink>
        </div>
        <ClientOnly><ThemeToggle /></ClientOnly>
      </div>
      <div class="sb-auth-card sb-panel my-7"><slot /></div>
    </main>
  </div>
</template>

<script setup lang="ts">
const { t } = useLanguage()
const features = [
  { label: t('Фото және PDF чектер'), icon: 'i-heroicons-document-text' },
  { label: t('Санаттарға бөлінген шығыс'), icon: 'i-heroicons-chart-pie' },
  { label: t('Жеке бюджет лимиттері'), icon: 'i-heroicons-adjustments-horizontal' },
]
</script>
