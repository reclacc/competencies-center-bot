# Competencies Center Bot

Telegram-бот для Центра компетенций с поддержкой polling и webhook режимов.

## Что уже сделано

- Поддержка polling и webhook режимов
- Конфигурация через `.env` файл
- Современная структура с aiogram 3.x
- Логирование событий
- Готовность к интеграции с Google Sheets

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
├── src/
│   ├── handlers/                     # Обработчики команд и сообщений
│   │   ├── __init__.py
│   │   └── start.py                  # Команда /start и главное меню
│   ├── keyboards/                    # Клавиатуры
│   │   ├── __init__.py
│   │   └── main_menu.py              # Главное меню
│   ├── config.py                     # Настройки из .env
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
# Отредактируйте .env и добавьте BOT_TOKEN
```

## Запуск

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

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `BOT_TOKEN` | Токен от @BotFather | *обязательный* |
| `WEBHOOK_MODE` | Режим работы (true/false) | `false` |
| `WEBHOOK_URL` | URL для вебхука | - |
| `WEBHOOK_PATH` | Путь для вебхука | `/webhook` |
| `APP_HOST` | Хост сервера | `0.0.0.0` |
| `APP_PORT` | Порт сервера | `8080` |

## Отладка

Логи выводятся в консоль. Для более детальной отладки измените уровень логирования в `main.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Требования к запуску

- Весь код тестируется на Python версии 3.10 - 3.12, настоятельно рекомендуется запускать на 3.12.
- Все зависимости и версии указаны в файле `requirements.txt`

## Контакты

При возникновении вопросов создайте Issue в репозитории.