import type { SummaryAnalytics, CategoryBreakdown, TrendPoint } from '~~/shared/types'

export const useAnalytics = () => {
  const api = useApi()

  const getSummary = async (params: Record<string, any> = {}) => {
    return await api.fetch<SummaryAnalytics>('/analytics/summary', { params })
  }

  const getByCategory = async (params: Record<string, any> = {}) => {
    return await api.fetch<CategoryBreakdown[]>('/analytics/by-category', { params })
  }

  const getTrends = async (params: Record<string, any> = {}) => {
    return await api.fetch<TrendPoint[]>('/analytics/trends', { params })
  }

  return {
    getSummary,
    getByCategory,
    getTrends,
  }
}
