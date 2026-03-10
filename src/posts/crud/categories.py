from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type

from src.posts.models import Category
from src.posts.schemas import AddCategorySchema


async def create_category_by_admin(data: AddCategorySchema, db: AsyncSession):
    stmt = insert(Category).values(**data.model_dump())
    try:
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка создания категории: {e}")
        raise e
    

async def get_category_posts(cat_id: int, db: AsyncSession):
    query = (
        select(Category)
        .where(Category.id == cat_id)
        .options(
            joinedload(Category.posts)
        )
    )
    try:
        result = await db.execute(query)
        if not result:
            return None
        return result.unique().scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Ошибка получения категории {cat_id}: {e}")
        raise e
    

async def delete_category_by_id(cat_id: int, db: AsyncSession):
    stmt = delete(Category).where(Category.id == cat_id)
    try:        
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка удаления категории {cat_id}: {e}")
        raise e