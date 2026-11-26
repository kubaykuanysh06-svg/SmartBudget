<template>
  <div class="min-h-screen grid grid-cols-1 md:grid-cols-12 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
    <!-- Left Brand Showcase (Desktop) -->
    <div class="hidden md:flex md:col-span-6 xl:col-span-7 relative overflow-hidden bg-slate-950 text-white p-8 lg:p-12 flex-col justify-between border-r border-slate-800/80">
      <!-- Ambient gradient orbs -->
      <div class="pointer-events-none absolute -top-28 -left-28 w-96 h-96 rounded-full bg-emerald-500/25 blur-3xl" />
      <div class="pointer-events-none absolute bottom-0 right-0 w-[28rem] h-[28rem] rounded-full bg-teal-500/15 blur-3xl" />

      <!-- Brand header -->
      <div class="relative z-10 flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-2xl bg-gradient-to-br from-emerald-400 via-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-500/25 ring-1 ring-white/20">
          <UIcon name="i-heroicons-chart-bar-square" class="w-6 h-6 text-white" />
        </div>
        <div>
          <span class="text-xl font-extrabold tracking-tight text-white">SmartBudget</span>
          <span class="ml-2 text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30">
            Fintech AI
          </span>
        </div>
      </div>

      <!-- Center Fintech Showcase -->
      <div class="relative z-10 max-w-xl space-y-8 my-auto py-8">
        <div class="space-y-4">
          <h1 class="text-4xl xl:text-5xl font-extrabold tracking-tight leading-[1.12]">
            Қаржыңызды <span class="bg-gradient-to-r from-emerald-300 via-teal-200 to-cyan-300 bg-clip-text text-transparent">нақты дерекпен</span> басқарыңыз
          </h1>
          <p class="text-base text-slate-400 leading-relaxed">
            Күнделікті кіріс-шығысты бір сәтте тіркеңіз, айлық лимиттерді бақылаңыз және Google Gemini негізіндегі қаржы кеңесшісімен артық шығынды қысқартыңыз.
          </p>
        </div>

        <!-- Preview Glass Card -->
        <div class="rounded-2xl bg-white/[0.04] backdrop-blur-md ring-1 ring-white/10 p-6 space-y-5 shadow-2xl">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs uppercase tracking-wider text-slate-400 font-medium">Айлық таза қалдық</p>
              <p class="text-3xl font-bold tabular-nums text-white mt-1">+420 000 ₸</p>
            </div>
            <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-400/30">
              <UIcon name="i-heroicons-arrow-trending-up" class="w-4 h-4" />
              84% жинақ нормасы
            </span>
          </div>

          <div class="space-y-2">
            <div class="flex justify-between text-xs text-slate-300">
              <span>Айлық бюджет орындалуы</span>
              <span class="tabular-nums text-emerald-300 font-semibold">80 000 ₸ / 200 000 ₸ (40%)</span>
            </div>
            <div class="h-2 rounded-full bg-slate-800 overflow-hidden">
              <div class="h-full w-2/5 rounded-full bg-gradient-to-r from-emerald-400 to-teal-400" />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3 pt-1">
            <div class="rounded-xl bg-white/[0.04] p-3 ring-1 ring-white/5">
              <p class="text-[11px] text-slate-400">Аналитика</p>
              <p class="text-xs font-semibold text-slate-200 mt-0.5">Нақты графиктер</p>
            </div>
            <div class="rounded-xl bg-white/[0.04] p-3 ring-1 ring-white/5">
              <p class="text-[11px] text-slate-400">Бюджет</p>
              <p class="text-xs font-semibold text-slate-200 mt-0.5">Ақылды лимиттер</p>
            </div>
            <div class="rounded-xl bg-white/[0.04] p-3 ring-1 ring-white/5">
              <p class="text-[11px] text-slate-400">Gemini AI</p>
              <p class="text-xs font-semibold text-slate-200 mt-0.5">Жеке кеңесші</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="relative z-10 flex items-center justify-between text-xs text-slate-500">
        <span>© {{ new Date().getFullYear() }} SmartBudget</span>
        <span>Қауіпсіз JWT шифрлау • Дербес деректер оқшаулауы</span>
      </div>
    </div>

    <!-- Right Auth Form Panel -->
    <div class="md:col-span-6 xl:col-span-5 flex flex-col justify-between p-6 sm:p-10">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5 md:invisible">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white shadow-md">
            <UIcon name="i-heroicons-chart-bar-square" class="w-5 h-5" />
          </div>
          <span class="text-lg font-extrabold tracking-tight">SmartBudget</span>
        </div>
        <ClientOnly>
          <UColorModeButton />
        </ClientOnly>
      </div>

      <div class="w-full max-w-md mx-auto my-auto py-8">
        <div class="bg-white dark:bg-slate-900/90 p-7 sm:p-9 rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-none ring-1 ring-slate-200/80 dark:ring-slate-800">
          <slot />
        </div>
      </div>

      <div class="text-center text-xs text-slate-400 md:hidden">
        SmartBudget — жеке қаржы мен бюджетті басқару жүйесі
      </div>
    </div>
  </div>
</template>
