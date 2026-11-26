export interface CategoryVisual {
  label: string
  icon: string
  badgeClass: string
  hex: string
}

const CATEGORY_MAP: Record<string, CategoryVisual> = {
  Salary: {
    label: 'Жалақы',
    icon: 'i-heroicons-banknotes',
    badgeClass: 'bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20',
    hex: '#10b981',
  },
  Freelance: {
    label: 'Фриланс',
    icon: 'i-heroicons-computer-desktop',
    badgeClass: 'bg-teal-500/12 text-teal-600 dark:text-teal-400 ring-1 ring-teal-500/20',
    hex: '#14b8a6',
  },
  Investments: {
    label: 'Инвестициялар',
    icon: 'i-heroicons-arrow-trending-up',
    badgeClass: 'bg-cyan-500/12 text-cyan-600 dark:text-cyan-400 ring-1 ring-cyan-500/20',
    hex: '#06b6d4',
  },
  Groceries: {
    label: 'Азық-түлік',
    icon: 'i-heroicons-shopping-cart',
    badgeClass: 'bg-amber-500/12 text-amber-600 dark:text-amber-400 ring-1 ring-amber-500/20',
    hex: '#f59e0b',
  },
  Transport: {
    label: 'Көлік',
    icon: 'i-heroicons-truck',
    badgeClass: 'bg-sky-500/12 text-sky-600 dark:text-sky-400 ring-1 ring-sky-500/20',
    hex: '#0ea5e9',
  },
  Utilities: {
    label: 'Коммуналдық төлем',
    icon: 'i-heroicons-bolt',
    badgeClass: 'bg-purple-500/12 text-purple-600 dark:text-purple-400 ring-1 ring-purple-500/20',
    hex: '#a855f7',
  },
  Entertainment: {
    label: 'Ойын-сауық',
    icon: 'i-heroicons-film',
    badgeClass: 'bg-pink-500/12 text-pink-600 dark:text-pink-400 ring-1 ring-pink-500/20',
    hex: '#ec4899',
  },
  Health: {
    label: 'Денсаулық',
    icon: 'i-heroicons-heart',
    badgeClass: 'bg-rose-500/12 text-rose-600 dark:text-rose-400 ring-1 ring-rose-500/20',
    hex: '#f43f5e',
  },
  Dining: {
    label: 'Дәмхана мен тамақ',
    icon: 'i-heroicons-cake',
    badgeClass: 'bg-orange-500/12 text-orange-600 dark:text-orange-400 ring-1 ring-orange-500/20',
    hex: '#f97316',
  },
  Shopping: {
    label: 'Сауда-саттық',
    icon: 'i-heroicons-shopping-bag',
    badgeClass: 'bg-violet-500/12 text-violet-600 dark:text-violet-400 ring-1 ring-violet-500/20',
    hex: '#8b5cf6',
  },
  Education: {
    label: 'Білім',
    icon: 'i-heroicons-academic-cap',
    badgeClass: 'bg-indigo-500/12 text-indigo-600 dark:text-indigo-400 ring-1 ring-indigo-500/20',
    hex: '#6366f1',
  },
  Other: {
    label: 'Басқа шығындар',
    icon: 'i-heroicons-squares-2x2',
    badgeClass: 'bg-slate-500/12 text-slate-600 dark:text-slate-300 ring-1 ring-slate-500/20',
    hex: '#64748b',
  },
}

const FALLBACK_COLORS = [
  '#10b981',
  '#0ea5e9',
  '#f59e0b',
  '#8b5cf6',
  '#f43f5e',
  '#14b8a6',
  '#f97316',
  '#6366f1',
]

export function getCategoryVisual(name?: string | null, type: 'income' | 'expense' | 'transfer' = 'expense'): CategoryVisual {
  if (name && CATEGORY_MAP[name]) {
    return CATEGORY_MAP[name]
  }
  if (name && name.trim()) {
    let hash = 0
    for (let i = 0; i < name.length; i++) {
      hash = (hash * 31 + name.charCodeAt(i)) >>> 0
    }
    return {
      label: name,
      icon: type === 'income' ? 'i-heroicons-arrow-down-left' : 'i-heroicons-tag',
      badgeClass: type === 'income'
        ? 'bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20'
        : 'bg-slate-500/12 text-slate-600 dark:text-slate-300 ring-1 ring-slate-500/20',
      hex: FALLBACK_COLORS[hash % FALLBACK_COLORS.length] || '#10b981',
    }
  }
  return type === 'income'
    ? {
        label: 'Кіріс',
        icon: 'i-heroicons-banknotes',
        badgeClass: 'bg-emerald-500/12 text-emerald-600 dark:text-emerald-400 ring-1 ring-emerald-500/20',
        hex: '#10b981',
      }
    : {
        label: 'Санатсыз',
        icon: 'i-heroicons-credit-card',
        badgeClass: 'bg-slate-500/12 text-slate-600 dark:text-slate-300 ring-1 ring-slate-500/20',
        hex: '#64748b',
      }
}

export function translateCategoryName(name?: string | null, fallback = 'Жалпы'): string {
  if (!name) return fallback
  return CATEGORY_MAP[name]?.label || name
}

const KZ_MONTHS_SHORT = [
  'қаң', 'ақп', 'нау', 'сәу', 'мам', 'мау',
  'шіл', 'там', 'қыр', 'қаз', 'қар', 'жел',
]

const KZ_MONTHS_FULL = [
  'Қаңтар', 'Ақпан', 'Наурыз', 'Сәуір', 'Мамыр', 'Маусым',
  'Шілде', 'Тамыз', 'Қыркүйек', 'Қазан', 'Қараша', 'Желтоқсан',
]

export function formatKzDate(dateStr: string): string {
  const parts = dateStr.split('-')
  if (parts.length !== 3) return dateStr
  const monthIdx = Number(parts[1]) - 1
  const day = Number(parts[2])
  if (monthIdx < 0 || monthIdx > 11 || Number.isNaN(day)) return dateStr
  return `${day} ${KZ_MONTHS_SHORT[monthIdx]}`
}

export function formatKzMonth(ym: string): string {
  const parts = ym.split('-')
  if (parts.length !== 2) return ym
  const year = parts[0]
  const monthIdx = Number(parts[1]) - 1
  if (monthIdx < 0 || monthIdx > 11) return ym
  return `${KZ_MONTHS_FULL[monthIdx]} ${year}`
}
