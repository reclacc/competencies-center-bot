"""Утилиты и данные для каталога образовательных платформ"""

from typing import Optional

# Категории образовательных платформ
CATEGORIES = [
    {
        "id": "programming",
        "name": "Программирование",
        "icon": "💻",
        "description": "Курсы по разработке ПО, веб-разработке и программированию",
    },
    {
        "id": "design",
        "name": "Дизайн",
        "icon": "🎨",
        "description": "Графический дизайн, UX/UI, 3D-моделирование",
    },
    {
        "id": "data_science",
        "name": "Анализ данных",
        "icon": "📊",
        "description": "Data Science, машинное обучение, аналитика",
    },
    {
        "id": "management",
        "name": "Менеджмент",
        "icon": "📈",
        "description": "Управление проектами, продуктовый менеджмент",
    },
    {
        "id": "languages",
        "name": "Иностранные языки",
        "icon": "🌍",
        "description": "Изучение иностранных языков",
    },
]

# Заглушка для платформ до интеграции с Google Sheets by чатгпт
PLATFORMS = [
    # Программирование
    {
        "id": "stepik",
        "name": "Stepik",
        "category_id": "programming",
        "description": (
            "Российская образовательная платформа с бесплатными и платными курсами "
            "по программированию, математике, анализу данных."
        ),
        "features": [
            "Интерактивные задачи с автопроверкой",
            "Сертификаты о прохождении",
            "Курсы от ведущих университетов",
            "Поддержка множества языков программирования",
        ],
        "target_audience": "Начинающие и опытные разработчики",
        "link": "https://stepik.org",
    },
    {
        "id": "coursera",
        "name": "Coursera",
        "category_id": "programming",
        "description": (
            "Международная платформа с курсами от топовых университетов мира. "
            "Специализации по Computer Science, AI, веб-разработке."
        ),
        "features": [
            "Курсы от Stanford, MIT, Google",
            "Профессиональные сертификаты",
            "Гибкий график обучения",
            "Финансовая помощь для студентов",
        ],
        "target_audience": "Студенты и профессионалы всех уровней",
        "link": "https://www.coursera.org",
    },
    {
        "id": "hexlet",
        "name": "Hexlet",
        "category_id": "programming",
        "description": (
            "Практические курсы по веб-разработке с акцентом на реальные проекты. "
            "Обучение JavaScript, Python, PHP."
        ),
        "features": [
            "Менторская поддержка",
            "Реальные проекты в портфолио",
            "Помощь в трудоустройстве",
            "Сообщество разработчиков",
        ],
        "target_audience": "Начинающие разработчики, карьерный переход",
        "link": "https://ru.hexlet.io",
    },
    # Дизайн
    {
        "id": "skillbox_design",
        "name": "Skillbox: Дизайн",
        "category_id": "design",
        "description": (
            "Комплексные курсы по графическому дизайну, UX/UI, motion-дизайну "
            "с дипломом государственного образца."
        ),
        "features": [
            "Работа с реальными заказчиками",
            "Портфолио из 5+ проектов",
            "Трудоустройство после обучения",
            "Мастер-классы от практиков",
        ],
        "target_audience": "Новички и дизайнеры среднего уровня",
        "link": "https://skillbox.ru/design",
    },
    {
        "id": "domestika",
        "name": "Domestika",
        "category_id": "design",
        "description": (
            "Творческая платформа с курсами по иллюстрации, дизайну, "
            "фотографии от известных креативных профессионалов."
        ),
        "features": [
            "Курсы от мировых экспертов",
            "Акцент на творческом процессе",
            "Международное сообщество",
            "Доступ навсегда после покупки",
        ],
        "target_audience": "Творческие профессионалы и любители",
        "link": "https://www.domestika.org",
    },
    # Анализ данных
    {
        "id": "datacamp",
        "name": "DataCamp",
        "category_id": "data_science",
        "description": (
            "Специализированная платформа для изучения Data Science, "
            "Python, R, SQL с интерактивными упражнениями."
        ),
        "features": [
            "Практика в браузере без установки",
            "Карьерные треки по специализациям",
            "Проекты на реальных данных",
            "Сертификация навыков",
        ],
        "target_audience": "Аналитики данных, дата-сайентисты",
        "link": "https://www.datacamp.com",
    },
    {
        "id": "kaggle_learn",
        "name": "Kaggle Learn",
        "category_id": "data_science",
        "description": (
            "Бесплатные микрокурсы по ML, Deep Learning, SQL от платформы Kaggle. "
            "Практика на соревнованиях."
        ),
        "features": [
            "Полностью бесплатно",
            "Интеграция с соревнованиями Kaggle",
            "Короткие практические курсы",
            "Сообщество дата-сайентистов",
        ],
        "target_audience": "Начинающие и практикующие ML-инженеры",
        "link": "https://www.kaggle.com/learn",
    },
    # Менеджмент
    {
        "id": "product_star",
        "name": "ProductStar",
        "category_id": "management",
        "description": (
            "Курсы по продуктовому менеджменту, проектному управлению, "
            "маркетингу с акцентом на практику."
        ),
        "features": [
            "Кейсы от Яндекс, Сбер, VK",
            "Менторство от практикующих PM",
            "Реальные продуктовые задачи",
            "Карьерный центр",
        ],
        "target_audience": "Менеджеры продуктов, project-менеджеры",
        "link": "https://productstar.ru",
    },
    {
        "id": "pmbok",
        "name": "PMI: Управление проектами",
        "category_id": "management",
        "description": (
            "Официальные курсы по подготовке к сертификации PMP, "
            "Agile, Scrum от Project Management Institute."
        ),
        "features": [
            "Международная сертификация",
            "Стандарты PMBOK",
            "Признание работодателями по всему миру",
            "Профессиональное сообщество",
        ],
        "target_audience": "Проектные менеджеры с опытом",
        "link": "https://www.pmi.org/learning",
    },
    # Языки
    {
        "id": "duolingo",
        "name": "Duolingo",
        "category_id": "languages",
        "description": (
            "Бесплатное изучение иностранных языков в игровой форме. " "Поддержка 40+ языков."
        ),
        "features": [
            "Геймификация обучения",
            "Ежедневные цели и напоминания",
            "Практика устной речи",
            "Полностью бесплатная базовая версия",
        ],
        "target_audience": "Изучающие языки всех уровней",
        "link": "https://www.duolingo.com",
    },
    {
        "id": "skyeng",
        "name": "Skyeng",
        "category_id": "languages",
        "description": (
            "Персональные уроки английского с преподавателем онлайн. "
            "Индивидуальная программа обучения."
        ),
        "features": [
            "Занятия с носителями языка",
            "Гибкий график",
            "Интерактивная платформа",
            "Подготовка к экзаменам IELTS, TOEFL",
        ],
        "target_audience": "Изучающие английский от A1 до C2",
        "link": "https://skyeng.ru",
    },
]


def get_categories() -> list[dict]:
    """
    Получить список всех категорий

    Returns:
        list[dict]: Список категорий
    """
    return CATEGORIES


def get_platforms_by_category(category_id: str) -> list[dict]:
    """
    Получить платформы по ID категории

    Args:
        category_id: ID категории

    Returns:
        list[dict]: Список платформ в категории
    """
    return [p for p in PLATFORMS if p["category_id"] == category_id]


def get_platform_by_id(platform_id: str) -> Optional[dict]:
    """
    Получить платформу по ID

    Args:
        platform_id: ID платформы

    Returns:
        Optional[dict]: Платформа или None
    """
    return next((p for p in PLATFORMS if p["id"] == platform_id), None)


def get_all_platforms() -> list[dict]:
    """
    Получить все платформы

    Returns:
        list[dict]: Список всех платформ
    """
    return PLATFORMS
