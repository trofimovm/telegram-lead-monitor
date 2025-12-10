# Telegram Lead Monitor

SaaS-платформа для мониторинга Telegram-каналов с LLM-анализом сообщений для поиска релевантных лидов.

## 🎯 Возможности

- **Telegram Мониторинг**: Подключение аккаунтов Telegram и мониторинг каналов/групп в реальном времени
- **LLM Анализ**: Автоматический анализ сообщений с помощью LLM для поиска релевантных лидов
- **Умные Правила**: Создание гибких правил мониторинга с настраиваемыми промптами для LLM
- **Управление Лидами**: Полнофункциональная CRM для работы с найденными лидами
- **Аналитика**: Детальная аналитика по источникам, правилам, конверсии и трендам
- **Уведомления**: Email-уведомления о новых лидах с настраиваемыми триггерами
- **Экспорт Данных**: Экспорт лидов в CSV формат

## Технологический стек

**Backend:**
- FastAPI (Python 3.10+)
- PostgreSQL + Redis
- Telethon (Telegram MTProto)
- SQLAlchemy + Alembic
- APScheduler (background tasks)
- pytest (testing)

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React Hooks & Context API

**LLM:**
- llm.codenrock.com (LiteLLM Proxy)
- Поддержка gpt-5-mini, gpt-4o, Claude, Gemini
- См. [LLM_MODELS.md](./LLM_MODELS.md) для деталей

## Быстрый старт

### Предварительные требования

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

### Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repo-url>
cd telegram-lead-monitor
```

2. **Настройте environment variables:**
```bash
# Backend
cp backend/.env.example backend/.env
# Отредактируйте backend/.env и заполните необходимые значения

# Frontend
cp frontend/.env.local.example frontend/.env.local
# Отредактируйте frontend/.env.local
```

3. **Запустите Docker сервисы (PostgreSQL + Redis):**
```bash
docker-compose up -d
```

4. **Установите зависимости Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. **Примените миграции базы данных:**
```bash
alembic upgrade head
```

6. **Установите зависимости Frontend:**
```bash
cd ../frontend
npm install
```

### Запуск проекта

В **двух отдельных терминалах** выполните:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend будет доступен на http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend будет доступен на http://localhost:3000

## 🐳 Docker Development

Проект полностью поддерживает Docker для локальной разработки с hot reload.

### Быстрый старт с Docker

```bash
# 1. Клонируйте репозиторий
git clone <repo-url>
cd telegram-lead-monitor

# 2. Создайте environment файлы
make setup

# 3. Отредактируйте backend/.env с вашими credentials
# - TELEGRAM_API_ID
# - TELEGRAM_API_HASH
# - LLM_API_KEY

# 4. Запустите все сервисы
make docker-up
```

После запуска приложение будет доступно:
- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

### Основные Docker команды

```bash
# Управление
make docker-up      # Запустить все сервисы
make docker-down    # Остановить все сервисы
make docker-build   # Собрать Docker образы

# Просмотр логов
make docker-logs    # Все сервисы
make backend        # Backend логи
make frontend       # Frontend логи
make worker         # Worker логи

# Разработка
make migrate        # Применить миграции БД
make test           # Запустить тесты
make health-check   # Проверить здоровье сервисов

# Доступ к контейнерам
make shell-backend  # Bash в backend контейнере
make shell-frontend # Shell в frontend контейнере

# Очистка
make clean          # Удалить все контейнеры и volumes
```

### Hot Reload

Все компоненты поддерживают hot reload:

- **Backend**: Изменения в `backend/app/` → автоматический перезапуск Uvicorn
- **Frontend**: Изменения в `frontend/` → hot module replacement
- **Worker**: Изменения в `backend/app/` → требуется `docker-compose restart worker`

### Архитектура Docker

Проект использует 5 Docker сервисов:

1. **postgres** - PostgreSQL 15 база данных
2. **redis** - Redis 7 кеш
3. **backend** - FastAPI REST API (порт 8000)
4. **worker** - Message Collector Worker (фоновая задача)
5. **frontend** - Next.js веб-интерфейс (порт 3000)

Подробнее: [DOCKER.md](./DOCKER.md)

## 📚 Документация

### API Documentation

После запуска backend, автоматическая документация API доступна:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Регистрация нового пользователя
- `POST /api/v1/auth/login` - Вход в систему
- `GET /api/v1/auth/me` - Получить текущего пользователя

#### Telegram Accounts
- `GET /api/v1/telegram/accounts` - Список аккаунтов
- `POST /api/v1/telegram/accounts` - Добавить аккаунт
- `POST /api/v1/telegram/accounts/{id}/send-code` - Отправить код авторизации
- `POST /api/v1/telegram/accounts/{id}/verify` - Подтвердить аккаунт кодом

#### Sources (Каналы/Группы)
- `GET /api/v1/telegram/sources` - Список источников
- `POST /api/v1/telegram/sources` - Добавить источник
- `PATCH /api/v1/telegram/sources/{id}` - Обновить источник
- `DELETE /api/v1/telegram/sources/{id}` - Удалить источник
- `POST /api/v1/telegram/sync-dialogs` - Синхронизация доступных диалогов

#### Rules (Правила мониторинга)
- `GET /api/v1/rules` - Список правил
- `POST /api/v1/rules` - Создать правило
- `GET /api/v1/rules/{id}` - Получить правило
- `PATCH /api/v1/rules/{id}` - Обновить правило
- `DELETE /api/v1/rules/{id}` - Удалить правило

#### Leads (Лиды)
- `GET /api/v1/leads` - Список лидов (с фильтрами)
- `GET /api/v1/leads/{id}` - Получить лид
- `PATCH /api/v1/leads/{id}` - Обновить лид (статус, notes, assignee)
- `DELETE /api/v1/leads/{id}` - Удалить лид
- `GET /api/v1/leads/stats` - Статистика по лидам
- `GET /api/v1/leads/export/csv` - Экспорт в CSV

#### Analytics
- `GET /api/v1/analytics/summary` - Общая аналитика
- `GET /api/v1/analytics/leads-time-series` - Временной ряд создания лидов
- `GET /api/v1/analytics/conversion-funnel` - Воронка конверсии
- `GET /api/v1/analytics/source-performance` - Производительность источников
- `GET /api/v1/analytics/rule-performance` - Эффективность правил
- `GET /api/v1/analytics/activity-trends` - Тренды активности

#### Notifications
- `GET /api/v1/notifications/settings` - Настройки уведомлений
- `PATCH /api/v1/notifications/settings` - Обновить настройки

## 🗂️ Структура проекта

```
telegram-lead-monitor/
├── backend/                   # FastAPI Backend
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── tenant.py
│   │   │   ├── telegram_account.py
│   │   │   ├── source.py
│   │   │   ├── message.py
│   │   │   ├── rule.py
│   │   │   └── lead.py
│   │   ├── schemas/          # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── telegram.py
│   │   │   ├── rules.py
│   │   │   ├── leads.py
│   │   │   ├── analytics.py
│   │   │   └── notifications.py
│   │   ├── api/v1/           # API routes
│   │   │   ├── auth.py
│   │   │   ├── telegram.py
│   │   │   ├── sources.py
│   │   │   ├── rules.py
│   │   │   ├── leads.py
│   │   │   ├── analytics.py
│   │   │   ├── notifications.py
│   │   │   └── users.py
│   │   ├── services/         # Business logic
│   │   │   ├── llm_service.py
│   │   │   └── notification_service.py
│   │   ├── telegram_connector/ # Telegram MTProto
│   │   │   ├── client_manager.py
│   │   │   └── message_processor.py
│   │   ├── workers/          # Background tasks
│   │   │   └── message_worker.py
│   │   ├── core/             # Core utilities
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── encryption.py
│   │   ├── db/               # Database
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── tests/                # Pytest tests
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_leads.py
│   │   └── test_analytics.py
│   ├── pytest.ini
│   └── requirements.txt
│
├── frontend/                 # Next.js Frontend
│   ├── app/                  # App Router pages
│   │   ├── dashboard/
│   │   │   ├── page.tsx             # Dashboard
│   │   │   ├── telegram-accounts/   # Telegram аккаунты
│   │   │   ├── sources/             # Источники
│   │   │   ├── rules/               # Правила
│   │   │   ├── leads/               # Лиды
│   │   │   ├── analytics/           # Аналитика
│   │   │   └── settings/            # Настройки
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── register/
│   │   └── layout.tsx
│   ├── components/           # React components
│   │   ├── auth/
│   │   ├── layouts/
│   │   ├── ui/
│   │   └── charts/
│   ├── lib/                  # Utilities
│   │   ├── api/              # API clients
│   │   ├── contexts/         # React contexts
│   │   └── utils/
│   └── package.json
│
├── docker-compose.yml        # PostgreSQL + Redis
└── README.md
```

## 🔧 Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://telegram_monitor:dev_password@localhost:5432/telegram_monitor

# JWT Authentication
SECRET_KEY=your-secret-key-min-32-chars-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram API (получить на https://my.telegram.org)
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Encryption (генерировать: from cryptography.fernet import Fernet; print(Fernet.generate_key()))
ENCRYPTION_KEY=your-fernet-encryption-key

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM API (LiteLLM Proxy)
LLM_API_URL=https://llm.codenrock.com
LLM_API_KEY=your-llm-api-key
LLM_MODEL=gpt-5-mini

# Email Notifications (опционально, для Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Telegram Lead Monitor

# Application
APP_NAME=Telegram Lead Monitor
ENVIRONMENT=development
DEBUG=True
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Тестирование

### Запуск тестов Backend

```bash
cd backend
source venv/bin/activate
pytest
```

### Запуск тестов с покрытием

```bash
pytest --cov=app --cov-report=html
```

Отчет о покрытии будет доступен в `htmlcov/index.html`

### Тестовые endpoints

Основные тесты покрывают:
- ✅ Authentication (регистрация, логин, JWT)
- ✅ Leads API (CRUD, фильтры, экспорт)
- ✅ Analytics API (все endpoints)

## 📊 Database Migrations

### Создать новую миграцию

```bash
cd backend
source venv/bin/activate
alembic revision --autogenerate -m "описание изменений"
```

### Применить миграции

```bash
alembic upgrade head
```

### Откатить миграцию

```bash
alembic downgrade -1
```

### История миграций

```bash
alembic history
```

## 🐳 Docker Services

### PostgreSQL
- **Port**: 5432
- **User**: telegram_monitor
- **Password**: dev_password
- **Database**: telegram_monitor

### Redis
- **Port**: 6379
- **Database**: 0

### Управление контейнерами

```bash
# Запустить
docker-compose up -d

# Остановить
docker-compose down

# Просмотр логов
docker-compose logs -f

# Перезапустить
docker-compose restart
```

## 🚀 Deployment

См. подробное руководство в [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📈 Этапы разработки (MVP)

- [x] **Stage 1**: Инфраструктура ✅
- [x] **Stage 2**: Backend Auth ✅
- [x] **Stage 3**: Frontend Auth ✅
- [x] **Stage 4**: Telegram Integration ✅
- [x] **Stage 5**: LLM Integration & Rules Engine ✅
- [x] **Stage 6**: Frontend для Rules & Leads ✅
- [x] **Stage 7**: Уведомления ✅
- [x] **Stage 8**: Analytics & Dashboard ✅
- [x] **Stage 9**: Testing & Documentation ✅

**Статус**: MVP завершен! 🎉

## 🔒 Безопасность

- JWT токены для аутентификации
- Bcrypt хеширование паролей
- Fernet шифрование токенов Telegram
- SQL Injection защита (SQLAlchemy ORM)
- CORS настройки
- Rate limiting (можно добавить)

## 🤝 Contributing

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📝 Roadmap

### После MVP (Этап 2)
- [ ] Telegram Bot уведомления
- [ ] TGStat API интеграция для поиска каналов
- [ ] OAuth (Google, GitHub)
- [ ] Billing & Subscriptions (Stripe)
- [ ] Teams & управление ролями
- [ ] Webhooks для интеграции с CRM
- [ ] Mobile приложение

## 📄 Лицензия

Proprietary

## 📧 Контакты

Для вопросов и предложений: [ваш email]

---

**Сделано с ❤️ для автоматизации поиска лидов в Telegram**
