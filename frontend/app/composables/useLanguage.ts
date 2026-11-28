import { messages } from '~/utils/localeMessages'
import { formatKzDate, formatKzMonth, translateCategoryName } from '~/utils/categoryDisplay'

export type Language = 'kk' | 'ru' | 'en'

export function useLanguage() {
  const saved = useCookie<Language>('smartbudget_locale', { default: () => 'kk', maxAge: 31536000, sameSite: 'lax' })
  const selected = useState<Language>('smartbudget-language', () => saved.value === 'ru' || saved.value === 'en' ? saved.value : 'kk')
  const language = computed<Language>({
    get: () => selected.value,
    set: value => { selected.value = value; saved.value = value },
  })
  const locale = computed(() => ({ kk: 'kk-KZ', ru: 'ru-KZ', en: 'en-GB' })[language.value])
  const tr = (kk: string, ru: string, en: string) => ({ kk, ru, en })[language.value]
  const t = (label: string) => language.value === 'kk' ? label : messages[label]?.[language.value === 'ru' ? 0 : 1] || label
  const tenge = computed(() => new Intl.NumberFormat(locale.value, { maximumFractionDigits: 2 }))
  const money = (value: number | string | null | undefined) => value == null ? '—' : tenge.value.format(Number(value)) + ' ₸'
  const decimal = (value: number | string) => new Intl.NumberFormat(locale.value, { maximumFractionDigits: 3 }).format(Number(value))
  const categoryLabel = (name?: string | null, fallback = 'Жалпы') => t(translateCategoryName(name, fallback))
  const dateLabel = (value: string) => language.value === 'kk' ? formatKzDate(value) :
    new Intl.DateTimeFormat(locale.value, { day: 'numeric', month: 'short', timeZone: 'UTC' }).format(new Date(value + 'T00:00:00Z'))
  const monthLabel = (value: string, compact = false) => language.value === 'kk' ?
    (compact ? formatKzMonth(value).split(' ')[0] : formatKzMonth(value)) :
    new Intl.DateTimeFormat(locale.value, { month: 'long', year: compact ? undefined : 'numeric', timeZone: 'UTC' }).format(new Date(value + '-01T00:00:00Z'))
  // The backend stores receipt descriptions as "Чек · <merchant>"; show the prefix in the chosen language.
  const descriptionLabel = (item: { description?: string | null; ai_metadata?: Record<string, any> }) => {
    const text = item.description || ''
    return item.ai_metadata?.receipt && text.startsWith('Чек · ') ? tr('Чек', 'Чек', 'Receipt') + text.slice(3) : text
  }
  return { language, locale, t, tr, money, decimal, categoryLabel, dateLabel, monthLabel, descriptionLabel }
}
