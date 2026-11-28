<template>
  <div class="space-y-6">
    <div>
      <h2 class="sb-page-title">{{ t('ЖИ Қаржы кеңесшісі') }}</h2>
      <p class="sb-page-caption">{{ t('Google Gemini негізіндегі жеке бюджет коучы және шығындар аудиті') }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Chat Panel -->
      <div class="lg:col-span-8">
        <UCard
          class="flex h-[min(620px,72dvh)] min-h-[440px] flex-col"
          :ui="{ body: { base: 'flex-1 flex flex-col p-4 sm:p-5 overflow-hidden' } }"
        >
          <!-- Messages Stream -->
          <div ref="messageStream" class="flex-1 overflow-y-auto space-y-4 pr-1">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              class="flex gap-3"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                v-if="msg.role === 'assistant'"
                class="sb-icon-box"
              >
                <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
              </div>
              <div
                class="max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line"
                :class="
                  msg.role === 'user'
                    ? 'bg-violet-700 text-white rounded-br-sm shadow-sm'
                    : 'bg-[var(--sb-soft)] text-[var(--sb-ink)] rounded-bl-sm ring-1 ring-[var(--sb-line)]'
                "
              >
                {{ msg.text }}
                <UButton
                  v-if="msg.receipt"
                  type="button"
                  color="primary"
                  variant="soft"
                  size="sm"
                  icon="i-heroicons-plus"
                  :label="t('Шығысқа қосу')"
                  class="mt-2 block"
                  @click="reviewReceipt(msg.receipt)"
                />
              </div>
            </div>

            <div v-if="isThinking" class="flex items-center gap-2.5 text-xs text-slate-400 pl-1">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin text-emerald-500" />
              <span>{{ attachedPhoto ? t('ЖИ фотоны талдап жатыр...') : t('ЖИ шығыстарыңызды талдап жатыр...') }}</span>
            </div>
          </div>

          <!-- Quick Prompt Chips -->
          <div class="pt-3 mt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2 mb-3">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              type="button"
              class="rounded-xl bg-[var(--sb-soft)] px-3 py-1.5 text-xs font-medium text-[var(--sb-muted)] transition-colors hover:bg-[var(--sb-accent-soft)] hover:text-[var(--sb-accent)]"
              @click="sendQuickPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>

          <!-- Input Form -->
          <div v-if="attachedPhoto" class="mb-2 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <UIcon name="i-heroicons-photo" class="shrink-0" />
            <span class="truncate">{{ attachedPhoto.name }}</span>
            <UButton
              type="button"
              size="xs"
              color="gray"
              variant="ghost"
              icon="i-heroicons-x-mark"
              :aria-label="t('Фотоны алып тастау')"
              :disabled="isThinking"
              @click="attachedPhoto = null; photoError = ''"
            />
          </div>
          <p v-if="photoError" role="alert" class="mb-2 text-xs text-rose-600 dark:text-rose-400">{{ photoError }}</p>
          <form class="flex gap-2.5" @submit.prevent="handleSendMessage">
            <input
              ref="photoInput"
              type="file"
              accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
              class="hidden"
              @change="selectPhoto"
            />
            <UButton
              type="button"
              size="lg"
              color="gray"
              variant="outline"
              icon="i-heroicons-photo"
              :aria-label="t('Фото қосу')"
              :title="t('Фото қосу')"
              :disabled="isThinking"
              @click="photoInput?.click()"
            />
            <UInput
              v-model="inputMessage"
              size="lg"
              class="flex-1"
              :placeholder="attachedPhoto ? t('Фото туралы сұрағыңыз (міндетті емес)') : t('Үнемдеу немесе бюджет жоспарлау туралы сұрақ қойыңыз...')"
              :disabled="isThinking"
            />
            <UButton
              color="primary"
              size="lg"
              icon="i-heroicons-paper-airplane"
              type="submit"
              :aria-label="t('Жіберу')"
              :loading="isThinking"
            />
          </form>
        </UCard>
      </div>

      <!-- Insights Sidebar -->
      <div class="lg:col-span-4 space-y-4">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-amber-500/15 text-amber-500 flex items-center justify-center">
            <UIcon name="i-heroicons-light-bulb" class="w-4 h-4" />
          </div>
          <h3 class="font-bold text-base text-slate-900 dark:text-white">{{ t('Жеке инсайттар') }}</h3>
        </div>

        <div
          v-if="ai.insights.value.length === 0"
          class="p-6 text-center rounded-2xl bg-white dark:bg-slate-900/80 ring-1 ring-slate-200/80 dark:ring-slate-800 text-slate-400 text-xs leading-relaxed"
        >
          {{ t('Жеке қаржылық инсайттар мен ескертулерді алу үшін көбірек операция енгізіңіз немесе чатта сұрақ қойыңыз.') }}
        </div>

        <div v-else class="space-y-3">
          <UCard
            v-for="item in ai.insights.value"
            :key="item.id"
            :ui="{ body: { padding: 'p-4 sm:p-4' } }"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                :class="{
                  'bg-amber-500/15 text-amber-500': item.type === 'tip',
                  'bg-rose-500/15 text-rose-500': item.type === 'warning',
                  'bg-emerald-500/15 text-emerald-500': item.type === 'recommendation' || item.type === 'deal',
                }"
              >
                <UIcon
                  :name="item.type === 'warning' ? 'i-heroicons-exclamation-triangle' : 'i-heroicons-sparkles'"
                  class="w-4 h-4"
                />
              </div>
              <div class="flex-1 text-xs">
                <h4 class="font-bold text-slate-900 dark:text-white mb-1">{{ item.title }}</h4>
                <p class="text-slate-600 dark:text-slate-400 leading-relaxed">{{ item.content }}</p>
              </div>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { t } = useLanguage()
const ai = useAiInsights()
const { receiptFile } = useTransactions()

const reviewReceipt = (receipt: File) => {
  receiptFile.value = receipt
  return navigateTo({ path: '/transactions', query: { action: 'receipt' } })
}

const chatMessages = ref<{ role: 'user' | 'assistant'; text: string; receipt?: File }[]>([
  {
    role: 'assistant',
    text: t('Сәлеметсіз бе! Мен сіздің SmartBudget жеке қаржы көмекшіңізбін. Кіріс-шығысыңызды талдап, үнемдеу жолдарын ұсына аламын немесе айлық жинақ жоспарын құруға көмектесемін. Қандай сұрағыңыз бар?'),
  },
])

const inputMessage = ref('')
const isThinking = ref(false)
const photoInput = ref<HTMLInputElement | null>(null)
const attachedPhoto = shallowRef<File | null>(null)
const photoError = ref('')
const messageStream = ref<HTMLDivElement | null>(null)
const photoSizeError = t('Фото көлемі 5 МБ-тан аспауы керек.')
const photoFormatError = t('JPEG, PNG немесе WebP форматындағы фотоны таңдаңыз.')

const selectPhoto = (event: Event) => {
  const input = event.target as HTMLInputElement
  const photo = input.files?.[0]
  input.value = ''
  if (!photo) return

  attachedPhoto.value = null
  photoError.value = ''
  if (photo.size > 5 * 1024 * 1024) {
    photoError.value = photoSizeError
  } else if (!photo.size || !/\.(jpe?g|png|webp)$/i.test(photo.name) && !['image/jpeg', 'image/png', 'image/webp'].includes(photo.type)) {
    photoError.value = photoFormatError
  } else {
    attachedPhoto.value = photo
  }
}

const quickPrompts = computed(() => [
  t('Қай санатта артық жұмсап жүрмін?'),
  t('Осы айда шығынды қалай азайтамын?'),
  t('Табысымның 20%-ын қалай жинаймын?'),
])

const sendQuickPrompt = (prompt: string) => {
  inputMessage.value = prompt
  handleSendMessage()
}

const handleSendMessage = async () => {
  const userText = inputMessage.value.trim()
  const photo = attachedPhoto.value
  if ((!userText && !photo) || isThinking.value) return
  if (photo && userText.length > 2000) {
    photoError.value = t('Фото туралы сұрақ 2 000 таңбадан аспауы керек.')
    return
  }
  inputMessage.value = ''
  photoError.value = ''

  chatMessages.value.push({ role: 'user', text: photo ? [`${t('Фото')}: ${photo.name}`, userText].filter(Boolean).join('\n') : userText })
  isThinking.value = true

  try {
    if (photo) {
      const { reply, receipt } = await ai.analyzeImage(photo, userText)
      attachedPhoto.value = null
      chatMessages.value.push({
        role: 'assistant',
        text: reply,
        receipt: receipt ? photo : undefined,
      })
    } else {
      const { reply } = await ai.sendChatMessage(userText)
      chatMessages.value.push({ role: 'assistant', text: reply })
    }
  } catch (error) {
    const status = getErrorStatus(error)
    if (photo) {
      inputMessage.value = userText
      if (status === 413 || status === 415) {
        attachedPhoto.value = null
        photoError.value = status === 413 ? photoSizeError : photoFormatError
      }
    }
    chatMessages.value.push({
      role: 'assistant',
      text: status === 503
        ? t('Gemini жауап беруі үшін сервердегі backend/.env файлына GEMINI_API_KEY орнатыңыз.')
        : t('Gemini жауабын алу мүмкін болмады. Қайталап көріңіз.'),
    })
  } finally {
    isThinking.value = false
    if (photo) {
      await nextTick()
      if (messageStream.value) messageStream.value.scrollTop = messageStream.value.scrollHeight
    }
  }
}

onMounted(() => {
  ai.fetchInsights()
})
</script>
