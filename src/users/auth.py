from passlib.context import CryptContext
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.schemas import LoginUserSchema
from src.users.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


async def create_user(db: AsyncSession, user_data: dict):
    query = select(User).where(User.email == user_data["email"])
    try:
        result = await db.execute(query)
        result = result.one_or_none()        
    except Exception as e:
        print(f"Ошибка при поиске юзера: {e}")
        raise e
    if result:
        return False
    user = User(**user_data)
    db.add(user)
    try:
        await db.commit()
        print(f"Юзер создан")
        return True
    except Exception as e:
        await db.rollback()
        print(f"Ошибка создания юзера: {e}")
        raise e


async def authenticate(db: AsyncSession, user: dict):  
    query = select(User).where(
        or_(
            User.email == user["login"],
            User.username == user["login"],
        )        
    )
    try:
        result = await db.execute(query)
        result = result.scalar_one_or_none()
        print(1)
    except Exception as e:
        print(f"Ошибка при поиске юзера: {e}")
        raise e
    if not result or not verify_password(user["password"], result.password):
        print(2)
        return None
    return result