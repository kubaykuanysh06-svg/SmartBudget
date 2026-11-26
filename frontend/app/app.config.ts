export default defineAppConfig({
  ui: {
    primary: 'emerald',
    gray: 'slate',
    card: {
      rounded: 'rounded-2xl',
      shadow: 'shadow-sm',
      background: 'bg-white dark:bg-slate-900/90',
      ring: 'ring-1 ring-slate-200/80 dark:ring-slate-800/90',
      divide: 'divide-y divide-slate-100 dark:divide-slate-800/80',
    },
    button: {
      rounded: 'rounded-xl',
      font: 'font-semibold',
    },
    input: {
      rounded: 'rounded-xl',
    },
    select: {
      rounded: 'rounded-xl',
    },
    modal: {
      rounded: 'rounded-2xl',
      overlay: {
        background: 'bg-slate-950/60 backdrop-blur-xs',
      },
    },
  },
})
