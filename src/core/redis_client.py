from redis.asyncio import Redis

from src.core.config import settings


class RedisClient:
    """
    Внутреннее хранилище для экземпляра Redis-клиента.

    Нужно для того, чтобы во всём приложении использовалось
    одно и то же соединение, а не создавалось новое каждый раз.
    """

    _instance: Redis | None = None

    @classmethod
    def get_instance(cls) -> Redis:
        """
        Возвращает общий экземпляр Redis-клиента.

        Если соединение с Redis ещё не было создано, этот метод
        инициализирует его, используя URL из настроек приложения.
        Клиент создаётся с автоматическим декодированием байтов
        в строки (UTF-8), чтобы ответы Redis были всегда строковыми.

        Returns:
            Redis: Активный Redis-клиент, который можно повторно
            использовать в любом месте приложения.
        """
        if cls._instance is None:
            cls._instance = Redis.from_url(
                settings.redis_url,
                decode_responses=True,  # декодирует байты в строки
                encoding="utf-8",
            )
        return cls._instance

    @classmethod
    async def close(cls):
        """
        Закрывает текущее соединение с Redis, если оно существует.

        Этот метод следует вызывать при завершении работы приложения,
        чтобы корректно закрыть сетевое соединение и освободить ресурсы.
        После закрытия внутренний экземпляр сбрасывается в None.
        """
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


def get_redis() -> Redis:
    """
    Удобная функция для получения общего Redis-клиента.

    Returns:
        Redis: Тот же экземпляр Redis, который используется приложением.
    """
    return RedisClient.get_instance()
