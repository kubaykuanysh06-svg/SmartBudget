export default defineNuxtRouteMiddleware(async (to) => {
  const nuxtApp = useNuxtApp()
  const publicPaths = ['/auth/login', '/auth/register']
  const isPublic = publicPaths.includes(to.path)
  const auth = useAuth()

  if (!auth.isAuthenticated.value) {
    if (!isPublic) {
      return navigateTo('/auth/login')
    }
    return
  }

  if (!auth.user.value) {
    const profile = await auth.fetchUser()
    if (!profile) {
      if (!isPublic) {
        return nuxtApp.runWithContext(() => navigateTo('/auth/login'))
      }
      return
    }
  }

  if (isPublic) {
    return nuxtApp.runWithContext(() => navigateTo('/'))
  }
})
