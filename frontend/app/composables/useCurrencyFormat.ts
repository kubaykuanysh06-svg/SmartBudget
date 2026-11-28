export const useCurrencyFormat = () => {
  const { user } = useAuth()
  const { locale } = useLanguage()
  const currency = computed(() => user.value?.currency || 'KZT')
  const formatter = computed(() => new Intl.NumberFormat(locale.value, {
    style: 'currency',
    currencyDisplay: 'narrowSymbol',
    currency: /^[A-Za-z]{3}$/.test(currency.value) ? currency.value : 'KZT',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }))
  const formatCurrency = (amount: number | string) => formatter.value.format(Number(amount) || 0)

  return { currency, formatCurrency }
}
