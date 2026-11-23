export const useApi = (token = useCookie<string | null>('auth_token')) => {
  const config = useRuntimeConfig()

  const fetchWithAuth = async <T>(url: string, options: any = {}): Promise<T> => {
    const headers = {
      ...(options.headers || {}),
      ...(token.value ? { Authorization: `Bearer ${token.value}` } : {}),
    }

    const fullUrl = url.startsWith('http') ? url : `${config.public.apiBaseUrl}${url.startsWith('/') ? '' : '/'}${url}`

    try {
      return await $fetch<T>(fullUrl, {
        ...options,
        headers,
      })
    } catch (err: any) {
      if (err?.response?.status === 401) {
        token.value = null
        navigateTo('/auth/login')
      }
      throw err
    }
  }

  return {
    fetch: fetchWithAuth,
  }
}
