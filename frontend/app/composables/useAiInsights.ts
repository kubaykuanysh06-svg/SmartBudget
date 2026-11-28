import type { AiInsight, ImageAnalysis, PriceAnalysis } from '~~/shared/types'

export const useAiInsights = () => {
  const api = useApi()
  const insights = useState<AiInsight[]>('ai_insights', () => [])
  const loading = ref(false)

  const fetchInsights = async () => {
    loading.value = true
    try {
      const data = await api.fetch<AiInsight[]>('/ai/insights')
      insights.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const sendChatMessage = async (message: string) => {
    return await api.fetch<{ reply: string }>('/ai/chat', {
      method: 'POST',
      body: { message },
    })
  }

  const analyzeImage = async (image: File, message: string) => {
    const body = new FormData()
    body.set('image', image)
    if (message) body.set('message', message)
    return await api.fetch<ImageAnalysis>('/ai/analyze-image', { method: 'POST', body })
  }

  const analyzePrice = async (item: { description: string; merchant?: string; amount: number }) => {
    return await api.fetch<PriceAnalysis>('/ai/analyze-price', {
      method: 'POST',
      body: item,
    })
  }

  return {
    insights,
    loading,
    fetchInsights,
    sendChatMessage,
    analyzeImage,
    analyzePrice,
  }
}
