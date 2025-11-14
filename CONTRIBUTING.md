# Руководство для разработчиков

Добро пожаловать! Это руководство поможет вам внести вклад в разработку бота Центра компетенций.

## Содержание

- [Подготовка к работе](#подготовка-к-работе)
- [Шаги разработки](#шаги-разработки)
- [Стандарты кода](#стандарты-кода)
- [Тестирование](#тестирование)
- [Git Flow](#git-flow)
- [Pull Request процесс](#pull-request-процесс)
- [Code Review](#code-review)
- [FAQ](#faq)

---

## Подготовка к работе

### 1. Клонирование репозитория

```bash
git clone https://github.com/reclacc/competencies-center-bot.git
cd competencies-center-bot
```

### 2. Установка зависимостей

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте его
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Обновите pip (опционально)
pip install --upgrade pip
```

### 3. Настройка окружения

```bash
# Создайте .env файл
cp .env.example .env

# Отредактируйте .env и добавьте токен бота
nano .env  # или любой другой редактор
```

Пример `.env`:
```env
# Токен бота
BOT_TOKEN=12345

# Database
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_ECHO=true

# Режим работы: false = polling, true = webhook
WEBHOOK_MODE=true

# URL вебхука (только для WEBHOOK_MODE=true)
# Например, для tuna: https://my-subdomain.tuna.am
WEBHOOK_URL=https://my-subdomain.tuna.am

# Путь для вебхука (по умолчанию /webhook)
WEBHOOK_PATH=/webhook

# Настройки сервера (для вебхука)
APP_HOST=0.0.0.0
APP_PORT=8080

# Для гугл таблиц
GOOGLE_CREDENTIALS_FILE=credentials.json
SHEET_ID=abcd1234
GOOGLE_WEBHOOK_PATH=/receive_edit

# Статическое поле
SCOPES=["https://www.googleapis.com/auth/spreadsheets"]
```

### 4. Проверка установки

```bash
# Запустите тесты
pytest

# Если все тесты прошли - вы готовы к работе!
```

---

## Шаги разработки

### Шаг 1: Синхронизация с репозиторием

**Перед началом работы всегда синхронизируйтесь:**

```bash
# Переключитесь на main ветку
git checkout main

# Получите последние изменения из main
git pull origin main

# Переключитесь на develop ветку
git checkout develop

# Её изменения тоже захватите
git pull origin develop
```

### Шаг 2: Создание новой ветки

**Типы веток:**

- `feature/название-фичи` - новая функциональность
- `fix/описание-бага` - исправление бага
- `refactor/что-рефакторим` - рефакторинг кода
- `docs/что-документируем` - обновление документации
- `test/что-тестируем` - добавление/улучшение тестов

**Примеры:**

```bash
# Новая функциональность
git checkout -b feature/google-sheets-integration

# Исправление бага
git checkout -b fix/webhook-error-handling

# Рефакторинг
git checkout -b refactor/handlers-structure

# Документация
git checkout -b docs/api-documentation

# Тесты
git checkout -b test/keyboard-handlers
```

### Шаг 3: Разработка

Вносите изменения в код, следуя [стандартам кода](#стандарты-кода).

**Полезные команды для разработки:**

```bash
# Запуск бота
python -m src.main

# Запуск тестов в watch режиме (автоматический перезапуск)
make test-watch

# Проверка кода во время разработки
make lint
```

### Шаг 4: Коммиты

**Формат коммита:**

```
<тип>: <краткое описание>

<детальное описание (опционально)>

<footer (опционально)>
```

**Типы коммитов:**

- `feat`: новая функциональность
- `fix`: исправление бага
- `refactor`: рефакторинг без изменения функциональности
- `docs`: изменения в документации
- `test`: добавление или изменение тестов
- `style`: форматирование, отсутствующие точки с запятой и т.д.
- `chore`: обновление зависимостей, конфигурации и т.д.

**Примеры хороших коммитов:**

```bash
git add .
git commit -m "feat: добавлена интеграция с Google Sheets"

git commit -m "fix: исправлена ошибка при обработке вебхука

Проблема возникала, когда приходил некорректный JSON.
Добавлена валидация входящих данных."

git commit -m "test: добавлены тесты для хендлера FAQ"

git commit -m "docs: обновлено README с инструкциями по деплою"

git commit -m "refactor: упрощена логика обработки меню"
```

**Плохие примеры (так НЕ надо):**

```bash
# ❌ Слишком общее
git commit -m "fix bug"

# ❌ Непонятно что сделано
git commit -m "update"

# ❌ Слишком много изменений в одном коммите
git commit -m "добавлено 10 новых фич и исправлено 5 багов"
```

### Шаг 5: Отправка

```bash
git push origin feature/ваша-ветка
```

---

## Стандарты кода

### Форматирование с Black

```bash
# Автоматическое форматирование
black src/ tests/

# Или через make
make format

# Проверка без изменений
black --check src/ tests/
```

**Настройки Black:**
- Длина строки: 100 символов
- Используется для всего Python кода

### Линтинг с Flake8

```bash
# Проверка кода
flake8 src/ tests/

# Или через make
make lint
```

**Основные правила:**
- Максимальная длина строки: 100 символов
- Следуйте PEP 8
- Избегайте неиспользуемых импортов
- Используйте осмысленные имена переменных

### Импорты с isort

```bash
# Автоматическая сортировка импортов
isort src/ tests/

# Проверка без изменений
isort --check-only src/ tests/
```

**Порядок импортов:**
1. Стандартная библиотека
2. Сторонние библиотеки
3. Локальные импорты

Пример:
```python
# Стандартная библиотека
import asyncio
import logging
from typing import Optional

# Сторонние библиотеки
from aiogram import Bot, Dispatcher
from aiogram.types import Message

# Локальные импорты
from src.config import settings
from src.keyboards.main_menu import get_main_menu
```

### Docstrings

Используйте docstrings для всех публичных функций, классов и модулей:

```python
def process_user_data(user_id: int, data: dict) -> bool:
    """
    Обрабатывает данные пользователя.
    
    Args:
        user_id: ID пользователя
        data: Словарь с данными пользователя
    
    Returns:
        True если обработка успешна, False иначе
    
    Raises:
        ValueError: Если данные некорректны
    """
    ...
```

### Type Hints

Всегда используйте type hints:

```python
# ✅ Хорошо
async def send_message(user_id: int, text: str) -> bool:
    ...

# ❌ Плохо
async def send_message(user_id, text):
    ...
```

---

## Тестирование

### Перед коммитом

**Обязательно запустите все тесты:**

```bash
# Все тесты
pytest

# Или через make
make test

# С покрытием кода
make test-cov
```

### Написание тестов

**Каждая новая функциональность должна иметь тесты!**

```python
# tests/test_new_feature.py
import pytest
from src.handlers.new_feature import new_handler


@pytest.mark.unit
async def test_new_handler(message):
    """Тест нового хендлера"""
    message.text = '/new_command'
    
    await new_handler(message)
    
    message.answer.assert_called_once()
    response = message.answer.call_args[0][0]
    assert "Ожидаемый текст" in response
```

### Минимальное покрытие

- **Unit тесты**: обязательны для всех новых функций
- **Integration тесты**: для сложных взаимодействий
- **Покрытие кода**: стремитесь к 80%+

```bash
# Проверка покрытия
pytest --cov=src --cov-report=term
```

---

## Git Flow

### Структура веток

```
main (production)
  ├── develop (staging)
  │   ├── feature/new-feature-1
  │   ├── feature/new-feature-2
  │   ├── fix/bug-fix
  │   └── refactor/code-improvement
  └── hotfix/critical-bug (созда`е`тся из main)
```

### Основные ветки

**`main`**
- Продакшн-готовый код
- Только стабильные релизы
- Защищена от прямых коммитов
- Требует Pull Request с одобрением

**`develop`**
- Ветка разработки
- Интеграция всех фич
- Тестирование перед релизом
- Мерджится в `main` при релизе

### Рабочие ветки

**Feature ветки** (`feature/*`)
- Создаются из `develop`
- Мерджатся обратно в `develop`
- Удаляются после мерджа

```bash
# Создание feature ветки
git checkout develop
git pull origin develop
git checkout -b feature/google-sheets-integration

# После завершения работы
git push origin feature/google-sheets-integration
# Создаете PR в develop
```

**Bugfix ветки** (`fix/*`)
- Создаются из `develop`
- Мерджатся в `develop`

```bash
git checkout develop
git checkout -b fix/webhook-timeout
# Исправляете баг, коммитите, пушите, создаете PR
```

**Hotfix ветки** (`hotfix/*`)
- Создаются из `main` для срочных исправлений
- Мерджатся в `main`, а `main` в `develop`

```bash
git checkout main
git checkout -b hotfix/critical-security-fix
# Исправляете, тестируете
git push origin hotfix/critical-security-fix
# Создаёте PR в main, hotfix мерджится в main
# main мерджится в develop (чтобы подтянуть все актуальные исправления)
```

---

## Pull Request процесс

### Шаг 1: Подготовка PR

**Перед созданием PR убедитесь:**

```bash
# 1. Синхронизируйтесь с develop
git checkout develop
git pull origin develop
git checkout feature/ваша-ветка
git merge develop

# 2. Разрешите конфликты (если есть)
# Отредактируйте конфликтующие файлы
git add .
git commit -m "fix: разрешены конфликты с develop"

# 3. Запустите тесты
make test

# 4. Проверьте код
make lint

# 5. Отформатируйте код
make format

# 6. Еще раз запустите тесты
make test

# 7. Запушьте изменения
git push origin feature/ваша-ветка
```

### Шаг 2: Создание PR

1. Перейдите на GitHub в репозиторий проекта
2. Нажмите "Compare & pull request" или "New pull request"
3. **Base:** `develop` (ветка, в которую мержим)
4. **Compare:** `feature/ваша-ветка` (ваша feature ветка)
5. Заполните описание PR по шаблону
6. Назначьте ревьюверов
7. Создайте PR

**Заполните шаблон PR:**

```markdown
## Описание изменений

<!-- Краткое описание того, что делает этот PR -->

## Тип изменений

<!-- Отметьте галочкой нужное -->

- [ ] Новая функциональность (feature)
- [ ] Исправление бага (bug fix)
- [ ] Рефакторинг (refactoring)
- [ ] Документация (documentation)
- [ ] Тесты (tests)
- [ ] Конфигурация (chore)

## Что было сделано

<!-- Детальное описание изменений -->

- 
- 
- 

## Как протестировать

<!-- Шаги для тестирования изменений -->

1. 
2. 
3. 

## Скриншоты (если применимо)

<!-- Добавьте скриншоты интерфейса, если изменения визуальные -->

## Связанные Issue

<!-- Укажите номера связанных Issues -->

Closes #
Related to #

## Чеклист

<!-- Убедитесь, что все пункты выполнены перед созданием PR -->

- [ ] Код отформатирован (`make format` или `black src/ tests/`)
- [ ] Код проверен линтером (`make lint` или `flake8 src/ tests/`)
- [ ] Все тесты проходят (`make test` или `pytest`)
- [ ] Добавлены новые тесты для новой функциональности
- [ ] Обновлена документация (README, TESTING, docstrings)
- [ ] Нет конфликтов с `develop` веткой
- [ ] Коммиты следуют [стандарту](https://github.com/reclacc/competencies-center-bot/blob/develop/CONTRIBUTING.md#шаг-4-коммиты)
- [ ] PR создан из актуальной ветки `develop`

## Дополнительная информация

<!-- Любая дополнительная информация, которая может быть полезна ревьюерам -->
```

### Шаг 3: Ожидание ревью

**Что происходит после создания PR:**

1. **Автоматические проверки** (CI/CD)
   - Запускаются тесты
   - Проверяется форматирование
   - Проверяется линтинг
   - ✅ Всё должно быть зеленым!!!

2. **Code Review**
   - Минимум 1 одобрение
   - Возможны комментарии и запросы на изменения

3. **Внесение изменений** (если требуется)
   ```bash
   # Вносите изменения в той же ветке
   git add .
   # Пишите нормальные коммиты, это просто пример!!!
   git commit -m "fix: исправлены замечания ревью"
   git push origin feature/ваша-ветка
   # PR автоматически обновится
   ```

4. **Одобрение и мердж**
   - Ревьюер одобряет PR
   - PR мерджится в `develop`
   - Ваша ветка удаляется

---

## Code Review

### Если вы ревьюер

**На что обращать внимание:**

**Код:**
- Читаемость и понятность
- Соответствие стандартам проекта
- Нет дублирования кода
- Правильное использование паттернов

**Тесты:**
- Наличие тестов для новой функциональности
- Покрытие edge cases, если требует функциональность
- Качество и читаемость тестов

**Документация:**
- Docstrings для новых функций
- Обновлён README (если нужно)
- Понятные комментарии

**Безопасность:**
- В коде нет токенов/паролей
- Валидация входных данных (если они есть)
- Обработка ошибок

### Если вы автор PR

**Исправляйте свои недочёты!**

---

## FAQ

### Q: У меня конфликты при мердже, что делать?

```bash
# 1. Сначала обновите develop
git checkout develop
git pull origin develop

# 2. Перебазируйте вашу ветку на актуальный develop
git checkout feature/ваша-ветка
git rebase develop

# 3. Разрешите конфликты вручную
# Отредактируйте файлы с конфликтами, затем:
git add .
git rebase --continue

# 4. Безопасный пуш после переписывания истории
git push --force-with-lease origin feature/ваша-ветка
```

### Q: Как отменить последний коммит?

```bash
# Отменить коммит, но сохранить изменения
git reset --soft HEAD~1

# Отменить коммит и изменения (так делать ОПАСНО)
git reset --hard HEAD~1
```

### Q: Я случайно коммитнул в develop, что делать?

```bash
# 1. Создайте новую ветку с текущими изменениями
git checkout -b feature/new-branch

# 2. Верните develop к исходному состоянию
git checkout develop
git reset --hard origin/develop

# 3. Продолжайте работу в новой ветке
git checkout feature/new-branch
```

### Q: Как исправить ещё не запушенный коммит?

```bash
# Исправить последний коммит (изменить сообщение и/или содержимое)
git add .
git commit --amend

# Затем при пуше используйте --force-with-lease
git push --force-with-lease origin feature/ваша-ветка
```

### Q: Как обновить свой PR после комментариев?

```bash
# Просто внесите изменения и запушьте в ту же ветку
git add .
git commit -m "fix: исправлены замечания ревью"
git push origin feature/ваша-ветка
# PR автоматически обновится
```

### Q: Тесты падают только в CI, но локально работают

```bash
# Проверьте версию Python
python --version

# Убедитесь, что используете те же зависимости
pip install -r requirements.txt --force-reinstall

# Запустите тесты так же, как в CI
pytest -v --tb=short
```

### Q: Как посмотреть, что именно изменится при мердже?
```bash
# Посмотреть разницу между вашей веткой и develop
git fetch origin
git diff feature/ваша-ветка..origin/develop

# Или с помощью git log
git log --oneline --graph feature/ваша-ветка..origin/develop
```
---

***Good Luck, Have Fun!***
