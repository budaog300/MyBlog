from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Type

from src.posts.models import Post, Category, Like, Bookmark
from src.users.models import User
from src.posts.schemas import AddPostSchema
from src.core.security import PaginationParams


async def get_posts_by_user(user: User, pagination: PaginationParams, db: AsyncSession):
    query = (
        select(Post)
        .where(Post.user_id == user.id)
        .options(
            joinedload(Post.category),
            joinedload(Post.user),
            joinedload(Post.likes)
        )
        .limit(pagination.size)
        .offset(pagination.offset)
    )    
    try:
        result = await db.execute(query)
        return result.unique().scalars().all()
    except SQLAlchemyError as e:
        print(f"Ошибка получения постов для пользователя {user.id}: {e}")
        raise e
    

async def create_post_by_user(data: AddPostSchema, user: User, db: AsyncSession):
    category = await db.get(Category, data.category_id)
    if not category:
        return False
    stmt = insert(Post).values(user_id=user.id, **data.model_dump())
    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        print(f"Ошибка создания поста пользователем {user.id}: {e}")
        raise e
    

async def toggle_like(post_id: int, user: User, db: AsyncSession):
    post = await db.get(Post, post_id)
    if not post:
        return None
    query = (
        select(Like)
        .where(
            Like.post_id == post_id,
            Like.user_id == user.id
        )
    )
    try:
        result = await db.execute(query)
        like = result.scalar_one_or_none()
   
        if like:       
            await db.delete(like)
            action = "unliked"
        else:            
            db.add(Like(post_id=post_id, user_id=user.id))
            action = "liked"
          
        await db.commit()
        return {"action": action, "post_id": post_id}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка с Like для пользователя {user.id}: {e}")
        raise e
       

async def toggle_bookmark(post_id: int, user: User, db: AsyncSession):
    post = await db.get(Post, post_id)
    if not post:
        return None
    query = (
        select(Bookmark)
        .where(
            Bookmark.post_id == post_id,
            Bookmark.user_id == user.id
        )
    )
    try:
        result = await db.execute(query)
        bookmark = result.scalar_one_or_none()
        if bookmark:
            await db.delete(bookmark)
            action = "removed_from_bookmarks"
            await db.commit()
            return {"action": action, "post_id": post_id}
        else:
            db.add(Bookmark(post_id=post_id, user_id=user.id))
            action = "added_to_bookmarks"
            await db.commit()
            return {"action": action, "post_id": post_id}
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Ошибка с Bookmark для пользователя {user.id}: {e}")
        raise e