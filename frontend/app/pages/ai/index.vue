<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">ЖИ Қаржы кеңесшісі</h2>
      <p class="text-sm text-slate-500">Google Gemini негізіндегі жеке бюджет коучы және шығындар аудиті</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Chat Panel -->
      <div class="lg:col-span-8">
        <UCard
          class="flex flex-col h-[620px]"
          :ui="{ body: { base: 'flex-1 flex flex-col p-4 sm:p-5 overflow-hidden' } }"
        >
          <!-- Messages Stream -->
          <div class="flex-1 overflow-y-auto space-y-4 pr-1">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              class="flex gap-3"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                v-if="msg.role === 'assistant'"
                class="w-9 h-9 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center shrink-0 shadow-xs"
              >
                <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
              </div>
              <div
                class="max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line"
                :class="
                  msg.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-br-xs shadow-xs'
                    : 'bg-slate-100 dark:bg-slate-800/90 text-slate-800 dark:text-slate-100 rounded-bl-xs ring-1 ring-slate-200/60 dark:ring-slate-700/60'
                "
              >
                {{ msg.text }}
              </div>
            </div>

            <div v-if="isThinking" class="flex items-center gap-2.5 text-xs text-slate-400 pl-1">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin text-emerald-500" />
              <span>ЖИ шығыстарыңызды талдап жатыр...</span>
            </div>
          </div>

          <!-- Quick Prompt Chips -->
          <div class="pt-3 mt-3 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-2 mb-3">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              type="button"
              class="text-xs font-medium px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-800/80 text-slate-600 dark:text-slate-300 hover:bg-emerald-500/15 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
              @click="sendQuickPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>

          <!-- Input Form -->
          <form class="flex gap-2.5" @submit.prevent="handleSendMessage">
            <UInput
              v-model="inputMessage"
              size="lg"
              class="flex-1"
              placeholder="Үнемдеу немесе бюджет жоспарлау туралы сұрақ қойыңыз..."
              :disabled="isThinking"
            />
            <UButton
              color="emerald"
              size="lg"
              icon="i-heroicons-paper-airplane"
              type="submit"
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
          <h3 class="font-bold text-base text-slate-900 dark:text-white">Жеке инсайттар</h3>
        </div>

        <div
          v-if="ai.insights.value.length === 0"
          class="p-6 text-center rounded-2xl bg-white dark:bg-slate-900/80 ring-1 ring-slate-200/80 dark:ring-slate-800 text-slate-400 text-xs leading-relaxed"
        >
          Жеке қаржылық инсайттар мен ескертулерді алу үшін көбірек операция енгізіңіз немесе чатта сұрақ қойыңыз.
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
const ai = useAiInsights()

const chatMessages = ref([
  {
    role: 'assistant',
    text: 'Сәлеметсіз бе! Мен сіздің SmartBudget жеке қаржы көмекшіңізбін. Кіріс-шығысыңызды талдап, үнемдеу жолдарын ұсына аламын немесе айлық жинақ жоспарын құруға көмектесемін. Қандай сұрағыңыз бар?',
  },
])

const inputMessage = ref('')
const isThinking = ref(false)

const quickPrompts = [
  'Қай санатта артық жұмсап жүрмін?',
  'Осы айда шығынды қалай азайтамын?',
  'Табысымның 20%-ын қалай жинаймын?',
]

const sendQuickPrompt = (prompt: string) => {
  inputMessage.value = prompt
  handleSendMessage()
}

const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isThinking.value) return
  const userText = inputMessage.value.trim()
  inputMessage.value = ''

  chatMessages.value.push({ role: 'user', text: userText })
  isThinking.value = true

  try {
    const res = await ai.sendChatMessage(userText)
    chatMessages.value.push({
      role: 'assistant',
      text: res.reply,
    })
  } catch (error) {
    const status = getErrorStatus(error)
    chatMessages.value.push({
      role: 'assistant',
      text: status === 503
        ? 'Gemini жауап беруі үшін сервердегі backend/.env файлына GEMINI_API_KEY орнатыңыз.'
        : 'Gemini жауабын алу мүмкін болмады. Қайталап көріңіз.',
    })
  } finally {
    isThinking.value = false
  }
}

onMounted(() => {
  ai.fetchInsights()
})
</script>
