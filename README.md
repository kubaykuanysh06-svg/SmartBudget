# 💰 SmartBudget

> Интеллектуальное веб-приложение для ведения личного бюджета, анализа цен, поиска скидок и подсказок с ИИ.

## 🚀 Стек технологий

- **Backend**: FastAPI 0.115+, Python 3.12, Async SQLAlchemy 2.0, asyncpg, Alembic, Pydantic v2
- **Frontend**: Nuxt 4 (Vue 3, Composition API, SSR/SSG), Nuxt UI, Tailwind CSS, Pinia
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

## 🛠️ Быстрый старт с Docker

```bash
# 1. Склонируйте репозиторий
git clone https://github.com/kubaykuanysh06-svg/SmartBudget.git
cd SmartBudget

# 2. Настройте .env для backend
cp backend/.env.example backend/.env
# Укажите ваш GEMINI_API_KEY и SECRET_KEY в backend/.env

# 3. Запустите все сервисы
docker-compose up --build
```

- **Frontend**: http://localhost:3000
- **FastAPI Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 💻 Локальная разработка

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # на Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Откройте браузер по адресу http://localhost:3000.
