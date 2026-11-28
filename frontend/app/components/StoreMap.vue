<template>
  <div ref="mapRegion" class="relative isolate h-64 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800 sm:h-72" :aria-label="tr('Дүкендер картасы', 'Карта магазинов', 'Store map')" role="region">
    <img v-for="tile in tiles" :key="tile.url" :src="tile.url" :style="tile.style" alt="" width="256" height="256" class="pointer-events-none absolute max-w-none select-none">
    <span aria-hidden="true" class="absolute left-1/2 top-1/2 z-20 size-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-600 ring-2 ring-white" />
    <button
      v-for="branch in branches" :key="branch.id" type="button" :style="position(branch)" :aria-label="branch.name" :title="branch.name"
      class="absolute -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary-600 p-1 text-white shadow ring-1 ring-white focus-visible:z-30"
      :class="branch.id === selected ? 'z-30 bg-rose-600' : 'z-10'"
      @click="$emit('select', branch)"
    >
      <UIcon name="i-heroicons-map-pin-solid" class="block size-4" />
    </button>
    <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener" class="absolute bottom-0 right-0 z-30 bg-white/95 px-2 py-0.5 text-xs text-slate-800 underline">© OpenStreetMap</a>
  </div>
</template>

<script setup lang="ts">
import type { Area, Point, StoreBranch } from '~~/shared/types/shopping'

const props = defineProps<{ area: Area; branches: StoreBranch[]; selected?: string }>()
defineEmits<{ select: [branch: StoreBranch] }>()
const { tr } = useLanguage()

const zoom = computed(() => {
  const latitudeScale = Math.cos(props.area.lat * Math.PI / 180)
  return Math.max(6, Math.min(16, Math.floor(Math.log2(156.54 * latitudeScale * 112 / props.area.radius))))
})
const world = computed(() => 2 ** zoom.value)
function pixel(point: Point) {
  const radians = Math.max(-85, Math.min(85, point.lat)) * Math.PI / 180
  const size = 256 * world.value
  return { x: (point.lon + 180) / 360 * size, y: (1 - Math.asinh(Math.tan(radians)) / Math.PI) / 2 * size }
}
const center = computed(() => pixel(props.area))
function position(point: Point) {
  const p = pixel(point)
  const size = world.value * 256
  const diff = p.x - center.value.x
  const x = ((diff + size * 1.5) % size) - size / 2
  return { left: `calc(50% + ${x}px)`, top: `calc(50% + ${p.y - center.value.y}px)` }
}
const width = ref(0)
const mapRegion = useTemplateRef<HTMLElement>('mapRegion')
let observer: ResizeObserver | undefined
onMounted(() => {
  if (!mapRegion.value) return
  observer = new ResizeObserver(([entry]) => { if (entry) width.value = entry.contentRect.width })
  observer.observe(mapRegion.value)
})
onBeforeUnmount(() => observer?.disconnect())
const tiles = computed(() => {
  if (!width.value) return []
  const p = center.value
  const result = []
  const left = Math.floor((p.x - width.value / 2) / 256)
  const right = Math.floor((p.x + width.value / 2) / 256)
  for (let y = Math.max(0, Math.floor((p.y - 144) / 256)); y <= Math.min(world.value - 1, Math.floor((p.y + 144) / 256)); y++) {
    for (let x = left; x <= right; x++) {
      const wrapped = (x + world.value) % world.value
      result.push({
        url: `https://tile.openstreetmap.org/${zoom.value}/${wrapped}/${y}.png`,
        style: { left: `calc(50% + ${x * 256 - p.x}px)`, top: `calc(50% + ${y * 256 - p.y}px)` },
      })
    }
  }
  return result
})
</script>
