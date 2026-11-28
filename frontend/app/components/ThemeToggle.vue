<template>
  <button type="button" class="sb-theme-button" :aria-label="label" :title="label" @click="toggle">
    <UIcon :name="isDark ? 'i-heroicons-sun' : 'i-heroicons-moon'" class="h-[17px] w-[17px]" aria-hidden="true" />
  </button>
</template>

<script setup lang="ts">
const { t } = useLanguage()
const colorMode = useColorMode()
const isDark = computed(() => colorMode.value === 'dark')
const label = computed(() => isDark.value ? t('Ашық тақырыпқа ауысу') : t('Қараңғы тақырыпқа ауысу'))

const toggle = () => { colorMode.preference = isDark.value ? 'light' : 'dark' }
</script>
