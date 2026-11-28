<template>
  <div>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <UNotifications />
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const { language, tr } = useLanguage()
useHead({
  htmlAttrs: { lang: language },
  title: computed(() => tr('SmartBudget — Ақылды жеке қаржы жүйесі', 'SmartBudget — умная система личных финансов', 'SmartBudget — smart personal finance')),
})

onMounted(async () => {
  if (auth.isAuthenticated.value) {
    await auth.fetchUser()
  }
})
</script>
