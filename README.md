# Competencies Center Bot

Telegram-бот для Центра компетенций с поддержкой polling и webhook режимов.

## Что уже сделано

- Поддержка polling и webhook режимов
- Конфигурация через `.env` файл
- Современная структура с aiogram 3.x
- Логирование событий
- Интеграция с Google Sheets

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
│   │   ├── start.py                  # Команда /start и главное меню
│   │   ├── courses.py                # Обработчик для курсов (FSM)
│   │   └── sections.py               # Обработчики для разделов (мероприятия, партнёры и пр.)
│   ├── keyboards/                    # Клавиатуры
│   │   ├── __init__.py
│   │   ├── courses_keyboard.py       # Курсы
│   │   ├── main_menu.py              # Главное меню
│   │   └── sections_keyboard.py      # Разделы
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
# Отредактируйте .env
```

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
| `SHEET_ID` | ID Google Sheets таблицы | - |
| `GOOGLE_CREDENTIALS_FILE` | Путь к credentials.json | credentials.json |
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