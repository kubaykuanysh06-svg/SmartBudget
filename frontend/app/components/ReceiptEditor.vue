<template>
  <UModal :model-value="true" :prevent-close="busy" :ui="{ width: 'w-full sm:max-w-6xl' }" @update:model-value="close">
    <div class="space-y-4 p-4 sm:p-6">
      <div class="flex items-start justify-between gap-4">
        <h3 class="sb-section-title">{{ title }}</h3>
        <UButton type="button" color="gray" variant="ghost" icon="i-heroicons-x-mark" :aria-label="t('Жабу')" :disabled="busy" @click="close(false)" />
      </div>

      <p v-if="notice" role="status" class="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200">{{ notice }}</p>
      <p v-if="readOnly && current" class="text-sm text-slate-600 dark:text-slate-300">
        {{ tr(`Шығыс чек күнімен есептеледі (${current.transaction_date}).`, `Расход учитывается по дате чека (${current.transaction_date}).`, `The expense is counted on the receipt date (${current.transaction_date}).`) }}
        <NuxtLink :to="{ path: '/analytics', query: { month: current.transaction_date.slice(0, 7) } }" class="font-medium text-emerald-700 underline dark:text-emerald-300">{{ t('Сол айдың аналитикасын ашу') }}</NuxtLink>
      </p>
      <p v-if="error" role="alert" class="rounded-lg bg-rose-50 p-3 text-sm text-rose-800 dark:bg-rose-900/30 dark:text-rose-200">{{ error }}</p>

      <div v-if="!draftReady" class="space-y-3">
        <label for="receipt-file" class="block text-sm font-medium">{{ t('Чек файлы') }}</label>
        <input
          id="receipt-file"
          type="file"
          accept="image/jpeg,image/png,image/webp,application/pdf,.jpg,.jpeg,.png,.webp,.pdf"
          class="block w-full text-sm"
          :disabled="busy"
          @change="upload"
        >
        <p class="text-sm text-slate-500" aria-live="polite">{{ busy ? t('Чек оқылып жатыр…') : t('JPEG, PNG, WebP немесе PDF. Ең көбі 10 МБ.') }}</p>
      </div>

      <form v-else class="space-y-4" @submit.prevent="save">
        <p v-if="!readOnly && hasUncertainty" class="text-sm text-amber-700 dark:text-amber-300">{{ t('Сары түспен белгіленген өрістерді чекпен салыстырып тексеріңіз.') }}</p>
        <label v-if="!readOnly && sourceCurrency !== 'KZT'" class="flex items-start gap-2 text-sm text-amber-700 dark:text-amber-300">
          <input v-model="confirmKzt" type="checkbox" class="mt-1" :disabled="busy">
          <span>{{ sourceCurrency ? tr(`Чекте ${sourceCurrency} валютасы оқылды.`, `В чеке распознана валюта ${sourceCurrency}.`, `The receipt currency was read as ${sourceCurrency}.`) : t('Чек валютасы оқылмады.') }} {{ tr('Барлық енгізілген соманың теңгемен берілгенін растаймын.', 'Подтверждаю, что все введённые суммы указаны в тенге.', 'I confirm that all entered amounts are in tenge.') }}</span>
        </label>
        <fieldset :disabled="readOnly || busy" class="space-y-4">
          <div class="grid gap-3 sm:grid-cols-3">
            <label v-for="field in headerFields" :key="field.key" class="block text-sm font-medium">
              {{ t(field.label) }}
              <input
                v-model="form[field.key]"
                :type="field.key === 'purchase_date' ? 'date' : 'text'"
                class="receipt-input mt-1"
                :class="mark(headerUncertain, field.key)"
                @input="clearHeader(field.key)"
              >
            </label>
          </div>

          <div class="overflow-x-auto rounded-lg ring-1 ring-slate-200 dark:ring-slate-700">
            <table class="w-full min-w-[900px] text-left text-sm">
              <thead class="bg-slate-50 dark:bg-slate-800">
                <tr>
                  <th v-for="field in lineFields" :key="field.key" scope="col" class="p-2 font-semibold">{{ t(field.label) }}</th>
                  <th scope="col" class="p-2 font-semibold">{{ t('Жол сомасында жеңілдік') }}</th>
                  <th scope="col" class="p-2 font-semibold">{{ t('Санат') }}</th>
                  <th v-if="readOnly" scope="col" class="p-2 font-semibold">{{ t('Санатқа есептелді') }}</th>
                  <th v-else scope="col" class="p-2"><span class="sr-only">{{ t('Әрекет') }}</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                <template v-for="(item, index) in items" :key="item.key">
                <tr>
                  <td v-for="field in lineFields" :key="field.key" class="p-2">
                    <input
                      v-model="item[field.key]"
                      type="text"
                      :inputmode="field.numeric ? 'decimal' : 'text'"
                      :aria-label="rowLabel(index, t(field.label))"
                      class="receipt-input"
                      :class="[mark(item.uncertain, field.key), field.key === 'name' ? 'min-w-[9rem]' : 'min-w-[4rem]']"
                      @input="clearLine(item, field.key)"
                    >
                  </td>
                  <td class="p-2">
                    <select v-model="item.discount_mode" :aria-label="rowLabel(index, tr('жеңілдік күйі', 'статус скидки', 'discount status'))" class="receipt-input min-w-[8rem]" :class="mark(item.uncertain, 'line_total_is_net')" @change="clearLine(item, 'line_total_is_net')">
                      <option value="">{{ t('Белгісіз / жоқ') }}</option>
                      <option value="net">{{ t('Есептелген') }}</option>
                      <option value="gross">{{ t('Әлі шегерілмеген') }}</option>
                    </select>
                  </td>
                  <td class="p-2">
                    <select v-model="item.category_id" :aria-label="rowLabel(index, tr('санат', 'категория', 'category'))" class="receipt-input min-w-[8rem]" :class="mark(item.uncertain, 'category_id')" @change="clearLine(item, 'category_id')">
                      <option value="">{{ t('Санатсыз') }}</option>
                      <option v-for="category in categories" :key="category.id" :value="category.id">{{ categoryLabel(category.name) }}</option>
                    </select>
                  </td>
                  <td v-if="readOnly" class="p-2 whitespace-nowrap tabular-nums">{{ money(item.allocated_amount) }}</td>
                  <td v-else class="p-2">
                    <UButton color="gray" variant="ghost" size="xs" icon="i-heroicons-x-mark" type="button" :aria-label="tr(`${index + 1}-жолды алып тастау`, `Удалить строку ${index + 1}`, `Remove line ${index + 1}`)" @click="items.splice(index, 1)" />
                  </td>
                </tr>
                <tr>
                  <td :colspan="lineFields.length + 3" class="p-2">
                    <details class="text-xs">
                      <summary class="cursor-pointer text-primary-600 dark:text-primary-400" :class="mark(item.uncertain, 'product_details')">{{ tr('Тауар сипаттары', 'Характеристики товара', 'Product details') }}</summary>
                      <div class="mt-2 grid gap-2 sm:grid-cols-4">
                        <label v-for="field in detailFields" :key="field.key">
                          {{ t(field.label) }}
                          <input v-model="item[field.key]" type="text" :inputmode="field.mode" class="receipt-input mt-1" :class="mark(item.uncertain, field.key)" @input="clearLine(item, field.key)">
                        </label>
                      </div>
                    </details>
                    <NuxtLink v-if="readOnly" :to="comparisonLink(item)" class="mt-1 inline-block text-xs font-medium text-primary-600 underline dark:text-primary-400" @click="close(false)">{{ tr('Бағаны салыстыру', 'Сравнить цены', 'Compare prices') }}</NuxtLink>
                  </td>
                </tr>
                </template>
              </tbody>
            </table>
          </div>
          <UButton v-if="!readOnly" type="button" size="sm" color="gray" variant="outline" icon="i-heroicons-plus" :label="t('Тауар қосу')" @click="items.push(editableLine())" />

          <div class="grid gap-3 sm:grid-cols-3">
            <label v-for="field in amountFields" :key="field.key" class="block text-sm font-medium">
              {{ t(field.label) }}
              <input v-model="form[field.key]" type="text" inputmode="decimal" class="receipt-input mt-1" :class="mark(headerUncertain, field.key)" @input="clearHeader(field.key)">
              <span v-if="field.key === 'fees' && !readOnly" class="mt-1 block text-xs font-normal text-slate-500">
                {{ t('Чек сомасына үстінен қосылған қызмет, жеткізу ақысы немесе комиссия. Бағаға кірген ҚҚС бұл өріске жазылмайды. Бөлек ақы болмаса, 0 енгізіңіз.') }}
              </span>
            </label>
          </div>
        </fieldset>

        <div v-if="totals" class="grid gap-3 rounded-xl bg-[var(--sb-soft)] p-3 text-sm tabular-nums sm:grid-cols-3">
          <p>{{ t('Тауарлар') }} <strong>{{ money(totals.subtotal) }}</strong></p>
          <p>{{ t('Жеңілдіктер') }} <strong>{{ money(Number(totals.item_discounts) + Number(totals.order_discount)) }}</strong></p>
          <p>{{ t('Қосымша төлемдер') }} <strong>{{ money(totals.fees) }}</strong></p>
          <p>{{ t('Есептелген сома') }} <strong>{{ money(totals.calculated) }}</strong></p>
          <p>{{ t('Төленді') }} <strong>{{ money(totals.paid) }}</strong></p>
          <p v-if="totals.difference !== null" :class="hasDifference ? 'text-amber-700 dark:text-amber-300' : ''">
            {{ t('Айырма') }} <strong>{{ money(Math.abs(Number(totals.difference))) }}</strong>
            <span v-if="hasDifference">&nbsp;{{ Number(totals.difference) > 0 ? t('артық төленген') : t('кем төленген') }}</span>
          </p>
        </div>
        <p v-if="previewError && !readOnly" class="text-sm text-amber-700 dark:text-amber-300" aria-live="polite">{{ previewError }}</p>
        <label v-if="hasDifference && !readOnly" class="flex items-start gap-2 text-sm font-medium">
          <input v-model="confirmedPaid" type="checkbox" class="mt-1" :disabled="busy">
          <span>{{ t('Чектегі төленген соманы растаймын. Айырма тауар сомаларына сай санаттарға бөлінеді.') }}</span>
        </label>

        <p v-if="!readOnly && !busy && saveBlocker" id="receipt-save-blocker" class="text-sm text-amber-700 dark:text-amber-300" aria-live="polite">{{ saveBlocker }}</p>
        <div class="flex justify-end gap-2">
          <UButton v-if="readOnly" type="button" color="primary" variant="soft" :label="t('Өңдеу')" @click="readOnly = false" />
          <UButton v-else type="submit" color="primary" :label="t('Сақтау')" :loading="busy" :disabled="!canSave" :aria-describedby="saveBlocker && !busy ? 'receipt-save-blocker' : undefined" />
        </div>
      </form>
    </div>
  </UModal>
</template>

<script setup lang="ts">
import type {
  Category, ExtractedReceipt, ReceiptDraft, ReceiptLine, ReceiptTotals, SavedReceipt, Transaction,
} from '~~/shared/types'

const props = defineProps<{ categories: Category[]; transaction?: Transaction | null; file?: File | null }>()
const emit = defineEmits<{ close: []; saved: [transaction: Transaction] }>()
const api = useApi()
const { tr, money, t, categoryLabel } = useLanguage()
const revision = useState('receipt-revision', () => 0)
const busy = ref(false)
const draftReady = ref(false)
const readOnly = ref(false)
const current = ref<Transaction | null>(null)
const uploadToken = ref('')
const notice = ref('')
const error = ref('')
const previewError = ref('')
const totals = ref<ReceiptTotals | null>(null)
const sourceCurrency = ref<string | null>('KZT')
const confirmKzt = ref(false)
const confirmedPaid = ref(false)
const headerUncertain = ref<string[]>([])
const form = reactive({ merchant: '', branch: '', branch_address: '', purchase_date: '', receipt_number: '', paid: '', order_discount: '0', fees: '0' })

const headerFields = computed(() => [
  { key: 'merchant', label: 'Дүкен' },
  { key: 'purchase_date', label: 'Чек күні' },
  { key: 'receipt_number', label: 'Чек нөмірі' },
  { key: 'branch', label: tr('Филиал', 'Филиал', 'Branch') },
  { key: 'branch_address', label: tr('Филиал мекенжайы', 'Адрес филиала', 'Branch address') },
] as const)
const detailFields = computed(() => [
  { key: 'brand', label: tr('Бренд', 'Бренд', 'Brand'), mode: 'text' },
  { key: 'barcode', label: tr('Штрихкод', 'Штрихкод', 'Barcode'), mode: 'numeric' },
  { key: 'variant', label: tr('Түрі', 'Вид', 'Variant'), mode: 'text' },
  { key: 'fat_percent', label: tr('Майлылығы (%)', 'Жирность (%)', 'Fat (%)'), mode: 'decimal' },
  { key: 'package_size', label: tr('Қаптама көлемі', 'Размер упаковки', 'Package size'), mode: 'decimal' },
  { key: 'package_unit', label: tr('Өлшем бірлігі', 'Единица измерения', 'Package unit'), mode: 'text' },
  { key: 'promotion_condition', label: tr('Акция шарты', 'Условие акции', 'Promotion condition'), mode: 'text' },
] as const)
const amountFields = [
  { key: 'order_discount', label: 'Чекке қосымша жеңілдік (₸)' },
  { key: 'fees', label: 'Қосымша төлем (₸)' },
  { key: 'paid', label: 'Чекте төленді (₸)' },
] as const
const lineFields = [
  { key: 'name', label: 'Тауар', numeric: false },
  { key: 'quantity', label: 'Саны / салмағы', numeric: true },
  { key: 'unit', label: 'Бірлік', numeric: false },
  { key: 'unit_price', label: 'Бірлік бағасы (₸)', numeric: true },
  { key: 'discount', label: 'Жеңілдік (₸)', numeric: true },
  { key: 'line_total', label: 'Жол сомасы (₸)', numeric: true },
] as const

const textValue = (value: string | number | null | undefined) => value == null ? '' : String(value)
const decimalValue = (value: string) => value.trim().replace(',', '.') || null
let nextItemKey = 0

function editableLine(line?: Partial<ReceiptLine>, uncertain: string[] = []) {
  return {
    key: nextItemKey++,
    name: line?.name || '',
    brand: line?.brand || '', barcode: line?.barcode || '', variant: line?.variant || '',
    fat_percent: textValue(line?.fat_percent), package_size: textValue(line?.package_size),
    package_unit: line?.package_unit || '', promotion_condition: line?.promotion_condition || '',
    quantity: textValue(line?.quantity),
    unit: line?.unit || '',
    unit_price: textValue(line?.unit_price),
    discount: textValue(line?.discount),
    line_total: textValue(line?.line_total),
    discount_mode: line?.line_total_is_net == null ? '' : line.line_total_is_net ? 'net' : 'gross',
    category_id: line?.category_id || '',
    allocated_amount: line?.allocated_amount,
    uncertain,
  }
}

const items = ref<ReturnType<typeof editableLine>[]>([])
const title = computed(() => readOnly.value ? t('Чек мәліметтері') : current.value ? t('Чекті өңдеу') : t('Чек жүктеу'))
const hasUncertainty = computed(() => headerUncertain.value.length > 0 || items.value.some(item => item.uncertain.length > 0))
const hasDifference = computed(() => Number(totals.value?.difference || 0) !== 0)
const saveBlocker = computed(() => {
  if (!form.merchant.trim()) return t('Сақтау үшін дүкен атауын енгізіңіз.')
  if (!form.purchase_date) return t('Сақтау үшін чек күнін енгізіңіз.')
  if (!items.value.length) return t('Сақтау үшін кемінде бір тауар қосыңыз.')
  if (items.value.some(item => !item.name.trim())) return t('Сақтау үшін әр тауардың атауын енгізіңіз.')
  if (items.value.some(item => item.barcode.trim() && !/^\d{8,14}$/.test(item.barcode.trim()))) return tr('Штрихкод 8–14 цифрдан тұруы керек.', 'Штрихкод должен содержать 8–14 цифр.', 'Barcodes must contain 8–14 digits.')
  if (!(Number(decimalValue(form.paid)) > 0)) return t('Чекте төленген соманы енгізіңіз.')
  if (sourceCurrency.value !== 'KZT' && !confirmKzt.value) return t('Форманың жоғарғы жағында сомалардың теңгемен көрсетілгенін растаңыз.')
  if (previewError.value) return t('Сақтау үшін есептегі көрсетілген қатені түзетіңіз.')
  if (!totals.value) return t('Сома есептеліп жатыр…')
  if (hasDifference.value && !confirmedPaid.value) return t('Айырманы түзетіңіз немесе төленген соманы растаңыз.')
  return ''
})
const canSave = computed(() => !busy.value && !saveBlocker.value)
const payload = computed<ReceiptDraft>(() => ({
  merchant: form.merchant.trim(),
  branch: form.branch.trim(), branch_address: form.branch_address.trim(),
  purchase_date: form.purchase_date || null,
  receipt_number: form.receipt_number.trim(),
  currency: 'KZT',
  paid: decimalValue(form.paid),
  order_discount: decimalValue(form.order_discount) ?? '0',
  fees: decimalValue(form.fees) ?? '0',
  confirm_paid: false,
  items: items.value.map(item => ({
    name: item.name.trim(),
    brand: item.brand.trim(), barcode: item.barcode.trim(), variant: item.variant.trim(),
    fat_percent: decimalValue(item.fat_percent), package_size: decimalValue(item.package_size),
    package_unit: item.package_unit.trim(), promotion_condition: item.promotion_condition.trim(),
    quantity: decimalValue(item.quantity),
    unit: item.unit.trim(),
    unit_price: decimalValue(item.unit_price),
    discount: decimalValue(item.discount),
    line_total: decimalValue(item.line_total),
    line_total_is_net: item.discount_mode ? item.discount_mode === 'net' : null,
    category_id: item.category_id || null,
  })),
}))

function rowLabel(index: number, text: string) {
  return tr(`${index + 1}-жол: ${text}`, `Строка ${index + 1}: ${text}`, `Line ${index + 1}: ${text}`)
}

function mark(fields: string[], field: string) {
  return (field === 'product_details' ? detailFields.value.some(detail => fields.includes(detail.key)) : fields.includes(field)) ? 'border-amber-500 bg-amber-50 dark:bg-amber-950/40' : ''
}

function comparisonLink(item: ReturnType<typeof editableLine>) {
  const { name, brand, barcode, variant, fat_percent, package_size, package_unit } = item
  return { path: '/deals', query: { name, brand, barcode, variant, fat_percent, package_size, package_unit } }
}

function clearHeader(field: string) {
  headerUncertain.value = headerUncertain.value.filter(key => key !== field)
}

function clearLine(item: ReturnType<typeof editableLine>, field: string) {
  item.uncertain = item.uncertain.filter(key => key !== field)
}

function close(open: boolean) {
  if (!open && !busy.value) emit('close')
}

function loadSaved(transaction: Transaction, message = '') {
  const receipt = transaction.ai_metadata?.receipt as SavedReceipt | undefined
  if (!receipt) return
  current.value = transaction
  readOnly.value = true
  draftReady.value = true
  sourceCurrency.value = 'KZT'
  headerUncertain.value = []
  notice.value = message
  Object.assign(form, {
    merchant: receipt.merchant, purchase_date: receipt.purchase_date || '',
    branch: receipt.branch || '', branch_address: receipt.branch_address || '',
    receipt_number: receipt.receipt_number, paid: textValue(receipt.paid),
    order_discount: receipt.order_discount, fees: receipt.fees,
  })
  items.value = receipt.items.map(line => editableLine({
    ...line,
    category_id: !props.categories.length || props.categories.some(category => category.id === line.category_id) ? line.category_id : null,
  }))
  totals.value = receipt.totals
  confirmedPaid.value = receipt.confirm_paid
}

function loadExtraction(extraction: ExtractedReceipt) {
  sourceCurrency.value = extraction.currency?.trim().toUpperCase() || null
  confirmKzt.value = false
  headerUncertain.value = [...new Set([
    ...extraction.uncertain_fields,
    ...(['merchant', 'purchase_date', 'receipt_number'] as const).filter(key => !extraction[key]),
    ...amountFields.filter(field => extraction[field.key] == null).map(field => field.key),
  ])]
  const date = extraction.purchase_date
  const validDate = date && /^\d{4}-\d{2}-\d{2}$/.test(date) && Number.isFinite(Date.parse(date))
  Object.assign(form, {
    merchant: extraction.merchant?.slice(0, 255) || '', purchase_date: validDate ? date : '',
    branch: extraction.branch?.slice(0, 120) || '', branch_address: extraction.branch_address?.slice(0, 255) || '',
    receipt_number: extraction.receipt_number?.slice(0, 120) || '', paid: textValue(extraction.paid),
    order_discount: textValue(extraction.order_discount), fees: textValue(extraction.fees),
  })
  items.value = extraction.items.map(line => {
    const suggestion = line.suggested_category?.trim().toLowerCase()
    const category = props.categories.find(option => option.name.trim().toLowerCase() === suggestion)
    return editableLine({
      name: line.name?.slice(0, 255) || '', quantity: textValue(line.quantity),
      brand: line.brand?.slice(0, 120), barcode: line.barcode?.slice(0, 24), variant: line.variant?.slice(0, 120),
      fat_percent: textValue(line.fat_percent), package_size: textValue(line.package_size),
      package_unit: line.package_unit?.slice(0, 24), promotion_condition: line.promotion_condition?.slice(0, 255),
      unit: line.unit?.slice(0, 24) || '', unit_price: textValue(line.unit_price),
      discount: textValue(line.discount), line_total: textValue(line.line_total),
      line_total_is_net: line.line_total_is_net, category_id: category?.id,
    }, [...new Set([
      ...line.uncertain_fields,
      ...lineFields.filter(field => line[field.key] == null).map(field => field.key),
      ...(!category ? ['category_id'] : []),
      ...(Number(line.discount) > 0 && line.line_total != null && line.line_total_is_net == null ? ['line_total_is_net'] : []),
    ])])
  })
  if (!items.value.length) items.value = [editableLine(undefined, ['name', 'quantity', 'unit_price', 'line_total', 'category_id'])]
  draftReady.value = true
}

function upload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (file) void uploadFile(file)
}

async function uploadFile(file: File) {
  if (busy.value) return
  error.value = ''
  if (file.size > 10 * 1024 * 1024) {
    error.value = t('Чек файлының көлемі 10 МБ-тан аспауы керек.')
    return
  }
  busy.value = true
  try {
    const body = new FormData()
    body.set('file', file)
    const result = await api.fetch<{ duplicate: Transaction | null; extraction: ExtractedReceipt | null; upload_token: string | null }>('/receipts/upload', { method: 'POST', body })
    if (result.duplicate) {
      loadSaved(result.duplicate, t('Бұл чек бұрын сақталған. Бар операция ашылды.'))
    } else if (result.extraction && result.upload_token) {
      uploadToken.value = result.upload_token
      loadExtraction(result.extraction)
    }
  } catch (failure) {
    const status = getErrorStatus(failure)
    error.value = status === 415 ? t('JPEG, PNG, WebP немесе PDF файлды таңдаңыз.')
      : status === 400 ? t('Сатып алу чегі танылмады. Анығырақ файлды таңдаңыз.')
      : status === 503 ? t('Чекті оқу үшін серверге Gemini кілтін баптау қажет.')
      : t('Чекті оқу мүмкін болмады. Қайталап көріңіз.')
  } finally {
    busy.value = false
  }
}

function calculationError(failure: unknown) {
  const message = formatApiError(failure, '')
  const line = /^Line (\d+): (.+)$/.exec(message)
  if (line) {
    const explanation = line[2].startsWith('specify') ? t('жеңілдіктің жол сомасына кіргенін көрсетіңіз')
      : line[2].startsWith('discount') ? t('жеңілдік жол сомасынан асып кетті')
      : t('жол сомасын немесе саны мен бірлік бағасын енгізіңіз')
    return `${rowLabel(Number(line[1]) - 1, explanation)}.`
  }
  if (message.startsWith('Receipt discount')) return t('Чек жеңілдігі тауарлардың жеңілдіктен кейінгі сомасынан асып кетті.')
  return t('Сомаларды, салмақты және күнді тексеріңіз.')
}

watch([payload, draftReady, readOnly], ([value, ready, viewing], _, onCleanup) => {
  if (!ready || viewing) return
  totals.value = null
  confirmedPaid.value = false
  previewError.value = ''
  if (!value.items.length) return
  let stale = false
  const timer = setTimeout(async () => {
    try {
      const preview = await api.fetch<ReceiptTotals>('/receipts/preview', { method: 'POST', body: value })
      if (!stale) totals.value = preview
    } catch (failure) {
      if (!stale) previewError.value = calculationError(failure)
    }
  }, 250)
  onCleanup(() => {
    stale = true
    clearTimeout(timer)
  })
})

async function save() {
  if (!canSave.value || readOnly.value) return
  busy.value = true
  error.value = ''
  const body = { ...payload.value, confirm_paid: confirmedPaid.value }
  try {
    const result = await api.fetch<{ transaction: Transaction; duplicate: boolean }>(
      current.value ? `/receipts/${current.value.id}` : '/receipts',
      current.value ? { method: 'PUT', body } : { method: 'POST', body: { ...body, upload_token: uploadToken.value } },
    )
    loadSaved(result.transaction, result.duplicate ? t('Бұл чек бұрын сақталған. Бар операция ашылды.') : t('Чек сақталды. Шығыс пен бюджет есебі жаңартылды.'))
    if (!result.duplicate) revision.value++
    emit('saved', result.transaction)
  } catch (failure) {
    error.value = t(formatApiError(failure, t('Чекті сақтау мүмкін болмады.')))
  } finally {
    busy.value = false
  }
}

if (props.transaction) loadSaved(props.transaction)
onMounted(() => {
  if (props.file) void uploadFile(props.file)
})
</script>

<style scoped>
.receipt-input {
  @apply w-full rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm text-slate-900 outline-none focus:ring-2 focus:ring-emerald-500 disabled:text-slate-600 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-100 dark:disabled:text-slate-300;
}

.receipt-input.border-amber-500 {
  border-color: #f59e0b;
}
</style>
