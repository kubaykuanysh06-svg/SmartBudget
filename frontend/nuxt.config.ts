// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-16',
  future: {
    compatibilityVersion: 4,
  },

  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@vueuse/nuxt',
  ],

  colorMode: {
    preference: 'system',
    fallback: 'dark',
  },

  runtimeConfig: {
    apiOrigin: 'http://127.0.0.1:8000',
    public: {
      apiBaseUrl: '/api',
    },
  },

  typescript: {
    strict: true,
  },
})
