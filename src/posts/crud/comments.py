from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.posts.models import Comment, Post
from src.users.models import User
from src.posts.schemas import AddCommentSchema


async def add_comment(post_id: int, data: AddCommentSchema, user: User, db: AsyncSession):
    post = await db.get(Post, post_id)
    if not post:
        return False
    if not parent_comment or data.parent_id is not None:
        parent_comment = await db.get(Comment, data.parent_id)        
        if parent_comment.post_id != post_id:
            return False
    stmt = (
        insert(Comment)
        .values(post_id=post_id, user_id=user.id, **data.model_dump())
    )
    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        raise e
    

async def delete_comment(comment_id: int, db: AsyncSession):
    stmt = delete(Comment).where(Comment.id == comment_id)
    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        raise e
