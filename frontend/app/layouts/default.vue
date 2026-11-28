<template>
  <div class="sb-shell">
    <a href="#main-content" class="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:m-2 focus:rounded-lg focus:bg-white focus:p-2">
      {{ t('Негізгі мазмұнға өту') }}
    </a>

    <aside class="sb-sidebar hidden lg:flex" :aria-label="t('Негізгі мәзір')">
      <NuxtLink to="/" class="sb-brand" :aria-label="t('SmartBudget басты панелі')">
        <span class="sb-brand-mark"><UIcon name="i-heroicons-wallet" class="h-5 w-5" /></span>
        <span>SmartBudget</span>
      </NuxtLink>

      <nav class="sb-nav space-y-7" :aria-label="t('Бөлімдер')">
        <div v-for="group in navGroups" :key="group.title" class="space-y-1">
          <p class="sb-nav-heading">{{ group.title }}</p>
          <NuxtLink
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="sb-nav-link"
            :class="{ 'sb-nav-active': route.path === item.path }"
            :aria-current="route.path === item.path ? 'page' : undefined"
          >
            <UIcon :name="item.icon" class="h-[19px] w-[19px] shrink-0" />
            <span class="truncate">{{ item.label }}</span>
          </NuxtLink>
        </div>
      </nav>

      <div class="sb-profile">
        <NuxtLink to="/settings" class="flex min-w-0 flex-1 items-center gap-2.5">
          <span class="sb-avatar">{{ userInitial }}</span>
          <span class="min-w-0">
            <span class="block truncate text-sm font-bold">{{ auth.user.value?.name || t('Пайдаланушы') }}</span>
            <span class="sb-muted block truncate text-xs">{{ auth.user.value?.email || auth.user.value?.currency || 'KZT' }}</span>
          </span>
        </NuxtLink>
        <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-right-on-rectangle" size="xs" :aria-label="t('Жүйеден шығу')" :title="t('Жүйеден шығу')" @click="auth.logout" />
      </div>
    </aside>

    <div class="sb-main-column">
      <header class="sb-topbar">
        <div class="sb-topbar-inner">
          <NuxtLink to="/" class="sb-brand lg:hidden" :aria-label="t('SmartBudget басты панелі')">
            <span class="sb-brand-mark"><UIcon name="i-heroicons-wallet" class="h-5 w-5" /></span>
            <span class="hidden min-[360px]:inline">SmartBudget</span>
          </NuxtLink>
          <div class="hidden items-center gap-2 text-sm lg:flex">
            <UIcon name="i-heroicons-squares-2x2" class="sb-muted h-4 w-4" />
            <UIcon name="i-heroicons-chevron-right" class="sb-muted h-3 w-3" />
            <span class="font-semibold">{{ currentItem?.label || 'SmartBudget' }}</span>
          </div>
          <div class="flex shrink-0 items-center gap-2 sm:gap-3">
            <ClientOnly><ThemeToggle /></ClientOnly>
            <UButton to="/transactions?action=new" icon="i-heroicons-plus" color="primary" size="sm" class="sb-top-action" :aria-label="t('Жаңа операция')">
              <span class="hidden min-[430px]:inline">{{ t('Жаңа операция') }}</span>
            </UButton>
          </div>
        </div>
      </header>

      <main id="main-content" ref="mainContent" class="sb-main" tabindex="-1">
        <div class="sb-content"><slot /></div>
      </main>

      <nav class="sb-mobile-nav lg:hidden" :aria-label="t('Мобильді мәзір')">
        <NuxtLink
          v-for="item in mobileItems"
          :key="item.path"
          :to="item.path"
          class="sb-mobile-item"
          :class="{ 'sb-mobile-active': route.path === item.path }"
          :aria-current="route.path === item.path ? 'page' : undefined"
        >
          <UIcon :name="item.icon" class="h-5 w-5" />
          <span>{{ item.short }}</span>
        </NuxtLink>
        <button type="button" class="sb-mobile-item" :class="{ 'sb-mobile-active': isMobileMenuOpen || !mobileItems.some(item => item.path === route.path) }" :aria-expanded="isMobileMenuOpen" @click="isMobileMenuOpen = true">
          <UIcon name="i-heroicons-ellipsis-horizontal-circle" class="h-5 w-5" />
          <span>{{ t('Тағы') }}</span>
        </button>
      </nav>
    </div>

    <USlideover v-model="isMobileMenuOpen" side="right">
      <div class="sb-drawer flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto p-5">
        <div class="flex items-center justify-between">
          <span class="sb-brand"><span class="sb-brand-mark"><UIcon name="i-heroicons-wallet" class="h-5 w-5" /></span>SmartBudget</span>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" :aria-label="t('Мәзірді жабу')" @click="isMobileMenuOpen = false" />
        </div>
        <nav v-for="group in navGroups" :key="group.title" :aria-label="group.title" class="space-y-1">
          <p class="sb-nav-heading">{{ group.title }}</p>
          <NuxtLink v-for="item in group.items" :key="item.path" :to="item.path" class="sb-nav-link" :class="{ 'sb-nav-active': route.path === item.path }" @click="isMobileMenuOpen = false">
            <UIcon :name="item.icon" class="h-5 w-5" />
            {{ item.label }}
          </NuxtLink>
        </nav>
        <div class="sb-profile mt-auto">
          <span class="sb-avatar">{{ userInitial }}</span>
          <span class="min-w-0 flex-1 truncate text-sm font-bold">{{ auth.user.value?.name || t('Пайдаланушы') }}</span>
          <UButton color="gray" variant="ghost" icon="i-heroicons-arrow-right-on-rectangle" :aria-label="t('Жүйеден шығу')" @click="auth.logout" />
        </div>
      </div>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
const { t } = useLanguage()
const route = useRoute()
const auth = useAuth()
const isMobileMenuOpen = ref(false)
const mainContent = ref<HTMLElement | null>(null)

const mobileItems = computed(() => [
  { label: t('Басты панель'), short: t('Басты бет'), path: '/', icon: 'i-heroicons-squares-2x2' },
  { label: t('Операциялар'), short: t('Операциялар'), path: '/transactions', icon: 'i-heroicons-arrows-right-left' },
  { label: t('Бюджеттер'), short: t('Бюджет'), path: '/budgets', icon: 'i-heroicons-wallet' },
  { label: t('Аналитика'), short: t('Аналитика'), path: '/analytics', icon: 'i-heroicons-chart-bar' },
])
const navGroups = computed(() => [
  { title: t('Қаржы'), items: mobileItems.value },
  {
    title: t('Құралдар'),
    items: [
      { label: t('Жеңілдіктер'), path: '/deals', icon: 'i-heroicons-tag' },
      { label: t('ЖИ көмекші'), path: '/ai', icon: 'i-heroicons-sparkles' },
      { label: t('Баптаулар'), path: '/settings', icon: 'i-heroicons-cog-6-tooth' },
    ],
  },
])
const currentItem = computed(() => navGroups.value.flatMap(group => group.items).find(item => item.path === route.path))
const userInitial = computed(() => auth.user.value?.name?.trim().charAt(0).toUpperCase() || 'S')

watch(() => route.path, () => {
  isMobileMenuOpen.value = false
  mainContent.value?.scrollTo({ top: 0 })
})
</script>
