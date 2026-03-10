from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.posts.models import Post, Tag, PostTag
from src.users.models import User
from src.posts.schemas import AddTagSchema


async def toggle_post_tag(post_id: int, tag_id: int, user: User, db: AsyncSession):
    post = await db.get(Post, post_id)
    if not post or post.user_id != user.id:
        return False

    stmt = insert(PostTag).values(post_id=post_id, tag_id=tag_id)
    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Ошибка добавления тега посту {post_id}: {e}")
        raise e


async def create_tag_by_admin(tag_data: AddTagSchema, db: AsyncSession):
    stmt = insert(Tag).values(**tag_data.model_dump())
    try:
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка создания тега: {e}")
        raise e
    

async def get_tag_posts(tag_id: int, db: AsyncSession):
    query = (
        select(Tag)
        .where(Tag.id == tag_id)
        .options(
            joinedload(Tag.posts)
        )
    )
    try:
        result = await db.execute(query)
        if not result:
            return None
        tag_posts = result.unique().scalars().all()
        return tag_posts
    except SQLAlchemyError as e:
        print(f"Ошибка получения постов для тега: {e}")
        raise e
        

async def delete_tag_by_id(tag_id: int, db: AsyncSession):
    stmt = delete(Tag).where(Tag.id == tag_id)
    try:
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка удаления тега {tag_id}: {e}")
        raise e