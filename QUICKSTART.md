# Быстрый старт для разработчиков

Это краткое руководство, чтоб кота не тянуть.

> Для полной информации смотрите [CONTRIBUTING.md](CONTRIBUTING.md)

## До первого коммита

### 1) Клонируйте и настройте

```bash
git clone https://github.com/reclacc/competencies-center-bot.git
cd competencies-center-bot

# Создайте venv и установите зависимости
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt

# Создайте .env
cp .env.example .env
# Отредактируйте .env и добавьте BOT_TOKEN
```

### 2) Создайте ветку

```bash
# Перейдите на актуальную версию main
git checkout main
git pull origin main

# Создайте ветку для вашей задачи
git checkout -b feature/my-cringe-feature
```

### 3) Разрабатывайте

```bash
# Делайте изменения
# Пробуйте, экспериментируйте...
# ...

# Проверьте код
make format  # Форматирование
make lint    # Линтинг
make test    # Тесты

# Или всё сразу:
make format && make lint && make test
```

### 4) Коммитьте ТОЛЬКО ЕСЛИ ПРОШЛИ ВСЕ ТЕСТЫ

```bash
git add .
# Коммиты пишите нормальные, подробные, это просто пример!!!
git commit -m "feat: добавлена новая крутая фича"
git push origin feature/my-cringe-feature
```

### 5) Создайте Pull Request

1. Перейдите на GitHub  
2. Нажмите **"Compare & pull request"**  
3. Заполните шаблон PR  
4. Отправьте на ревью!

---

## 📋 Шпаргалка по командам

### Git

```bash
# Создание ветки
git checkout -b feature/название

# Коммит
git add .
git commit -m "тип: описание"

# Отправка
git push origin имя-ветки

# Отмена изменений
git checkout -- имя-файла

# Временное сохранение
git stash
git stash pop
```

### Разработка

```bash
# Запуск бота
python -m src.main

# Тесты
make test              # Все тесты
make test-unit         # Unit тесты
make test-integration  # Integration тесты
make test-cov          # С покрытием
make test-watch        # Watch mode

# Качество кода
make format            # Black форматирование
make lint              # Flake8 проверка
make clean             # Очистка кеша
```

### Проверка перед PR

```bash
# Убедитесь, что всё в порядке
make format && make lint && make test
```

---

## Типы коммитов

| Тип | Когда использовать | Пример |
|-----|-------------------|--------|
| `feat` | Новая функциональность | `feat: добавлен экспорт в Excel` |
| `fix` | Исправление бага | `fix: исправлена ошибка вебхука` |
| `refactor` | Рефакторинг кода | `refactor: упрощена логика меню` |
| `test` | Добавление тестов | `test: добавлены тесты для FAQ` |
| `docs` | Документация | `docs: обновлен README` |
| `style` | Форматирование | `style: исправлено форматирование` |
| `chore` | Обновление зависимостей | `chore: обновлен aiogram до 3.22` |

---

## Имена веток

| Тип | Формат | Пример |
|-----|--------|--------|
| Новая фича | `feature/описание` | `feature/google-sheets` |
| Исправление бага | `fix/описание` | `fix/webhook-error` |
| Рефакторинг | `refactor/описание` | `refactor/handlers` |
| Документация | `docs/описание` | `docs/api-guide` |
| Тесты | `test/описание` | `test/keyboards` |

---

## Частые ошибки

### 1. Забыли обновить локалку перед работой

```bash
# ❌ Неправильно
git checkout -b feature/new
# работаете...

# ✅ Правильно
git checkout main
git pull origin main
git checkout develop
git pull origin develop
git checkout -b feature/new
# работаете...
```

### 2. Не запустили линтер и тесты перед коммитом

```bash
# ❌ Неправильно
git commit -m "feat: новая фича"
git push
# PR падает на CI

# ✅ Правильно
make lint && make format && make test
git commit -m "feat: новая фича"
git push
```

### 3. Плохое название коммита

```bash
# ❌ Неправильно
git commit -m "fix"
git commit -m "update"
git commit -m "changes"

# ✅ Правильно
git commit -m "fix: исправлена ошибка обработки вебхука"
git commit -m "feat: добавлена интеграция с Google Sheets"
```

### 4. Работа в main/develop ветке

```bash
# ❌ Неправильно
git checkout develop
# внесли изменения
git commit -m "..."

# ✅ Правильно
git checkout develop
git checkout -b feature/my-feature
# внесли изменения
git commit -m "..."
```

---

## Что делать если...

### ...у меня конфликты?

```bash
git fetch origin
git merge origin/develop
# Разрешите конфликты в файлах
git add .
git commit -m "fix: разрешены конфликты"
```

### ...тесты падают?

```bash
# Запустите тесты локально
pytest -v

# Смотрите детали ошибки
pytest tests/test_failing.py -vv

# Исправьте код
# Запустите снова
pytest
```

### ...забыл отформатировать код?

```bash
make format
make lint
git add .
git commit -m "style: форматирование кода"
git push
```

### ...нужно изменить последний коммит?

```bash
# Внесите изменения
git add .
git commit --amend --no-edit
git push -f origin ваша-ветка
```

### ...случайно коммитнул в не ту ветку?

```bash
# Сохраните изменения в новую ветку
git branch feature/bad-branch
git reset --hard HEAD~1
git checkout feature/correct-branch
```

---

## ✨ Чеклист перед первым PR

- [ ] Клонировал репозиторий  
- [ ] Настроил окружение  
- [ ] Создал ветку с правильным именем  
- [ ] Внёс изменения  
- [ ] Запустил `make format`  
- [ ] Запустил `make lint`  
- [ ] Запустил `make test`  
- [ ] Написал хорошие коммиты  
- [ ] Заполнил шаблон PR  
- [ ] Прочитал [CONTRIBUTING.md](CONTRIBUTING.md)
---
