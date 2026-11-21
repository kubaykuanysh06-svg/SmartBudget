import type { Transaction, TransactionCreate } from '~~/shared/types'

export const useTransactions = () => {
  const api = useApi()
  const transactions = useState<Transaction[]>('transactions', () => [])
  const loading = ref(false)

  const fetchTransactions = async (params: Record<string, any> = {}) => {
    loading.value = true
    try {
      const data = await api.fetch<Transaction[]>('/transactions', {
        params,
      })
      transactions.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createTransaction = async (payload: TransactionCreate) => {
    const data = await api.fetch<Transaction>('/transactions', {
      method: 'POST',
      body: payload,
    })
    transactions.value.unshift(data)
    return data
  }

  const deleteTransaction = async (id: string) => {
    await api.fetch(`/transactions/${id}`, { method: 'DELETE' })
    transactions.value = transactions.value.filter((t) => t.id !== id)
  }

  return {
    transactions,
    loading,
    fetchTransactions,
    createTransaction,
    deleteTransaction,
  }
}
