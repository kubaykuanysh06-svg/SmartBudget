# 💰 SmartBudget

> Интеллектуальное веб-приложение для ведения личного бюджета, анализа цен, поиска скидок и подсказок с ИИ.

## 🚀 Стек технологий

- **Backend**: FastAPI 0.115+, Python 3.12, Async SQLAlchemy 2.0, asyncpg, Alembic, Pydantic v2
- **Frontend**: Nuxt 3 в режиме совместимости с Nuxt 4 (Vue 3, Composition API, SSR/SSG), Nuxt UI, Tailwind CSS, Pinia
- **Database & Cache**: PostgreSQL 16, Redis 7 (ARQ background tasks)
- **AI**: Google Gemini API (категоризация, проверка цен, персональный коучинг)
- **Deployment**: Docker, Docker Compose

---

## 🌟 Ключевые возможности

1. **Учёт расходов и доходов**:
   - Быстрое добавление покупок с суммами, магазинами, тегами и категориями
   - Иерархические категории трат и доходов
2. **Лимиты и Бюджеты**:
   - Установка лимитов на месяц / неделю / год
   - Индикаторы расхода бюджета (зелёный/жёлтый/красный статус)
3. **ИИ-помощник (Gemini)**:
   - **Автокатегоризация**: определение категории по описанию чека и магазину
   - **Анализ цен**: проверка, выгодна ли покупка товара перед сделкой
   - **Финансовый коуч**: персональные советы и ответы на вопросы по оптимизации расходов
4. **Скидки и выгодные траты**:
   - Лента акций и скидок в магазинах
   - Персональные предложения на основе ваших частых трат
5. **Аналитика**:
   - Структура расходов по категориям
   - Тренды трат по месяцам
   - Норма сбережений и чистая экономия

---

## 📂 Структура проекта

```text
smartbudget/
├── backend/                  # FastAPI сервис
│   ├── alembic/              # Миграции базы данных
│   ├── src/
│   │   ├── ai/               # Модуль Gemini AI (промпты, анализ цен, коуч)
│   │   ├── analytics/        # Агрегация аналитики и графиков
│   │   ├── auth/             # JWT аутентификация и пользователи
│   │   ├── budgets/          # Управление лимитами бюджетов
│   │   ├── categories/       # Дерево категорий расходов/доходов
│   │   ├── core/             # Конфигурация, async DB engine, безопасность
│   │   ├── deals/            # Скидки, предложения, история цен
│   │   ├── transactions/     # Транзакции, фильтры, репозиторий
│   │   ├── worker.py         # Фоновые задачи ARQ (проверка скидок)
│   │   └── main.py           # Точка входа FastAPI
│   ├── Dockerfile
│   └── pyproject.toml
│
├── frontend/                 # Nuxt 4 приложение
│   ├── app/                  # Исходный код приложения Nuxt 4
│   │   ├── assets/           # Стили Tailwind
│   │   ├── composables/      # useAuth, useTransactions, useBudgets, useAiInsights...
│   │   ├── layouts/          # default.vue (с боковым меню), auth.vue
│   │   └── pages/            # Дашборд, транзакции, бюджеты, скидки, ИИ, настройки
│   ├── shared/types/         # TypeScript интерфейсы
│   ├── nuxt.config.ts        # Конфигурация Nuxt 4 (compatibilityVersion: 4)
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml        # Оркестрация Postgres, Redis, Backend, Frontend, Worker
└── README.md
```

---

## Быстрый старт с Docker на Windows

Запустите Docker Desktop и дождитесь запуска движка. Выполните команды из
корня репозитория в PowerShell. Node.js и Python входят в образы контейнеров.

```powershell
if (!(Test-Path backend/.env)) {
    Copy-Item backend/.env.example backend/.env
    $bytes = New-Object byte[] 48
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $rng.GetBytes($bytes) } finally { $rng.Dispose() }
    $secret = [Convert]::ToBase64String($bytes)
    (Get-Content backend/.env) -replace '^SECRET_KEY=.*', "SECRET_KEY=$secret" |
        Set-Content -Encoding utf8 backend/.env
}
docker compose up --build -d --wait
docker compose ps
```

- Веб-приложение: http://localhost:3001
- Документация API: http://localhost:8000/docs
- Проверка API: http://localhost:8000/health

Если порт 3001 занят, задайте другой перед запуском, например
`$env:SMARTBUDGET_FRONTEND_PORT = '3002'`. Интерфейс обращается к API через
тот же адрес, поэтому отдельная настройка API в браузере не нужна.

Миграции PostgreSQL выполняются при старте API. Текущую версию можно проверить
командой `docker compose exec backend alembic current`. Данные PostgreSQL
хранятся в томе Compose и сохраняются при остановке или пересборке контейнеров.

Для раздела «ИИ Ассистент» добавьте свой `GEMINI_API_KEY` в локальный файл
`backend/.env` и обновите контейнеры командой `docker compose up -d`. По умолчанию
используется `gemini-3.5-flash-lite`. Регистрация, операции, бюджеты и статистика
доступны без ключа Gemini.

## Сценарий демонстрации

1. Создайте отдельную учётную запись. Для новых аккаунтов интерфейса используется тенге.
2. В разделе «Транзакции» добавьте доход 50 000 ₸ и расход 8 000 ₸, выбрав
   категории для обеих операций.
3. Откройте дашборд. Баланс за месяц должен увеличиться на 42 000 ₸.
   Обновите страницу и убедитесь, что обе операции сохранились.
4. На вкладке «Бюджеты» создайте общий лимит 20 000 ₸. Расход 8 000 ₸
   составляет 40% лимита. В «Аналитике» этот расход отобразится в выбранной категории.

## Автотесты и проверка миграций

Для запуска миграций (up/down/up + `alembic check`) и интеграционных тестов API на изолированной временной базе PostgreSQL (без затрагивания рабочих данных):

```powershell
docker compose -p smartbudget_test -f docker-compose.test.yml run --rm --build tests
docker compose -p smartbudget_test -f docker-compose.test.yml down -v
```
