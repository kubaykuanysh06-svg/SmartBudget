<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 border-r border-gray-200 dark:border-gray-800 flex flex-col justify-between p-4 bg-white dark:bg-gray-900">
      <div class="space-y-6">
        <!-- Logo -->
        <div class="flex items-center gap-3 px-2">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center text-white font-bold text-lg shadow-md">
            💰
          </div>
          <span class="text-xl font-bold tracking-tight bg-gradient-to-r from-emerald-600 to-teal-500 bg-clip-text text-transparent">
            SmartBudget
          </span>
        </div>

        <!-- Navigation Links -->
        <nav class="space-y-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
            :class="[
              route.path === item.path
                ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 font-semibold'
                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-100'
            ]"
          >
            <UIcon :name="item.icon" class="w-5 h-5" />
            <span>{{ item.label }}</span>
          </NuxtLink>
        </nav>
      </div>

      <!-- User / Logout -->
      <div class="border-t border-gray-200 dark:border-gray-800 pt-4 px-2 flex items-center justify-between">
        <div class="flex items-center gap-3 truncate">
          <UAvatar :alt="auth.user.value?.name || 'User'" size="sm" />
          <div class="truncate text-xs">
            <p class="font-medium truncate">{{ auth.user.value?.name || 'Пользователь' }}</p>
            <p class="text-gray-500 truncate">{{ auth.user.value?.email || 'Гость' }}</p>
          </div>
        </div>
        <UButton
          color="gray"
          variant="ghost"
          icon="i-heroicons-arrow-right-on-rectangle"
          size="sm"
          title="Выйти"
          @click="auth.logout"
        />
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Header -->
      <header class="h-16 border-b border-gray-200 dark:border-gray-800 px-6 flex items-center justify-between bg-white dark:bg-gray-900">
        <h1 class="text-lg font-semibold">{{ currentTitle }}</h1>
        <div class="flex items-center gap-3">
          <ClientOnly>
            <UColorModeButton />
          </ClientOnly>
          <UButton
            icon="i-heroicons-plus"
            label="Новая покупка"
            color="emerald"
            size="sm"
            @click="navigateTo('/transactions?action=new')"
          />
        </div>
      </header>

      <!-- Page Body -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const auth = useAuth()

const navItems = [
  { label: 'Дашборд', path: '/', icon: 'i-heroicons-home' },
  { label: 'Транзакции', path: '/transactions', icon: 'i-heroicons-banknotes' },
  { label: 'Бюджеты', path: '/budgets', icon: 'i-heroicons-chart-pie' },
  { label: 'Аналитика', path: '/analytics', icon: 'i-heroicons-presentation-chart-line' },
  { label: 'Скидки и цены', path: '/deals', icon: 'i-heroicons-tag' },
  { label: 'ИИ Ассистент', path: '/ai', icon: 'i-heroicons-sparkles' },
  { label: 'Настройки', path: '/settings', icon: 'i-heroicons-cog-6-tooth' },
]

const currentTitle = computed(() => {
  const current = navItems.find((item) => item.path === route.path)
  return current ? current.label : 'SmartBudget'
})
</script>
