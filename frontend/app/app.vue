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

onMounted(async () => {
  if (auth.isAuthenticated.value) {
    await auth.fetchUser()
  }
})
</script>
