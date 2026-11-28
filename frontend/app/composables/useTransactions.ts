import type { Transaction, TransactionCreate } from '~~/shared/types'

export const useTransactions = () => {
  const api = useApi()
  const transactions = useState<Transaction[]>('transactions', () => [])
  const receiptFile = useState<File | null>('receipt-file', () => null)
  const loading = ref(false)

  const fetchTransactions = async (params: Record<string, any> = {}) => {
    loading.value = true
    try {
      const data = await api.fetch<{ items: Transaction[] }>('/transactions', {
        params,
      })
      transactions.value = data.items
      return data.items
    } finally {
      loading.value = false
    }
  }

  const createTransaction = async (payload: TransactionCreate) => {
    const data = await api.fetch<Transaction>('/transactions', {
      method: 'POST',
      body: payload,
    })
    if (!transactions.value.some(transaction => transaction.id === data.id)) {
      transactions.value.unshift(data)
    }
    return data
  }

  const deleteTransaction = async (id: string) => {
    await api.fetch(`/transactions/${id}`, { method: 'DELETE' })
    transactions.value = transactions.value.filter((t) => t.id !== id)
  }

  return {
    transactions,
    receiptFile,
    loading,
    fetchTransactions,
    createTransaction,
    deleteTransaction,
  }
}
