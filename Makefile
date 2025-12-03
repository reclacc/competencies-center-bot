.PHONY: test test-unit test-integration test-cov test-watch lint format clean help

help:
	@echo "Доступные команды:"
	@echo "  make test              - Запустить все тесты"
	@echo "  make test-unit         - Запустить только unit тесты"
	@echo "  make test-integration  - Запустить только integration тесты"
	@echo "  make test-cov          - Запустить тесты с покрытием"
	@echo "  make test-watch        - Запустить тесты в watch режиме"
	@echo "  make lint              - Проверить код линтером"
	@echo "  make format            - Форматировать код"
	@echo "  make clean             - Очистить кеш и временные файлы"
	@echo "  make install           - Установить зависимости"

install:
	pip install -r requirements.txt

test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

test-watch:
	ptw src tests -- --testmon -q

lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

run:
	@echo "Не забудьте установить WEBHOOK_URL в .env"
	python -m src.main