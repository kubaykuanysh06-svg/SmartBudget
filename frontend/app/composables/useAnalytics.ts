import type { SummaryAnalytics, CategoryBreakdown, ReceiptReport, TrendPoint } from '~~/shared/types'

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

  const getReceiptReport = (params: Record<string, string>) =>
    api.fetch<ReceiptReport>('/analytics/receipts', { params })

  return {
    getSummary,
    getByCategory,
    getTrends,
    getReceiptReport,
  }
}
