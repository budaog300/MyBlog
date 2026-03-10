from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from src.users.models import User


async def get_users(db: AsyncSession):
    query = select(User)
    try:
        result = await db.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        print(f"Ошибка получения всех пользователей: {e}")
        raise e
    

async def delete_user_by_id(user_id: int, db: AsyncSession):
    stmt = delete(User).where(User.id == user_id)
    try:
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        print(f"Ошибка удаления пользователя: {e}")
        raise e
    

async def change_role_user(user_id: int, role: str, db: AsyncSession):
    query = select(User).where(User.id == user_id)
    try:
        user = await db.execute(query)
        user = user.scalar_one_or_none()   
    except SQLAlchemyError as e:
        print(f"Ошибка получения пользователя: {e}")
        raise e
    if not user:
        return None
    cur_role = getattr(user, role)
    setattr(user, role, not cur_role)    
    try:
        await db.commit()
        await db.refresh(user)
        return getattr(user, role)
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка изменения роли пользователя: {e}")
        raise e