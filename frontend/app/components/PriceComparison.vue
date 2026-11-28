<template>
  <div class="space-y-4">
    <UCard>
      <template #header><h3 class="sb-section-title">{{ tr('Филиалдар картасы', 'Карта филиалов', 'Store branches') }}</h3></template>
      <div class="space-y-4">
        <div class="flex flex-wrap items-end gap-3">
          <UButton variant="soft" icon="i-heroicons-map-pin" :loading="locating" @click="locate">{{ tr('Орнымды анықтау', 'Определить местоположение', 'Use my location') }}</UButton>
          <label class="text-sm">{{ tr('Радиус (км)', 'Радиус (км)', 'Radius (km)') }}<USelect v-model.number="radius" :options="[1, 3, 5, 10, 15]" /></label>
        </div>
        <form class="flex flex-wrap items-end gap-2" @submit.prevent="searchPlaces">
          <label class="min-w-[12rem] flex-1 text-sm">{{ tr('Қала, аудан немесе мекенжай', 'Город, район или адрес', 'City, district or address') }}<UInput v-model="placeQuery" minlength="2" maxlength="160" required /></label>
          <UButton type="submit" :loading="placeBusy">{{ tr('Мекенжайды іздеу', 'Найти адрес', 'Find address') }}</UButton>
        </form>
        <p v-if="locationIssue" role="status" class="text-sm text-amber-700 dark:text-amber-300">{{ locationMessage }}</p>
        <div v-if="places.length" class="flex flex-wrap gap-2">
          <UButton v-for="place in places" :key="place.name + place.lat + place.lon" color="gray" variant="outline" @click="choosePlace(place)">{{ place.name }}</UButton>
        </div>
        <template v-if="area">
          <p class="text-sm font-semibold">{{ placeName || tr('Ағымдағы орын', 'Текущее местоположение', 'Current location') }}</p>
          <div class="grid gap-4 lg:grid-cols-2">
            <ClientOnly><StoreMap :area="area" :branches="branches" :selected="selected?.id" @select="selectBranch" /></ClientOnly>
            <div class="max-h-72 space-y-2 overflow-auto text-sm">
              <p v-if="branchBusy" role="status" class="sb-muted">{{ tr('Филиалдар ізделуде…', 'Поиск филиалов…', 'Finding branches…') }}</p>
              <p v-else-if="!branchAvailable" role="status" class="text-amber-700 dark:text-amber-300">{{ tr('Филиалдар дереккөзі уақытша қолжетімсіз.', 'Источник данных о филиалах недоступен.', 'The branch data source is temporarily unavailable.') }}</p>
              <p v-else-if="!branches.length" class="sb-muted">{{ tr('Радиус ішінде картаға тіркелген филиал табылмады.', 'В радиусе нет филиалов на карте.', 'No mapped branches found within this radius.') }}</p>
              <div v-for="branch in branches" :key="branch.id" class="rounded-lg bg-[var(--sb-soft)] px-3 py-2">
                <button type="button" class="w-full text-left" :aria-expanded="selected?.id === branch.id" @click="selectBranch(branch)">
                  <span class="flex justify-between gap-2 font-semibold"><span>{{ branch.name }}</span><span class="shrink-0">{{ km(branch.distance_km) }}</span></span>
                  <span class="text-xs sb-muted">{{ branch.address || tr('Мекенжай көрсетілмеген', 'Адрес не указан', 'Address unavailable') }}</span>
                </button>
                <p v-if="selected?.id === branch.id" class="mt-1 text-xs sb-muted" aria-live="polite">
                  {{ routeBusy ? tr('Маршрут ізделуде…', 'Поиск маршрута…', 'Finding route…') : routeInfo ? tr('Жолмен', 'По дороге', 'By road') + ' ' + km(routeInfo.distance_km) + ' · ' + routeInfo.minutes + ' ' + tr('мин', 'мин', 'min') : tr('Жол маршруты қолжетімсіз. Қашықтық түзу сызықпен берілген.', 'Маршрут недоступен. Расстояние указано по прямой.', 'Route unavailable. Distance is measured in a straight line.') }}
                </p>
              </div>
            </div>
          </div>
        </template>
      </div>
    </UCard>
    <UCard>
      <template #header><h3 class="sb-section-title">{{ tr('Тауар бағаларын салыстыру', 'Сравнение цен товаров', 'Compare product prices') }}</h3></template>
      <form class="space-y-3" @submit.prevent="submitSearch">
        <div class="flex flex-wrap items-end gap-2">
          <label class="min-w-[12rem] flex-1 text-sm">{{ tr('Тауар атауы немесе штрихкод', 'Название товара или штрихкод', 'Product name or barcode') }}<UInput v-model="query" maxlength="255" required /></label>
          <UButton type="submit" :loading="priceBusy">{{ tr('Бағаны іздеу', 'Найти цены', 'Find prices') }}</UButton>
        </div>
        <div class="flex flex-wrap items-end gap-3">
          <label class="text-sm">{{ tr('Жол шығыны (₸/км, екі бағыт)', 'Расходы на дорогу (₸/км, туда и обратно)', 'Travel rate (₸/km, round trip)') }}<UInput v-model="travel" type="number" min="0" max="100000" step="0.01" /></label>
          <label class="flex items-center gap-2 py-2 text-sm"><input v-model="conditions" type="checkbox">{{ tr('Акция шарттарын орындай аламын', 'Могу выполнить условия акций', 'I qualify for the promotion conditions') }}</label>
        </div>
      </form>
      <p v-if="reference" class="mt-3 text-sm"><strong>{{ tr('Салыстыру үшін таңдалған тауар', 'Выбранный товар', 'Selected product') }}</strong> · {{ reference.name }}</p>
      <p v-if="priceError" role="alert" class="mt-3 text-sm text-rose-600">{{ tr('Баға деректері жүктелмеді.', 'Не удалось загрузить цены.', 'Could not load price data.') }}</p>
      <div v-if="result" class="mt-4 space-y-4">
        <p v-if="!result.offers.some(offer => offer.current_price_verified)" class="text-sm text-amber-700 dark:text-amber-300">{{ tr('Бүгінгі баға мен қорды растауға дерек жеткіліксіз. Көрсетілген бағалардың тіркелген күнін тексеріңіз.', 'Недостаточно данных для подтверждения цен и наличия на сегодня. Проверяйте даты указанных цен.', 'There is insufficient data to verify today’s prices and stock. Check the date of each price.') }}</p>
        <p v-if="!result.offers.length" class="text-sm sb-muted">{{ tr('Сәйкес баға дерегі табылмады.', 'Подходящих цен не найдено.', 'No matching price data found.') }}</p>
        <p v-else-if="result.offers[0]?.match === 'search'" class="text-sm sb-muted">{{ tr('Салыстыру үшін тізімнен нақты тауарды таңдаңыз.', 'Выберите товар в списке для сравнения.', 'Select a product below to compare its offers.') }}</p>
        <p v-if="area && result.offers.some(offer => offer.distance_km === null)" class="text-sm sb-muted">{{ tr('Орны белгісіз филиалдар радиус бойынша ұсыныстарға кірмейді.', 'Филиалы без координат не учитываются в рекомендациях по радиусу.', 'Branches without a known location are excluded from recommendations within the radius.') }}</p>
        <div v-if="recommendations.length" class="grid gap-3 sm:grid-cols-2">
          <div v-for="card in recommendations" :key="card.key" class="rounded-xl bg-[var(--sb-soft)] p-3 text-sm">
            <h4 class="font-bold">{{ card.label }}</h4>
            <p>{{ card.offer.product.name }} · {{ offerName(card.offer) }} · <strong>{{ card.key === 'closest' ? km(Number(card.value)) : money(card.value) }}</strong><span v-if="card.key === 'cheapest_unit'"> / {{ unit(card.offer.unit) }}</span></p>
            <p class="text-xs sb-muted">{{ evidence(card.offer) }} · {{ card.offer.date }}</p>
            <p v-if="card.offer.age_days > 14" class="text-xs text-amber-700 dark:text-amber-300">{{ tr(`Баға ${card.offer.age_days} күн бұрын тіркелген, қазір өзгеруі мүмкін.`, `Цена зафиксирована ${card.offer.age_days} дн. назад и могла измениться.`, `This price was recorded ${card.offer.age_days} days ago and may have changed.`) }}</p>
            <p v-if="card.compare && card.savings !== null" class="text-xs sb-muted">
              {{ tr('Үнем', 'Экономия', 'Savings') }} {{ money(card.savings) }}<span v-if="card.key === 'cheapest_unit'"> / {{ unit(card.offer.unit) }}</span> · {{ tr('Салыстырылған ұсыныс', 'С чем сравнили', 'Compared with') }} {{ card.compare.product.name }} · {{ offerName(card.compare) }} · {{ card.key === 'cheapest_unit' ? money(card.compare.unit_price) + ' / ' + unit(card.compare.unit) : card.key === 'cheapest_with_trip' ? money(card.compare.trip_total) : money(card.compare.package_price) }} ({{ card.compare.date }})
            </p>
            <p v-if="card.key === 'cheapest_with_trip'" class="text-xs sb-muted">{{ tr('Түзу сызықпен есептелген болжам.', 'Оценка по расстоянию по прямой.', 'Estimate based on straight-line distance.') }}</p>
          </div>
        </div>
        <p v-if="result.offers.length && result.offers[0]?.match !== 'search' && !result.offers.some(offer => offer.distance_km !== null)" class="text-sm sb-muted">
          {{ area
            ? tr('Бұл ұсыныстардың филиалдары картадан табылмады, сондықтан «Ең жақын» нұсқа мен жол құны есептелмеді.', 'Филиалы этих предложений не найдены на карте, поэтому «Ближайший» вариант и стоимость дороги не рассчитаны.', 'These offers’ branches were not found on the map, so the closest option and travel cost could not be calculated.')
            : tr('Орныңызды таңдасаңыз, «Ең жақын» нұсқа мен жол құны да есептеледі.', 'Укажите местоположение, чтобы рассчитать «Ближайший» вариант и стоимость дороги.', 'Choose your location to also see the closest option and travel cost.') }}
        </p>
        <section v-for="section in sections" :key="section.key">
          <h4 class="mb-2 text-sm font-bold">{{ section.label }}</h4>
          <div class="grid gap-2 xl:grid-cols-2">
            <div v-for="offer in section.rows" :key="offer.id" class="space-y-1 rounded-xl border border-[var(--sb-line)] p-3 text-sm">
              <div class="flex flex-wrap justify-between gap-2">
                <strong>{{ offer.product.name }}</strong><span v-if="offer.package_price !== null" class="font-bold tabular-nums">{{ money(offer.package_price) }}</span>
              </div>
              <p v-if="offer.product.package_size" class="sb-muted">{{ tr('Қаптама', 'Упаковка', 'Package') }} · {{ decimal(offer.product.package_size) }} {{ unit(offer.product.package_unit || '') }}</p>
              <p>{{ offerName(offer) }} · {{ offer.address || tr('Мекенжай көрсетілмеген', 'Адрес не указан', 'Address unavailable') }}</p>
              <p class="sb-muted">{{ offer.unit_price !== null ? money(offer.unit_price) + ' / ' + unit(offer.unit) : tr('Бірлік бағасы белгісіз', 'Цена за единицу неизвестна', 'Unit price unavailable') }} · {{ offer.distance_km === null ? tr('Қашықтық белгісіз', 'Расстояние неизвестно', 'Distance unavailable') : km(offer.distance_km) }}</p>
              <p class="sb-muted">{{ evidence(offer) }} · {{ offer.date }} · <a v-if="offer.source_url" :href="offer.source_url" target="_blank" rel="noopener" class="underline">{{ offer.source_name }}</a><NuxtLink v-else-if="offer.transaction_id" :to="{ path: '/transactions', query: { receipt: offer.transaction_id } }" class="underline">{{ tr('Сіздің чегіңіз', 'Ваш чек', 'Your receipt') }}</NuxtLink><span v-else>{{ offer.source_name }}</span></p>
              <p class="sb-muted">{{ offer.available_today === true ? tr('Қорда бар екені расталды', 'Наличие подтверждено', 'In stock, verified') : offer.available_today === false ? tr('Қорда жоқ', 'Нет в наличии', 'Out of stock') : tr('Қордағы күйі расталмаған', 'Наличие не подтверждено', 'Stock unverified') }}</p>
              <p v-if="offer.condition" class="text-amber-700 dark:text-amber-300">{{ tr('Акция шарты', 'Условие акции', 'Promotion condition') }} · {{ offer.condition }}</p>
              <p v-if="offer.trip_total !== null" class="font-medium">{{ tr('Жолды қосқанда', 'С учётом дороги', 'With travel') }} {{ money(offer.trip_total) }}</p>
              <p v-else-if="offer.condition && Number(travel) > 0 && offer.distance_km !== null" class="text-xs sb-muted">{{ tr('Акцияға қажетті сатып алудың толық сомасы белгісіз.', 'Полная стоимость покупки по акции неизвестна.', 'The full qualifying purchase cost is unknown.') }}</p>
              <UButton v-if="offer.match !== 'exact'" size="xs" variant="soft" @click="chooseProduct(offer.product)">{{ tr('Осы тауарды салыстыру', 'Сравнить этот товар', 'Compare this product') }}</UButton>
            </div>
          </div>
        </section>
      </div>
    </UCard>
  </div>
</template>

<script setup lang="ts">
import type { Area, Comparison, Offer, Place, Point, ProductReference, StoreBranch } from '~~/shared/types/shopping'

const { language, tr, money, decimal } = useLanguage()
const api = useApi()
const currentRoute = useRoute()
const query = ref('')
const submittedQuery = ref('')
const reference = ref<ProductReference | null>(null)
const radius = ref(3)
const point = ref<Point | null>(null)
const area = computed<Area | null>(() => point.value ? { ...point.value, radius: Number(radius.value) } : null)
const placeName = ref('')
const placeQuery = ref('')
const places = ref<Place[]>([])
const placeBusy = ref(false)
const locating = ref(false)
const locationIssue = ref<'denied' | 'unavailable' | 'no-place' | ''>('')
const branches = ref<StoreBranch[]>([])
const branchBusy = ref(false)
const branchAvailable = ref(true)
const selected = ref<StoreBranch>()
const routeBusy = ref(false)
const routeInfo = ref<{ distance_km: number; minutes: number } | null>(null)
const priceBusy = ref(false)
const priceError = ref(false)
const result = ref<Comparison | null>(null)
const conditions = ref(false)
const travel = ref<number | string>('')
const km = (value: number) => decimal(value) + ' ' + tr('км', 'км', 'km')
const unit = (value: string) => ({ l: tr('л', 'л', 'L'), kg: tr('кг', 'кг', 'kg'), pc: tr('дана', 'шт.', 'item') } as Record<string, string>)[value] || value
const locationMessage = computed(() => ({
  denied: tr('Орналасуға рұқсат берілмеді. Мекенжайды қолмен іздеңіз.', 'Доступ к геолокации запрещён. Введите адрес вручную.', 'Location permission denied. Search for an address manually.'),
  unavailable: tr('Орналасу қолжетімсіз. Мекенжайды қолмен іздеңіз.', 'Геолокация недоступна. Введите адрес вручную.', 'Location unavailable. Search for an address manually.'),
  'no-place': tr('Мекенжай табылмады. Қала атауымен іздеп көріңіз.', 'Адрес не найден. Попробуйте название города.', 'No address found. Try searching for the city.'),
  '': '',
})[locationIssue.value])

function locate() {
  locationIssue.value = ''
  if (!navigator.geolocation || !window.isSecureContext) {
    locationIssue.value = 'unavailable'
    return
  }
  locating.value = true
  navigator.geolocation.getCurrentPosition(({ coords }) => {
    locating.value = false
    placeName.value = ''
    point.value = { lat: coords.latitude, lon: coords.longitude }
  }, error => {
    locating.value = false
    locationIssue.value = error.code === 1 ? 'denied' : 'unavailable'
  }, { timeout: 10000, maximumAge: 60000 })
}
async function searchPlaces() {
  const name = placeQuery.value.trim()
  if (name.length < 2) return
  placeBusy.value = true
  places.value = []
  locationIssue.value = ''
  try {
    places.value = await api.fetch<Place[]>('/shopping/places', { query: { query: name, lang: language.value } })
    if (!places.value.length) locationIssue.value = 'no-place'
  } catch {
    locationIssue.value = 'unavailable'
  } finally {
    placeBusy.value = false
  }
}
function choosePlace(place: Place) {
  locationIssue.value = ''
  placeName.value = place.name
  point.value = { lat: place.lat, lon: place.lon }
  places.value = []
}

let branchRequest = 0
async function loadBranches() {
  if (!area.value) return
  const request = ++branchRequest
  branches.value = []
  selected.value = undefined
  routeRequest++
  branchBusy.value = true
  try {
    const data = await api.fetch<{ available: boolean; branches: StoreBranch[] }>('/shopping/branches', { method: 'POST', body: area.value })
    if (request === branchRequest) {
      branches.value = data.branches
      branchAvailable.value = data.available
    }
  } catch {
    if (request === branchRequest) branchAvailable.value = false
  } finally {
    if (request === branchRequest) branchBusy.value = false
  }
}

let routeRequest = 0
async function selectBranch(branch: StoreBranch) {
  if (!point.value) return
  const request = ++routeRequest
  selected.value = branch
  routeBusy.value = true
  routeInfo.value = null
  try {
    const data = await api.fetch<typeof routeInfo.value>('/shopping/route', {
      method: 'POST', body: { ...point.value, to_lat: branch.lat, to_lon: branch.lon },
    })
    if (request === routeRequest) routeInfo.value = data
  } catch {
    if (request === routeRequest) routeInfo.value = null
  } finally {
    if (request === routeRequest) routeBusy.value = false
  }
}

let priceRequest = 0
async function loadPrices() {
  if (!submittedQuery.value && !reference.value) return
  const request = ++priceRequest
  priceError.value = false
  priceBusy.value = true
  try {
    const data = await api.fetch<Comparison>('/shopping/compare', {
      method: 'POST',
      body: { query: submittedQuery.value, reference: reference.value, area: area.value, cost_per_km: Number(travel.value) || 0, allow_conditions: conditions.value },
    })
    if (request === priceRequest) result.value = data
  } catch {
    if (request === priceRequest) {
      priceError.value = true
      result.value = null
    }
  } finally {
    if (request === priceRequest) priceBusy.value = false
  }
}
function submitSearch() {
  submittedQuery.value = query.value.trim()
  reference.value = null
  result.value = null
  void loadPrices()
}
function chooseProduct(product: ProductReference) {
  reference.value = product
  query.value = product.name
  submittedQuery.value = product.name
  result.value = null
  void loadPrices()
}
function fromLink() {
  const field = (key: string) => typeof currentRoute.query[key] === 'string' ? String(currentRoute.query[key]) : ''
  const name = field('name')
  if (name) chooseProduct({
    name, brand: field('brand'), barcode: field('barcode'), variant: field('variant'),
    fat_percent: field('fat_percent'), package_size: field('package_size'), package_unit: field('package_unit'),
  })
}
const offerName = (offer: Offer) => [offer.store, offer.branch].filter(Boolean).join(' · ')
const evidence = (offer: Offer) => offer.current_price_verified
  ? tr('Бүгінгі расталған баға', 'Сегодняшняя подтверждённая цена', 'Verified price today')
  : offer.source_kind === 'receipt' ? tr('Чекте тіркелген баға', 'Цена из чека', 'Price recorded on receipt')
    : tr('Бұрын тіркелген баға', 'Ранее зафиксированная цена', 'Previously recorded price')

const sections = computed(() => [
  { key: 'exact', label: tr('Дәл сол тауар', 'Тот же товар', 'Exact product') },
  { key: 'other_package', label: tr('Сипаты бірдей, қаптамасы басқа', 'Те же характеристики, другая упаковка', 'Same characteristics, different pack') },
  { key: 'similar', label: tr('Ұқсас баламалар', 'Похожие варианты', 'Similar alternatives') },
  { key: 'uncertain', label: tr('Күмәнді сәйкестіктер', 'Сомнительные совпадения', 'Uncertain matches') },
  { key: 'search', label: tr('Табылған тауарлар', 'Найденные товары', 'Products found') },
].map(section => ({ ...section, rows: result.value?.offers.filter(offer => offer.match === section.key) || [] })).filter(section => section.rows.length))

const recommendations = computed(() => {
  if (!result.value) return []
  const data = result.value
  const names = {
    cheapest_package: tr('Қаптамасы ең арзан', 'Самая дешёвая упаковка', 'Cheapest package'),
    cheapest_unit: tr('Өлшем бірлігі ең арзан', 'Лучшая цена за единицу', 'Lowest unit price'),
    closest: tr('Ең жақын', 'Ближайший', 'Closest'),
    cheapest_with_trip: tr('Жолмен бірге ең тиімді', 'Выгоднее с учётом дороги', 'Lowest total with travel'),
  }
  return (Object.keys(names) as (keyof typeof names)[]).flatMap(key => {
    const row = data.recommendations[key]
    if (!row) return []
    const offer = data.offers.find(item => item.id === row.offer_id)
    const compare = data.offers.find(item => item.id === row.compare_id)
    return offer ? [{ ...row, key, label: names[key], offer, compare }] : []
  })
})

watch(area, () => { void loadBranches(); void loadPrices() })
let travelTimer: ReturnType<typeof setTimeout> | undefined
watch([travel, conditions], () => {
  clearTimeout(travelTimer)
  travelTimer = setTimeout(() => { if (Number(travel.value) >= 0 && Number(travel.value) <= 100000) void loadPrices() }, 350)
})
onMounted(fromLink)
watch(() => currentRoute.query, fromLink)
onBeforeUnmount(() => clearTimeout(travelTimer))
</script>
