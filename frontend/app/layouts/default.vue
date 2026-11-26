<template>
  <div class="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
    <!-- Desktop Sidebar -->
    <aside class="hidden md:flex w-[256px] lg:w-[268px] shrink-0 border-r border-slate-200/80 dark:border-slate-800/80 flex-col justify-between p-4 bg-white dark:bg-slate-900/95">
      <div class="space-y-6">
        <!-- Brand Logo -->
        <NuxtLink to="/" class="flex items-center gap-3 px-2.5 py-1 group">
          <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-md shadow-emerald-500/20 group-hover:scale-105 transition-transform">
            <UIcon name="i-heroicons-chart-bar-square" class="w-5 h-5" />
          </div>
          <div>
            <span class="block text-lg font-extrabold tracking-tight text-slate-900 dark:text-white leading-none">
              SmartBudget
            </span>
            <span class="text-[11px] font-medium text-slate-400">Жеке қаржы жүйесі</span>
          </div>
        </NuxtLink>

        <!-- Grouped Navigation -->
        <div class="space-y-5">
          <div v-for="group in navGroups" :key="group.title" class="space-y-1">
            <p class="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
              {{ group.title }}
            </p>
            <NuxtLink
              v-for="item in group.items"
              :key="item.path"
              :to="item.path"
              class="relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all"
              :class="[
                route.path === item.path
                  ? 'bg-emerald-500/10 dark:bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-semibold ring-1 ring-emerald-500/20'
                  : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-100',
              ]"
            >
              <UIcon
                :name="item.icon"
                class="w-5 h-5 shrink-0"
                :class="route.path === item.path ? 'text-emerald-600 dark:text-emerald-400' : 'text-slate-400 dark:text-slate-500'"
              />
              <span class="truncate">{{ item.label }}</span>
              <span
                v-if="item.badge"
                class="ml-auto text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-md bg-teal-500/15 text-teal-600 dark:text-teal-300"
              >
                {{ item.badge }}
              </span>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- User Profile Card -->
      <div class="rounded-2xl bg-slate-50 dark:bg-slate-800/50 ring-1 ring-slate-200/70 dark:ring-slate-800 p-3 flex items-center justify-between gap-2">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20 ring-1 ring-emerald-500/30 text-emerald-700 dark:text-emerald-300 font-bold text-sm flex items-center justify-center shrink-0">
            {{ userInitial }}
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5">
              <p class="text-xs font-bold text-slate-900 dark:text-white truncate">
                {{ auth.user.value?.name || 'Пайдаланушы' }}
              </p>
              <span class="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-300">
                {{ auth.user.value?.currency || 'KZT' }}
              </span>
            </div>
            <p class="text-[11px] text-slate-500 dark:text-slate-400 truncate">
              {{ auth.user.value?.email || '' }}
            </p>
          </div>
        </div>
        <UButton
          color="gray"
          variant="ghost"
          icon="i-heroicons-arrow-right-on-rectangle"
          size="xs"
          title="Жүйеден шығу"
          @click="auth.logout"
        />
      </div>
    </aside>

    <!-- Mobile Navigation Drawer -->
    <USlideover v-model="isMobileMenuOpen" side="left">
      <div class="h-full flex flex-col justify-between p-5 bg-white dark:bg-slate-900">
        <div class="space-y-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white">
                <UIcon name="i-heroicons-chart-bar-square" class="w-5 h-5" />
              </div>
              <span class="text-lg font-extrabold tracking-tight">SmartBudget</span>
            </div>
            <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" @click="isMobileMenuOpen = false" />
          </div>

          <div class="space-y-4">
            <div v-for="group in navGroups" :key="group.title" class="space-y-1">
              <p class="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                {{ group.title }}
              </p>
              <NuxtLink
                v-for="item in group.items"
                :key="item.path"
                :to="item.path"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium"
                :class="
                  route.path === item.path
                    ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-300 font-semibold'
                    : 'text-slate-600 dark:text-slate-400'
                "
                @click="isMobileMenuOpen = false"
              >
                <UIcon :name="item.icon" class="w-5 h-5" />
                <span>{{ item.label }}</span>
              </NuxtLink>
            </div>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div class="truncate text-xs">
            <p class="font-bold truncate">{{ auth.user.value?.name || 'Пайдаланушы' }}</p>
            <p class="text-slate-500 truncate">{{ auth.user.value?.email }}</p>
          </div>
          <UButton
            color="rose"
            variant="soft"
            size="xs"
            icon="i-heroicons-arrow-right-on-rectangle"
            label="Шығу"
            @click="auth.logout"
          />
        </div>
      </div>
    </USlideover>

    <!-- Main Content Column -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top Header -->
      <header class="h-16 shrink-0 border-b border-slate-200/80 dark:border-slate-800/80 px-4 sm:px-6 lg:px-8 flex items-center justify-between bg-white/85 dark:bg-slate-900/80 backdrop-blur-md">
        <div class="flex items-center gap-3 min-w-0">
          <UButton
            class="md:hidden"
            color="gray"
            variant="ghost"
            icon="i-heroicons-bars-3"
            @click="isMobileMenuOpen = true"
          />
          <div class="min-w-0">
            <h1 class="text-base sm:text-lg font-bold tracking-tight text-slate-900 dark:text-white truncate">
              {{ currentItem?.label || 'SmartBudget' }}
            </h1>
            <p v-if="currentItem?.subtitle" class="hidden sm:block text-xs text-slate-500 dark:text-slate-400 truncate">
              {{ currentItem.subtitle }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2.5 shrink-0">
          <ClientOnly>
            <UColorModeButton />
          </ClientOnly>
          <UButton
            icon="i-heroicons-plus"
            label="Жаңа операция"
            color="emerald"
            size="sm"
            class="shadow-sm shadow-emerald-500/20"
            @click="navigateTo('/transactions?action=new')"
          />
        </div>
      </header>

      <!-- Page Body -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div class="max-w-7xl mx-auto">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const auth = useAuth()
const isMobileMenuOpen = ref(false)

interface NavItem {
  label: string
  subtitle: string
  path: string
  icon: string
  badge?: string
}

const navGroups: { title: string; items: NavItem[] }[] = [
  {
    title: 'Негізгі мәзір',
    items: [
      {
        label: 'Басты панель',
        subtitle: 'Ағымдағы айдағы қаржылық шолу',
        path: '/',
        icon: 'i-heroicons-squares-2x2',
      },
      {
        label: 'Операциялар',
        subtitle: 'Кірістер мен шығыстар тарихы',
        path: '/transactions',
        icon: 'i-heroicons-arrows-right-left',
      },
      {
        label: 'Бюджеттер',
        subtitle: 'Санаттар мен кезеңдер бойынша шығыс лимиттері',
        path: '/budgets',
        icon: 'i-heroicons-chart-pie',
      },
      {
        label: 'Аналитика',
        subtitle: 'Шығыс құрылымы мен айлық трендтер',
        path: '/analytics',
        icon: 'i-heroicons-presentation-chart-line',
      },
    ],
  },
  {
    title: 'Ақылды құралдар',
    items: [
      {
        label: 'Жеңілдіктер мен баға',
        subtitle: 'Бағаны ЖИ арқылы тексеру және науқандар',
        path: '/deals',
        icon: 'i-heroicons-tag',
      },
      {
        label: 'ЖИ Көмекші',
        subtitle: 'Google Gemini негізіндегі жеке қаржы коучы',
        path: '/ai',
        icon: 'i-heroicons-sparkles',
        badge: 'AI',
      },
      {
        label: 'Баптаулар',
        subtitle: 'Жеке профиль мен негізгі валюта',
        path: '/settings',
        icon: 'i-heroicons-cog-6-tooth',
      },
    ],
  },
]

const allItems = navGroups.flatMap(g => g.items)
const currentItem = computed(() => allItems.find(item => item.path === route.path))

const userInitial = computed(() => {
  const name = auth.user.value?.name?.trim()
  return name ? name.charAt(0).toUpperCase() : 'S'
})
</script>
