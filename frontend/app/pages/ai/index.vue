<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-xl font-bold">ИИ-Советник по бюджету</h2>
      <p class="text-sm text-gray-500">Персональный финансовый коуч на базе Google Gemini</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chat Interface -->
      <div class="lg:col-span-2">
        <UCard class="flex flex-col h-[600px]" :ui="{ body: { base: 'flex-1 flex flex-col p-4 sm:p-4 overflow-hidden' } }">
          <!-- Messages Box -->
          <div class="flex-1 overflow-y-auto space-y-4 pr-2">
            <div
              v-for="(msg, idx) in chatMessages"
              :key="idx"
              class="flex gap-3"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                v-if="msg.role === 'assistant'"
                class="w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center shrink-0 text-sm"
              >
                🤖
              </div>
              <div
                class="max-w-[80%] rounded-2xl px-4 py-3 text-sm"
                :class="
                  msg.role === 'user'
                    ? 'bg-emerald-600 text-white rounded-br-none'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-none'
                "
              >
                {{ msg.text }}
              </div>
            </div>
            <div v-if="isThinking" class="flex items-center gap-2 text-xs text-gray-400">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <span>ИИ анализирует ваши расходы...</span>
            </div>
          </div>

          <!-- Quick Prompts -->
          <div class="pt-3 border-t border-gray-100 dark:border-gray-800 flex flex-wrap gap-2 mb-3">
            <button
              v-for="prompt in quickPrompts"
              :key="prompt"
              class="text-xs px-2.5 py-1 rounded-full border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              @click="sendQuickPrompt(prompt)"
            >
              {{ prompt }}
            </button>
          </div>

          <!-- Input Bar -->
          <form class="flex gap-2" @submit.prevent="handleSendMessage">
            <UInput
              v-model="inputMessage"
              class="flex-1"
              placeholder="Спросите совет по экономии или оптимизации..."
              :disabled="isThinking"
            />
            <UButton
              color="emerald"
              icon="i-heroicons-paper-airplane"
              type="submit"
              :loading="isThinking"
            />
          </form>
        </UCard>
      </div>

      <!-- Insights Sidebar -->
      <div class="space-y-4">
        <h3 class="font-bold text-base flex items-center gap-2">
          <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 text-amber-500" />
          <span>Персональные инсайты</span>
        </h3>

        <div v-if="ai.insights.value.length === 0" class="p-6 text-center border rounded-xl dark:border-gray-800 text-gray-400 text-sm">
          Добавьте больше транзакций, чтобы получить персонализированный аудит трат.
        </div>
        <div v-else class="space-y-3">
          <UCard
            v-for="item in ai.insights.value"
            :key="item.id"
            :ui="{ body: { padding: 'p-4 sm:p-4' } }"
          >
            <div class="flex items-start gap-3">
              <div
                class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-sm"
                :class="{
                  'bg-amber-100 text-amber-600 dark:bg-amber-950': item.type === 'tip',
                  'bg-rose-100 text-rose-600 dark:bg-rose-950': item.type === 'warning',
                  'bg-emerald-100 text-emerald-600 dark:bg-emerald-950': item.type === 'recommendation',
                }"
              >
                <UIcon
                  :name="
                    item.type === 'warning'
                      ? 'i-heroicons-exclamation-triangle'
                      : 'i-heroicons-sparkles'
                  "
                  class="w-4 h-4"
                />
              </div>
              <div class="flex-1 text-xs">
                <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-1">{{ item.title }}</h4>
                <p class="text-gray-600 dark:text-gray-400 leading-relaxed">{{ item.content }}</p>
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
    text: 'Привет! Я ваш личный финансовый ИИ-ассистент SmartBudget. Я могу проанализировать ваши последние траты, подсказать скрытые резервы для экономии или помочь составить реалистичный план накоплений. О чем хотите узнать?',
  },
])

const inputMessage = ref('')
const isThinking = ref(false)

const quickPrompts = [
  'Где я переплачиваю больше всего?',
  'Как сократить расходы в этом месяце?',
  'Оцени мой бюджет на кафе и рестораны',
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
        ? 'Для ответа Gemini задайте GEMINI_API_KEY в backend/.env.'
        : 'Не удалось получить ответ Gemini. Попробуйте ещё раз.',
    })
  } finally {
    isThinking.value = false
  }
}

onMounted(() => {
  ai.fetchInsights()
})
</script>
