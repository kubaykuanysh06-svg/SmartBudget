// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-16',
  future: {
    compatibilityVersion: 4,
  },

  css: ['~/assets/css/main.css'],

  app: {
    head: {
      title: 'SmartBudget — Ақылды жеке қаржы жүйесі',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Шығыстар мен кірістерді есептеу, бюджет лимиттері және ЖИ қаржы кеңесшісі',
        },
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap',
        },
      ],
    },
  },

  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@vueuse/nuxt',
  ],

  colorMode: {
    preference: 'light',
    fallback: 'light',
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
