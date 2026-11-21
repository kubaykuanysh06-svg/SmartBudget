import type { Deal } from '~~/shared/types'

export const useDeals = () => {
  const api = useApi()
  const deals = useState<Deal[]>('deals_list', () => [])
  const personalizedDeals = useState<Deal[]>('deals_personalized', () => [])
  const loading = ref(false)

  const fetchDeals = async (params: Record<string, any> = {}) => {
    loading.value = true
    try {
      const data = await api.fetch<Deal[]>('/deals', { params })
      deals.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const fetchPersonalized = async () => {
    try {
      const data = await api.fetch<Deal[]>('/deals/personalized')
      personalizedDeals.value = data
      return data
    } catch {
      return []
    }
  }

  return {
    deals,
    personalizedDeals,
    loading,
    fetchDeals,
    fetchPersonalized,
  }
}
