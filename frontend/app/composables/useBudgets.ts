import type { Budget, BudgetStatus } from '~~/shared/types'

export const useBudgets = () => {
  const api = useApi()
  const budgets = useState<BudgetStatus[]>('budgets_status', () => [])
  const loading = ref(false)

  const fetchBudgets = async () => {
    loading.value = true
    try {
      const data = await api.fetch<BudgetStatus[]>('/budgets/status')
      budgets.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createBudget = async (payload: { category_id?: string | null; limit_amount: number; period: string; start_date: string }) => {
    const data = await api.fetch<Budget>('/budgets', {
      method: 'POST',
      body: payload,
    })
    await fetchBudgets()
    return data
  }

  const deleteBudget = async (id: string) => {
    await api.fetch(`/budgets/${id}`, { method: 'DELETE' })
    budgets.value = budgets.value.filter(b => b.id !== id)
  }

  return {
    budgets,
    loading,
    fetchBudgets,
    createBudget,
    deleteBudget,
  }
}
