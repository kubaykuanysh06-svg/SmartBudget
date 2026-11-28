<template>
  <UCard>
    <template #header>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <h3 class="sb-section-title">{{ tr('Чектер аналитикасы', 'Аналитика чеков', 'Receipt analytics') }}</h3>
        <USelect v-model="period" :options="periods" :aria-label="tr('Кезең', 'Период', 'Period')" />
      </div>
    </template>
    <form v-if="period === 'custom'" class="mb-4 flex flex-wrap items-end gap-3" @submit.prevent="applyDates">
      <label class="text-sm">{{ tr('Басталу күні', 'Дата начала', 'Start date') }}<UInput v-model="draftFrom" type="date" required /></label>
      <label class="text-sm">{{ tr('Аяқталу күні', 'Дата окончания', 'End date') }}<UInput v-model="draftTo" type="date" required /></label>
      <UButton type="submit">{{ tr('Көрсету', 'Показать', 'Apply') }}</UButton>
    </form>
    <p v-if="invalid" role="alert" class="mb-3 text-sm text-rose-600">{{ tr('1–366 күндік кезеңді таңдаңыз.', 'Выберите период от 1 до 366 дней.', 'Choose a period of 1 to 366 days.') }}</p>
    <p v-if="loading" role="status" class="text-sm sb-muted">{{ tr('Есеп жүктелуде…', 'Загрузка отчёта…', 'Loading report…') }}</p>
    <p v-else-if="failed" role="alert" class="text-sm text-rose-600">{{ tr('Есеп жүктелмеді.', 'Не удалось загрузить отчёт.', 'Could not load the report.') }}</p>
    <div v-else-if="report" class="space-y-6">
      <div class="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-5">
        <div v-for="stat in stats" :key="stat.label" class="rounded-xl bg-[var(--sb-soft)] p-3">
          <p class="text-xs sb-muted">{{ stat.label }}</p><p class="mt-1 text-lg font-bold tabular-nums">{{ stat.value }}</p>
        </div>
      </div>
      <div class="space-y-2 text-sm">
        <p>{{ tr('Алдыңғы тең кезең', 'Предыдущий равный период', 'Previous equal period') }} · {{ report.previous_from }} — {{ report.previous_to }} · {{ money(report.totals.previous) }}</p>
        <p class="font-semibold">{{ tr('Шығынның өзгерісі', 'Изменение расходов', 'Spending change') }} {{ signed(report.totals.difference) }} <span v-if="report.totals.percent !== null">({{ decimal(report.totals.percent) }}%)</span></p>
        <p v-if="report.top_category_growth">{{ tr('Өсімге ең көп әсер еткен санат', 'Наибольший рост по категории', 'Largest category increase') }} · {{ label(report.top_category_growth, 'category') }} · {{ signed(report.top_category_growth.difference) }}</p>
        <p v-if="report.top_product_growth">{{ tr('Өсімге ең көп әсер еткен тауар', 'Наибольший рост по товару', 'Largest product increase') }} · {{ report.top_product_growth.name }} · {{ signed(report.top_product_growth.difference) }}</p>
      </div>
      <div>
        <div class="mb-3 flex flex-wrap gap-2">
          <UButton v-for="option in groups" :key="option.key" :variant="group === option.key ? 'solid' : 'soft'" :aria-pressed="group === option.key" size="sm" @click="group = option.key; limit = 12">{{ option.label }}</UButton>
        </div>
        <p v-if="!rows.length" class="text-sm sb-muted">{{ tr('Бұл кезеңдерде дерек жоқ.', 'За эти периоды данных нет.', 'No data for these periods.') }}</p>
        <ul class="space-y-2">
          <li v-for="row in rows.slice(0, limit)" :key="row.key">
            <button type="button" class="w-full rounded-xl border border-[var(--sb-line)] p-3 text-left text-sm hover:bg-[var(--sb-soft)] focus-visible:outline-primary-500" @click="openLines(row)">
              <span class="flex flex-wrap justify-between gap-x-4">
                <strong class="break-all">{{ label(row, group) }}</strong>
                <span class="tabular-nums">{{ money(row.current) }} · {{ decimal(row.share) }}% <span class="sb-muted">({{ signed(row.difference) }}<template v-if="row.percent !== null"> · {{ decimal(row.percent) }}%</template>)</span></span>
              </span>
              <span class="mt-2 block h-1.5 rounded-full bg-[var(--sb-soft)]"><span class="block h-full rounded-full bg-primary-500" :style="{ width: row.share + '%' }" /></span>
              <span v-if="row.movement" class="mt-2 block text-xs sb-muted">
                {{ tr('Бірлік құнының әсері', 'Вклад цены за единицу', 'Unit price effect') }} {{ signed(row.movement.price_effect) }} ·
                {{ tr('Мөлшердің әсері', 'Вклад количества', 'Quantity effect') }} {{ signed(row.movement.quantity_effect) }}
                ({{ decimal(row.movement.previous_quantity) }} → {{ decimal(row.movement.current_quantity) }} {{ unitLabel(row.movement.unit) }};
                {{ money(row.movement.previous_unit_cost) }} → {{ money(row.movement.current_unit_cost) }} / {{ unitLabel(row.movement.unit) }})
              </span>
            </button>
          </li>
        </ul>
        <UButton v-if="rows.length > limit" class="mt-3" variant="soft" size="sm" @click="limit += 12">{{ tr('Тағы көрсету', 'Показать ещё', 'Show more') }}</UButton>
      </div>
      <div>
        <h4 class="mb-2 text-sm font-bold">{{ tr('Кезең бюджеттері', 'Бюджеты за период', 'Budgets for the period') }}</h4>
        <p v-if="!report.budgets.length" class="text-sm sb-muted">{{ tr('Кезеңге сәйкес бюджет жоқ.', 'На этот период нет бюджета.', 'No budget for this period.') }}</p>
        <ul class="space-y-1 text-sm">
          <li v-for="(budget, index) in report.budgets" :key="index" class="flex flex-wrap justify-between gap-x-4">
            <span>{{ budget.category_name ? t(translateCategoryName(budget.category_name)) : tr('Жалпы бюджет', 'Общий бюджет', 'Overall budget') }} · {{ budget.date_from }} — {{ budget.date_to }}</span>
            <span :class="Number(budget.remaining) < 0 ? 'text-rose-600 dark:text-rose-400' : ''">
              {{ Number(budget.remaining) < 0 ? tr('Лимиттен асты', 'Превышение', 'Over budget') : tr('Қалды', 'Осталось', 'Remaining') }} {{ money(Math.abs(Number(budget.remaining))) }} / {{ money(budget.limit) }}
            </span>
          </li>
        </ul>
      </div>
      <div>
        <h4 class="text-sm font-bold">{{ tr('Жиі алынатын тауарлардың баға тарихы', 'История цен часто покупаемых товаров', 'Price history for frequent purchases') }}</h4>
        <p v-if="!report.history.length" class="mt-2 text-sm sb-muted">{{ tr('Тарих үшін бір тауар кемінде екі чекте болуы керек.', 'Для истории нужны хотя бы два чека с одним товаром.', 'Price history needs at least two receipts for the same product.') }}</p>
        <details v-for="product in report.history" :key="product.key" class="mt-2 rounded-lg bg-[var(--sb-soft)] p-3 text-sm">
          <summary class="cursor-pointer font-medium">{{ product.name }}</summary>
          <ul class="mt-2 space-y-2">
            <li v-for="(price, index) in product.observations" :key="index" class="flex flex-wrap justify-between gap-x-4">
              <NuxtLink :to="receiptLink(price.transaction_id)" class="text-primary-600 underline dark:text-primary-400">{{ price.day }} · {{ price.store }}</NuxtLink>
              <span>{{ money(price.package_price) }} <span v-if="price.unit_price !== null">· {{ money(price.unit_price) }} / {{ unitLabel(price.unit) }}</span></span>
            </li>
          </ul>
        </details>
      </div>
    </div>
    <UModal v-model="detailOpen" :ui="{ width: 'w-full sm:max-w-2xl' }">
      <div class="space-y-3 p-5">
        <div class="flex items-start justify-between gap-4">
          <h3 class="sb-section-title">{{ detailTitle }}</h3>
          <UButton color="gray" variant="ghost" icon="i-heroicons-x-mark" :aria-label="tr('Жабу', 'Закрыть', 'Close')" @click="detailOpen = false" />
        </div>
        <p v-if="detailError" role="alert" class="text-sm text-rose-600">{{ tr('Тауар жолдары жүктелмеді.', 'Не удалось загрузить строки чеков.', 'Could not load receipt lines.') }}</p>
        <p v-else-if="!detailRows.length && !detailLoading" class="text-sm sb-muted">{{ tr('Таңдалған кезеңде чек жоқ.', 'В выбранном периоде чеков нет.', 'No receipts in the selected period.') }}</p>
        <ul class="max-h-[60vh] divide-y divide-[var(--sb-line)] overflow-auto">
          <li v-for="line in detailRows" :key="line.transaction_id + '-' + line.line_index" class="py-2 text-sm">
            <div class="flex flex-wrap justify-between gap-2"><strong>{{ line.product.name }}</strong><span>{{ money(line.spend) }}</span></div>
            <NuxtLink :to="receiptLink(line.transaction_id)" class="text-primary-600 underline dark:text-primary-400">{{ line.day }} · {{ [line.merchant, line.branch, line.address].filter(Boolean).join(' · ') }}</NuxtLink>
            <span class="sb-muted"> · {{ decimal(line.quantity) }} {{ unitLabel(line.quantity_unit) }}</span>
          </li>
        </ul>
        <UButton v-if="detailLoading || detailRows.length < detailTotal" :loading="detailLoading" size="sm" variant="soft" @click="loadLines">{{ tr('Тағы көрсету', 'Показать ещё', 'Show more') }}</UButton>
      </div>
    </UModal>
  </UCard>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'
import type { ReceiptReport } from '~~/shared/types'

type Group = 'category' | 'store' | 'product'
type Change = { current: string; previous: string; difference: string; percent: string | null }
type Movement = {
  unit: string; current_quantity: string; previous_quantity: string; price_effect: string; quantity_effect: string
  current_unit_cost: string; previous_unit_cost: string
}
type Row = Change & { key: string; name: string | null; share: string; movement: Movement | null }
type History = { key: string; name: string; observations: { day: string; store: string; transaction_id: string; unit: string; unit_price: string | null; package_price: string | null }[] }
type Report = {
  totals: Change; average_receipt: string; purchase_count: number; discount_total: string; previous_from: string; previous_to: string
  categories: Row[]; stores: Row[]; products: Row[]; top_category_growth: Row | null; top_product_growth: Row | null
  history: History[]; budgets: ReceiptReport['budgets']
}
type Line = {
  transaction_id: string; line_index: number; merchant: string; branch: string; address: string; day: string
  quantity: string; quantity_unit: string; spend: string; product: { name: string }
}

const props = defineProps<{ month?: string }>()
const api = useApi()
const { t, tr, money, decimal } = useLanguage()
const revision = useState('receipt-revision', () => 0)
const report = ref<Report | null>(null)
const loading = ref(true)
const failed = ref(false)
const invalid = ref(false)
const period = ref('month')
const group = ref<Group>('category')
const limit = ref(12)
const draftFrom = ref(dayjs().startOf('month').format('YYYY-MM-DD'))
const draftTo = ref(dayjs().format('YYYY-MM-DD'))
const customRange = ref({ date_from: draftFrom.value, date_to: draftTo.value })
const range = computed(() => {
  if (period.value === 'custom') return customRange.value
  const now = props.month && period.value === 'month' ? dayjs(props.month + '-01') : dayjs()
  const start = period.value === 'week' ? now.subtract(6, 'day') : now.startOf('month')
  return { date_from: start.format('YYYY-MM-DD'), date_to: (props.month && period.value === 'month' ? now.endOf('month') : now).format('YYYY-MM-DD') }
})
const periods = computed(() => [
  { value: 'week', label: tr('Соңғы 7 күн', 'Последние 7 дней', 'Last 7 days') },
  { value: 'month', label: props.month || tr('Осы ай', 'Этот месяц', 'This month') },
  { value: 'custom', label: tr('Еркін кезең', 'Свой период', 'Custom range') },
])
const groups = computed<{ key: Group; label: string }[]>(() => [
  { key: 'category', label: tr('Санаттар', 'Категории', 'Categories') },
  { key: 'store', label: tr('Дүкендер мен филиалдар', 'Магазины и филиалы', 'Stores and branches') },
  { key: 'product', label: tr('Тауарлар', 'Товары', 'Products') },
])
const rows = computed(() => (group.value === 'category' ? report.value?.categories : group.value === 'store' ? report.value?.stores : report.value?.products) || [])
const stats = computed(() => [
  { label: tr('Жалпы шығын', 'Общие расходы', 'Total spending'), value: money(report.value?.totals.current) },
  { label: tr('Орташа чек', 'Средний чек', 'Average receipt'), value: money(report.value?.average_receipt) },
  { label: tr('Сатып алу саны', 'Количество покупок', 'Purchase count'), value: decimal(report.value?.purchase_count || 0) },
  { label: tr('Алынған жеңілдік', 'Полученные скидки', 'Discounts received'), value: money(report.value?.discount_total) },
  { label: tr('Бюджет қалдығы', 'Остаток бюджета', 'Budget remaining'), value: budgetRemaining.value },
])
// Prefer the overall budget; otherwise add up the category budgets for the period.
const budgetRemaining = computed(() => {
  const budgets = report.value?.budgets || []
  if (!budgets.length) return tr('Бюджет жоқ', 'Нет бюджета', 'No budget')
  const overall = budgets.filter(budget => !budget.category_name)
  const rows = overall.length ? overall : budgets
  return money(rows.reduce((sum, budget) => sum + Number(budget.remaining), 0))
})
const signed = (value: string) => (Number(value) > 0 ? '+' : '') + money(value)
function unitLabel(unit: string) {
  return ({ l: tr('л', 'л', 'L'), kg: tr('кг', 'кг', 'kg'), pc: tr('дана', 'шт.', 'item') } as Record<string, string>)[unit] || unit
}
const label = (row: Row, kind: Group) => kind === 'category'
  ? t(translateCategoryName(row.name, 'Санатсыз'))
  : row.name || tr('Белгісіз', 'Неизвестно', 'Unknown')
const receiptLink = (id: string) => ({ path: '/transactions', query: { receipt: id } })

function applyDates() {
  const days = dayjs(draftTo.value).diff(dayjs(draftFrom.value), 'day') + 1
  invalid.value = !Number.isFinite(days) || days < 1 || days > 366
  if (!invalid.value) customRange.value = { date_from: draftFrom.value, date_to: draftTo.value }
}

let version = 0
async function load() {
  const request = ++version
  loading.value = true
  failed.value = false
  detailOpen.value = false
  try {
    const data = await api.fetch<Report>('/analytics/receipt-details', { query: range.value })
    if (request === version) report.value = data
  } catch {
    if (request === version) failed.value = true
  } finally {
    if (request === version) loading.value = false
  }
}

const detailOpen = ref(false)
const detailTitle = ref('')
const detailRows = ref<Line[]>([])
const detailTotal = ref(0)
const detailLoading = ref(false)
const detailError = ref(false)
let detailVersion = 0
let filter: { group: Group; key: string }
function openLines(row: Row) {
  filter = { group: group.value, key: row.key }
  detailVersion++
  detailTitle.value = label(row, group.value)
  detailRows.value = []
  detailTotal.value = 0
  detailOpen.value = true
  void loadLines()
}
async function loadLines() {
  const request = detailVersion
  detailLoading.value = true
  detailError.value = false
  try {
    const data = await api.fetch<{ total: number; rows: Line[] }>('/analytics/receipt-lines', { query: { ...range.value, ...filter, offset: detailRows.value.length } })
    if (request !== detailVersion) return
    detailRows.value.push(...data.rows)
    detailTotal.value = data.total
  } catch {
    if (request === detailVersion) detailError.value = true
  } finally {
    if (request === detailVersion) detailLoading.value = false
  }
}
watch([range, revision], load)
onMounted(() => {
  void load()
  window.addEventListener('focus', load)
})
onBeforeUnmount(() => window.removeEventListener('focus', load))
</script>
