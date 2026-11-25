<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold">Скидки и выгодные траты</h2>
        <p class="text-sm text-gray-500">Специальные предложения и умный мониторинг цен</p>
      </div>
      <UButton
        icon="i-heroicons-arrow-path"
        color="gray"
        variant="ghost"
        label="Обновить"
        @click="deals.fetchDeals()"
      />
    </div>

    <!-- AI Price Check Widget -->
    <UCard class="bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-transparent border-emerald-200 dark:border-emerald-900">
      <div class="space-y-3">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-magnifying-glass-circle" class="w-6 h-6 text-emerald-600" />
          <h3 class="font-bold text-base">ИИ-проверка цены перед покупкой</h3>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Введите название товара и стоимость, а наш ИИ проанализирует, насколько выгодна эта цена:
        </p>
        <div class="flex flex-col sm:flex-row gap-3">
          <UInput
            v-model="productToCheck"
            class="flex-1"
            placeholder="Например: Наушники Sony WH-1000XM5 или Кофе Lavazza 1 кг"
          />
          <UInput
            v-model="priceToCheck"
            type="number"
            step="0.01"
            min="0.01"
            class="w-full sm:w-44"
            :placeholder="`Цена (${currency})`"
          />
          <UButton
            color="emerald"
            label="Проверить"
            :loading="isAnalyzing"
            @click="handleCheckPrice"
          />
        </div>

        <div
          v-if="analysisError"
          role="alert"
          class="text-xs text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900 rounded-lg px-3 py-2"
        >
          {{ analysisError }}
        </div>

        <div v-if="analysisResult" class="mt-4 p-4 rounded-xl bg-white dark:bg-gray-800 border border-emerald-100 dark:border-emerald-950">
          <div
            class="flex items-center gap-2 font-semibold"
            :class="analysisResult.verdict === 'overpriced' ? 'text-amber-600' : 'text-green-600'"
          >
            <UIcon
              :name="analysisResult.verdict === 'overpriced' ? 'i-heroicons-exclamation-triangle' : 'i-heroicons-check-circle'"
              class="w-5 h-5"
            />
            <span>{{ verdictTitle(analysisResult.verdict) }}</span>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-300 mt-1">{{ analysisResult.explanation }}</p>
          <p v-if="analysisResult.estimated_fair_price != null" class="text-xs text-gray-500 mt-2">
            Ориентировочная справедливая цена: {{ formatCurrency(analysisResult.estimated_fair_price) }}
          </p>
        </div>
      </div>
    </UCard>

    <!-- Deals Grid -->
    <div>
      <h3 class="text-lg font-bold mb-4">Актуальные скидки и промо-акции</h3>
      <div v-if="deals.deals.value.length === 0" class="p-12 text-center border border-dashed rounded-2xl dark:border-gray-800">
        <UIcon name="i-heroicons-tag" class="w-12 h-12 mx-auto mb-2 text-gray-400" />
        <p class="text-sm text-gray-500">Скидки обновляются фоновым сканером. Нажмите «Обновить» или добавьте операции, чтобы получить персональные предложения.</p>
      </div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard
          v-for="item in deals.deals.value"
          :key="item.id"
          class="flex flex-col justify-between"
        >
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                {{ item.store }}
              </span>
              <UBadge color="rose" variant="solid" size="xs">
                -{{ item.discount_percent }}%
              </UBadge>
            </div>
            <h4 class="font-bold text-sm">{{ item.title }}</h4>
            <p v-if="item.description" class="text-xs text-gray-500 line-clamp-2">
              {{ item.description }}
            </p>
          </div>

          <div class="pt-4 mt-3 border-t border-gray-100 dark:border-gray-800 flex items-center justify-between">
            <div>
              <p class="text-xs line-through text-gray-400">{{ formatCurrency(item.original_price) }}</p>
              <p class="text-base font-bold text-emerald-600">{{ formatCurrency(item.discount_price) }}</p>
            </div>
            <UButton
              v-if="item.url"
              :to="item.url"
              target="_blank"
              color="emerald"
              variant="soft"
              size="xs"
              label="Купить со скидкой"
            />
          </div>
        </UCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PriceAnalysis } from '~~/shared/types'

const deals = useDeals()
const ai = useAiInsights()

const productToCheck = ref('')
const priceToCheck = ref<string | number>('')
const isAnalyzing = ref(false)
const analysisError = ref('')
const analysisResult = ref<PriceAnalysis | null>(null)

const { currency, formatCurrency } = useCurrencyFormat()

const verdictTitle = (verdict: PriceAnalysis['verdict']) => {
  if (verdict === 'good_deal') return 'Выгодная цена!'
  if (verdict === 'overpriced') return 'Цена выше рыночной'
  return 'Рыночная цена'
}

const handleCheckPrice = async () => {
  analysisError.value = ''
  analysisResult.value = null
  if (!productToCheck.value.trim()) {
    analysisError.value = 'Введите название товара для проверки'
    return
  }
  const moneyErr = validateMoneyInput(priceToCheck.value)
  if (moneyErr) {
    analysisError.value = moneyErr
    return
  }

  isAnalyzing.value = true
  try {
    analysisResult.value = await ai.analyzePrice({
      description: productToCheck.value.trim(),
      amount: Number(String(priceToCheck.value).replace(',', '.')),
    })
  } catch (err: any) {
    const status = getErrorStatus(err)
    analysisError.value = status === 503
      ? 'Для ИИ-проверки цены задайте действительный GEMINI_API_KEY в backend/.env.'
      : formatApiError(err, 'Не удалось получить оценку цены от Gemini.')
  } finally {
    isAnalyzing.value = false
  }
}

onMounted(() => {
  deals.fetchDeals()
})
</script>
