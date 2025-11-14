from pydantic import BaseModel


class UserSchema(BaseModel):
    """Поля таблицы"""

    user_id: int
    status: str
    mailing: bool
