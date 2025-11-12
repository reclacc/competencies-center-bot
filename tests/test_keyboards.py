"""Тесты для клавиатур"""

import pytest
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.keyboards.main_menu import get_main_menu


@pytest.mark.unit
class TestMainMenu:
    """Тесты для главного меню"""

    def test_get_main_menu_returns_keyboard(self):
        """Проверка возврата клавиатуры"""
        keyboard = get_main_menu()

        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.resize_keyboard is True

    def test_main_menu_has_correct_buttons(self):
        """Проверка наличия всех кнопок"""
        keyboard = get_main_menu()

        expected_buttons = [
            "Целевые группы",
            "Мероприятия",
            "Партнёры",
            "Цифровые продукты",
            "Направления",
            "Курсы",
            "FAQ",
            "Подписка на уведомления",
        ]

        # Собираем все тексты кнопок
        all_buttons = []
        for row in keyboard.keyboard:
            for button in row:
                all_buttons.append(button.text)

        # Проверяем наличие всех ожидаемых кнопок
        for expected in expected_buttons:
            assert expected in all_buttons, f"Кнопка '{expected}' не найдена"

    def test_main_menu_button_count(self):
        """Проверка количества кнопок"""
        keyboard = get_main_menu()

        button_count = sum(len(row) for row in keyboard.keyboard)

        assert button_count == 8, "Должно быть 8 кнопок в главном меню"

    def test_main_menu_buttons_are_keyboard_button_type(self):
        """Проверка типа кнопок"""
        keyboard = get_main_menu()

        for row in keyboard.keyboard:
            for button in row:
                assert isinstance(button, KeyboardButton)

    def test_main_menu_layout(self):
        """Проверка расположения кнопок"""
        keyboard = get_main_menu()

        # Проверяем, что все кнопки по одной в ряду
        for row in keyboard.keyboard:
            assert len(row) == 1, "Каждая кнопка должна быть на отдельной строке"

    def test_main_menu_idempotency(self):
        """Проверка идемпотентности - повторные вызовы дают одинаковый результат"""
        keyboard1 = get_main_menu()
        keyboard2 = get_main_menu()

        # Сравниваем количество кнопок и их тексты
        buttons1 = [btn.text for row in keyboard1.keyboard for btn in row]
        buttons2 = [btn.text for row in keyboard2.keyboard for btn in row]

        assert buttons1 == buttons2
