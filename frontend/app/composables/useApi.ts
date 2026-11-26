const SESSION_COOKIE_OPTIONS = {
  maxAge: 60 * 60 * 24 * 7, // matches REFRESH_TOKEN_EXPIRE_DAYS on the backend
  sameSite: 'lax' as const,
}

export const useAuthCookies = () => ({
  token: useCookie<string | null>('auth_token', SESSION_COOKIE_OPTIONS),
  refreshToken: useCookie<string | null>('refresh_token', SESSION_COOKIE_OPTIONS),
})

type TokenPair = { access_token: string; refresh_token: string }

// Client-only: lets parallel requests that all got 401 share one refresh call.
// Never shared on the server, where module state is common to all users.
let clientRefresh: Promise<TokenPair> | null = null

export const useApi = (token = useAuthCookies().token) => {
  const config = useRuntimeConfig()
  const { refreshToken } = useAuthCookies()

  const toUrl = (url: string) =>
    url.startsWith('http') ? url : `${config.public.apiBaseUrl}${url.startsWith('/') ? '' : '/'}${url}`

  const request = <T>(url: string, options: any) =>
    $fetch<T>(toUrl(url), {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
      },
    })

  const refreshSession = async (): Promise<boolean> => {
    const current = refreshToken.value
    if (!current) return false
    try {
      const call = () =>
        $fetch<TokenPair>(toUrl('/auth/refresh'), {
          method: 'POST',
          body: { refresh_token: current },
        })
      let pair: TokenPair
      if (import.meta.client) {
        clientRefresh ??= call().finally(() => { clientRefresh = null })
        pair = await clientRefresh
      } else {
        pair = await call()
      }
      token.value = pair.access_token
      refreshToken.value = pair.refresh_token
      return true
    } catch {
      return false
    }
  }

  const fetchWithAuth = async <T>(url: string, options: any = {}): Promise<T> => {
    try {
      return await request<T>(url, options)
    } catch (err: any) {
      const status = err?.statusCode ?? err?.status ?? err?.response?.status
      if (status !== 401 || url.includes('/auth/login') || url.includes('/auth/refresh')) {
        throw err
      }
      // The access token lives 30 minutes; renew it once with the refresh token.
      if (await refreshSession()) {
        return await request<T>(url, options)
      }
      token.value = null
      refreshToken.value = null
      if (import.meta.client) {
        navigateTo('/auth/login')
      }
      throw err
    }
  }

  return {
    fetch: fetchWithAuth,
  }
}
