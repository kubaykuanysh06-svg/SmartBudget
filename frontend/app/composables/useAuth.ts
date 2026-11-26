import type { AiInsight, BudgetStatus, Deal, Transaction, User } from '~~/shared/types'

export const useAuth = () => {
  const { token, refreshToken } = useAuthCookies()
  const user = useState<User | null>('auth_user', () => null)
  const txnsState = useState<Transaction[]>('transactions', () => [])
  const budgetsState = useState<BudgetStatus[]>('budgets_status', () => [])
  const insightsState = useState<AiInsight[]>('ai_insights', () => [])
  const dealsState = useState<Deal[]>('deals_list', () => [])
  const personalizedDealsState = useState<Deal[]>('deals_personalized', () => [])
  const api = useApi(token)

  const isAuthenticated = computed(() => !!token.value)

  const clearCachedUserData = () => {
    txnsState.value = []
    budgetsState.value = []
    insightsState.value = []
    dealsState.value = []
    personalizedDealsState.value = []
  }

  const fetchUser = async () => {
    if (!token.value) {
      user.value = null
      return null
    }
    try {
      const data = await api.fetch<User>('/auth/me')
      user.value = data
      return data
    } catch {
      token.value = null
      refreshToken.value = null
      user.value = null
      clearCachedUserData()
      return null
    }
  }

  const login = async (credentials: { email: string; password: string }) => {
    clearCachedUserData()
    const data = await api.fetch<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: credentials,
    })
    token.value = data.access_token
    refreshToken.value = data.refresh_token
    await fetchUser()
    return data
  }

  const register = async (payload: { email: string; password: string; name: string; currency?: string }) => {
    clearCachedUserData()
    const data = await api.fetch<User>('/auth/register', {
      method: 'POST',
      body: payload,
    })
    // Auto-login after registration
    await login({ email: payload.email, password: payload.password })
    return data
  }

  const updateProfile = async (payload: { name?: string; currency?: string }) => {
    const data = await api.fetch<User>('/auth/me', {
      method: 'PATCH',
      body: payload,
    })
    user.value = data
    return data
  }

  const logout = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
    clearCachedUserData()
    navigateTo('/auth/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    fetchUser,
    login,
    register,
    updateProfile,
    logout,
  }
}
