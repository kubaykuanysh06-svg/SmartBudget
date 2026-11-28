export default defineAppConfig({
  ui: {
    primary: 'violet',
    gray: 'slate',
    card: {
      rounded: 'rounded-[20px]',
      shadow: 'shadow-[var(--sb-shadow)]',
      background: 'bg-[var(--sb-surface)]',
      ring: 'ring-1 ring-[var(--sb-line)]',
      divide: 'divide-y divide-[var(--sb-line)]',
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
      rounded: 'rounded-[22px]',
      background: 'bg-[var(--sb-surface)] dark:bg-[var(--sb-surface)]',
      overlay: {
        background: 'bg-[#160f32]/55 backdrop-blur-sm',
      },
    },
  },
})
