<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <UNotifications />
</template>

<script setup lang="ts">
const auth = useAuth()

onMounted(async () => {
  if (auth.isAuthenticated.value) {
    await auth.fetchUser()
  }
})
</script>
