# Competencies Center Bot

Telegram-бот для Центра компетенций с поддержкой polling и webhook режимов.

## Что уже сделано

- Поддержка polling и webhook режимов
- Конфигурация через `.env` файл
- Современная структура с aiogram 3.x
- Логирование событий
- Интеграция с Google Sheets
- Асинхронная работа с PostgreSQL
- Система миграций Alembic
- Ролевая система доступа (USER, ADMIN)

## Структура проекта

```
competencies-center-bot/
├── .github/
│   ├── workflows/
│   │   └── tests.yml                 # CI
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md             # Шаблон Issue с багом
│   │   └── feature_request.md        # Шаблон Issue с фичей
│   └── pull_request_template.md      # Шаблон PR
├── alembic/                          # Миграции базы данных
│   ├── versions/
│   │   └── 001_initial.py            # Начальная миграция (создание таблицы users)
│   ├── env.py                        # Конфигурация Alembic для асинхронных миграций
│   └── script.py.mako                # Шаблон для генерации новых миграций
├── alembic.ini                       # Конфигурация Alembic
├── src/
│   ├── core/                         # Основные компоненты приложения
│   │   ├── config.py                 # Настройки из .env
│   │   └── database.py               # Настройки базы данных
│   ├── handlers/                     # Обработчики команд и сообщений
│   │   ├── admin/                    # Обработчики админ-команд
│   │   │   ├── broadcast.py          # Рассылка сообщений
│   │   │   └── user_management.py    # Управление пользователями
│   │   ├── courses.py                # Обработчик для курсов (FSM)
│   │   ├── sections.py               # Обработчики для разделов
│   │   └── start.py                  # Команда /start и главное меню
│   ├── keyboards/                    # Клавиатуры
│   │   ├── courses_keyboard.py       # Курсы
│   │   ├── main_menu.py              # Главное меню
│   │   └── sections_keyboard.py      # Разделы
│   ├── middlewares/                  # Промежуточное ПО
│   │   └── admin.py                  # Middleware для проверки прав админа
│   ├── models/                       # Модели данных
│   │   ├── base.py                   # Базовая модель
│   │   └── user.py                   # Модель пользователя
│   ├── repositories/                 # Репозитории для работы с данными
│   │   └── user.py                   # Репозиторий пользователей
│   ├── services/                     # Бизнес-логика
│   │   ├── broadcast.py              # Сервис рассылки
│   │   └── user_service.py           # Сервис работы с пользователями
│   ├── main.py                       # Точка входа
│   └── utils.py                      # Утилиты
├── tests/                            # Тесты
├── .env                              # Переменные окружения (создать из .env.example)
├── .env.example                      # Пример конфигурации
├── CONTRIBUTING.md                   # Руководство для разработчиков
├── requirements.txt                  # Зависимости
├── QUICKSTART.md                     # Краткое руководство для разработчиков
└── README.md
```

## Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/reclacc/competencies-center-bot.git
cd competencies-center-bot
```

2. **Создайте виртуальное окружение**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. **Установите зависимости**
```bash
pip install -r requirements.txt
```

4. **Настройте переменные окружения**
```bash
cp .env.example .env
# Отредактируйте .env
```

## Настройка базы данных

### Требования

- **PostgreSQL** версии 16.0 или выше (протестировано на 18.1)
- Создана пустая база данных для приложения

### Конфигурация в .env

```env
# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=competencies_center
DB_ECHO=false
```

### Создание и применение миграций

**Первоначальное создание БД:**

```bash
# Применить все миграции
alembic upgrade head
```

Эта команда создаст таблицу `users` с необходимыми индексами и настройками.

**Проверка статуса миграций:**

```bash
alembic current
```

**Откат последней миграции:**

```bash
alembic downgrade -1
```

**Откат всех миграций:**

```bash
alembic downgrade base
```

### Создание новой миграции

Если вы добавили новую модель или изменили существующую:

1. **Отредактируйте модель в `src/models/`**

2. **Создайте миграцию:**

```bash
alembic revision --autogenerate -m "Описание изменений"
```

3. **Проверьте сгенерированную миграцию в `alembic/versions/`**

4. **Примените миграцию:**

```bash
alembic upgrade head
```

### Структура базы данных

**Таблица: users**

| Поле | Тип | Описание |
|------|-----|---------|
| `id` | BigInteger | Первичный ключ |
| `user_id` | BigInteger | Telegram ID пользователя (уникальный) |
| `role` | String(20) | Роль: 'user' или 'admin' |
| `mailing` | Boolean | Подписка на рассылку (по умолчанию false) |
| `created_at` | DateTime | Дата создания |
| `updated_at` | DateTime | Дата последнего обновления |

**Индексы:**
- `ix_users_user_id` — для быстрого поиска по Telegram ID
- `ix_users_mailing` — для поиска подписчиков на рассылку
- `ix_users_role` — для поиска администраторов

## Настройка Google Sheets

Чтобы бот мог работать с таблицей Google Sheets, нужно выполнить следующие шаги:

1. **Создайте сервисный аккаунт Google**
2. **Включите API Google Sheets**
3. **Создайте Google Таблицу и получите её ID**
4. **Дайте сервисному аккаунту доступ к таблице**
5. **Настройте триггер Google Apps Script на "при редактировании:"**
```javascript
function onEdit(e) {
  var sheet = e.source.getActiveSheet();
  var range = e.range;
  
  var data = {
    sheet: sheet.getName(),
    cell: range.getA1Notation(),
    value: range.getValue(),
    user: Session.getActiveUser().getEmail()
  };
  
  var url = 'https://your-webhook.url/receive_edit';
  
  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(data)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
  } catch(error) {
    Logger.log('Error: ' + error);
  }
}
```

## Структура Google Sheets

Таблица должна содержать следующие листы:

### Основные листы

| Лист | Описание | Обязательные поля |
|------|----------|-------------------|
| `categories` | Категории курсов | id, name |
| `courses` | Курсы | id, name, description, category_id |
| `platforms` | Образовательные платформы | id, name, description |
| `target_groups` | Целевые группы | id, name, description |
| `events` | Мероприятия | id, title, description |
| `partners` | Партнёры | id, name, description |
| `digital_products` | Цифровые продукты | id, name, description |
| `areas` | Направления | id, name, description |

**Важно:** В каждом листе строка с `id = 0` содержит описание раздела и не отображается в списках.

## Запуск

### Требования

- Python 3.10 - 3.12 (рекомендуется 3.12)
- PostgreSQL 16+ (протестировано на 18.1)
- Выполнены миграции БД (`alembic upgrade head`)

### Режим Polling

```bash
python -m src.main
```

В `.env` должно быть:
```env
WEBHOOK_MODE=false
```

### Режим Webhook

1. **Настройте .env**
```env
WEBHOOK_MODE=true
WEBHOOK_URL=https://your-webhook.url
APP_PORT=8080
```

2. **Запустите бота**
```bash
python -m src.main
```

Бот автоматически установит вебхук по адресу: `https://your-webhook.url/webhook`

## Конфигурация

Все настройки находятся в `.env` файле:

### Telegram

| Параметр | Описание | Обязательный |
|----------|---------|-------------|
| `BOT_TOKEN` | Токен от @BotFather | ✅ Да |
| `ADMINS` | ID администраторов через запятую | ✅ Да |

### База данных

| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| `DB_USER` | Пользователь PostgreSQL | ✅ Обязательный |
| `DB_PASSWORD` | Пароль БД | ✅ Обязательный |
| `DB_HOST` | Хост БД | ✅ Обязательный |
| `DB_PORT` | Порт БД | 5432 |
| `DB_NAME` | Имя БД | ✅ Обязательный |
| `DB_ECHO` | Вывод SQL запросов в логи | false |

### Google Sheets

| Параметр | Описание | Обязательный |
|----------|---------|-------------|
| `SHEET_ID` | ID Google Sheets таблицы | ✅ Да |
| `GOOGLE_CREDENTIALS_FILE` | Путь к credentials.json | credentials.json |

### Webhook

| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| `WEBHOOK_MODE` | Режим работы (true/false) | false |
| `WEBHOOK_URL` | URL для вебхука | - |
| `WEBHOOK_PATH` | Путь для вебхука Telegram | `/webhook` |
| `GOOGLE_WEBHOOK_PATH` | Путь для вебхука Google Sheets | `/receive_edit` |
| `APP_HOST` | Хост сервера | `0.0.0.0` |
| `APP_PORT` | Порт сервера | 8080 |

## Отладка

Логи выводятся в консоль. Для более детальной отладки измените уровень логирования в `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Проверка подключения к БД

```bash
python -c "
import asyncio
from src.core.database import db_helper
from sqlalchemy import text

async def check():
    async with db_helper.engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('✅ БД работает:', result.scalar())

asyncio.run(check())
"
```

## Требования к запуску

- **Python:** версия 3.10 - 3.12 (рекомендуется 3.12)
- **PostgreSQL:** версия 16 и выше (рекомендуется 18.1)
- Все зависимости и версии указаны в файле `requirements.txt`

## Контакты

При возникновении вопросов создайте Issue в репозитории.