<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h2 class="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">Жеңілдіктер мен баға талдауы</h2>
        <p class="text-sm text-slate-500">Сатып алар алдында бағаның тиімділігін ЖИ арқылы тексеріңіз</p>
      </div>
      <UButton
        icon="i-heroicons-arrow-path"
        color="gray"
        variant="soft"
        size="sm"
        label="Жаңарту"
        :loading="deals.loading.value"
        @click="deals.fetchDeals()"
      />
    </div>

    <!-- AI Price Check Card -->
    <div class="rounded-3xl p-6 sm:p-7 bg-gradient-to-br from-emerald-500/12 via-teal-500/6 to-transparent ring-1 ring-emerald-500/25 space-y-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-2xl bg-emerald-500 text-white flex items-center justify-center shadow-sm">
          <UIcon name="i-heroicons-magnifying-glass-circle" class="w-6 h-6" />
        </div>
        <div>
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white">ЖИ арқылы бағаны тексеру</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400">
            Тауар атауы мен бағасын жазыңыз — Gemini оның нарыққа сай екенін бағалайды
          </p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-3">
        <UInput
          v-model="productToCheck"
          size="lg"
          class="flex-1"
          placeholder="Мысалы: Sony WH-1000XM5 құлаққабы немесе Lavazza кофесі 1 кг"
        />
        <UInput
          v-model="priceToCheck"
          type="number"
          size="lg"
          step="0.01"
          min="0.01"
          class="w-full sm:w-48"
          :placeholder="`Бағасы (${currency})`"
        />
        <UButton
          color="emerald"
          size="lg"
          icon="i-heroicons-sparkles"
          label="Тексеру"
          :loading="isAnalyzing"
          @click="handleCheckPrice"
        />
      </div>

      <div
        v-if="analysisError"
        role="alert"
        class="flex items-center gap-2 text-xs font-medium text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/40 ring-1 ring-amber-200 dark:ring-amber-900/70 rounded-xl px-3.5 py-2.5"
      >
        <UIcon name="i-heroicons-information-circle" class="w-4 h-4 shrink-0" />
        <span>{{ analysisError }}</span>
      </div>

      <div
        v-if="analysisResult"
        class="p-5 rounded-2xl bg-white dark:bg-slate-900 ring-1 ring-slate-200/80 dark:ring-slate-800 space-y-2"
      >
        <div
          class="inline-flex items-center gap-2 text-xs font-bold px-3 py-1 rounded-full"
          :class="
            analysisResult.verdict === 'overpriced'
              ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400'
              : 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400'
          "
        >
          <UIcon
            :name="analysisResult.verdict === 'overpriced' ? 'i-heroicons-exclamation-triangle' : 'i-heroicons-check-circle'"
            class="w-4 h-4"
          />
          <span>{{ verdictTitle(analysisResult.verdict) }}</span>
        </div>
        <p class="text-sm text-slate-700 dark:text-slate-200 leading-relaxed">{{ analysisResult.explanation }}</p>
        <p v-if="analysisResult.estimated_fair_price != null" class="text-xs text-slate-500 tabular-nums">
          Болжамды әділ нарықтық баға: <strong>{{ formatCurrency(analysisResult.estimated_fair_price) }}</strong>
        </p>
      </div>
    </div>

    <!-- Active Deals Grid -->
    <div class="space-y-4">
      <h3 class="text-base font-bold text-slate-900 dark:text-white">Белсенді науқандар мен жеңілдіктер</h3>

      <div
        v-if="deals.deals.value.length === 0"
        class="p-12 text-center rounded-3xl bg-white dark:bg-slate-900/80 ring-1 ring-slate-200/80 dark:ring-slate-800"
      >
        <div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mx-auto mb-3">
          <UIcon name="i-heroicons-tag" class="w-6 h-6" />
        </div>
        <p class="text-sm font-semibold text-slate-700 dark:text-slate-200">Қазірше белсенді жеңілдіктер тізімі бос</p>
        <p class="text-xs text-slate-500 mt-1 max-w-md mx-auto">
          Науқандар фондық сканер арқылы жаңартылады. Жоғарыдағы ЖИ виджеті арқылы кез келген тауар бағасын қазір тексере аласыз.
        </p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <UCard
          v-for="item in deals.deals.value"
          :key="item.id"
          class="flex flex-col justify-between"
        >
          <div class="space-y-2.5">
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                {{ item.store }}
              </span>
              <UBadge color="rose" variant="solid" size="xs">
                -{{ item.discount_percent }}%
              </UBadge>
            </div>
            <h4 class="font-bold text-sm text-slate-900 dark:text-white">{{ item.title }}</h4>
            <p v-if="item.description" class="text-xs text-slate-500 line-clamp-2">
              {{ item.description }}
            </p>
          </div>

          <div class="pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div class="tabular-nums">
              <p class="text-xs line-through text-slate-400">{{ formatCurrency(item.original_price) }}</p>
              <p class="text-base font-extrabold text-emerald-600 dark:text-emerald-400">{{ formatCurrency(item.discount_price) }}</p>
            </div>
            <UButton
              v-if="item.url"
              :to="item.url"
              target="_blank"
              color="emerald"
              variant="soft"
              size="xs"
              label="Өту"
              trailing-icon="i-heroicons-arrow-top-right-on-square"
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
  if (verdict === 'good_deal') return 'Тиімді баға!'
  if (verdict === 'overpriced') return 'Нарықтан қымбаттау'
  return 'Қалыпты нарықтық баға'
}

const handleCheckPrice = async () => {
  analysisError.value = ''
  analysisResult.value = null
  if (!productToCheck.value.trim()) {
    analysisError.value = 'Тексеру үшін тауар атауын енгізіңіз'
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
      ? 'Бағаны ЖИ арқылы тексеру үшін backend/.env файлына жарамды GEMINI_API_KEY орнатыңыз.'
      : formatApiError(err, 'Gemini-ден баға талдауын алу мүмкін болмады.')
  } finally {
    isAnalyzing.value = false
  }
}

onMounted(() => {
  deals.fetchDeals()
})
</script>
