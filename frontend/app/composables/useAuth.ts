import type { User } from '~~/shared/types'

export const useAuth = () => {
  const token = useCookie<string | null>('auth_token', {
    maxAge: 60 * 60 * 24 * 7, // 7 days
    sameSite: 'lax',
  })
  const user = useState<User | null>('auth_user', () => null)
  const api = useApi()

  const isAuthenticated = computed(() => !!token.value)

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
      user.value = null
      return null
    }
  }

  const login = async (credentials: { email: string; password: string }) => {
    const data = await api.fetch<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: credentials,
    })
    token.value = data.access_token
    await fetchUser()
    return data
  }

  const register = async (payload: { email: string; password: string; name: string; currency?: string }) => {
    const data = await api.fetch<User>('/auth/register', {
      method: 'POST',
      body: payload,
    })
    // Auto-login after registration
    await login({ email: payload.email, password: payload.password })
    return data
  }

  const logout = () => {
    token.value = null
    user.value = null
    navigateTo('/auth/login')
  }

  return {
    token,
    user,
    isAuthenticated,
    fetchUser,
    login,
    register,
    logout,
  }
}
