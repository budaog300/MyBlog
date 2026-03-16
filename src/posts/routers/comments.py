from fastapi import APIRouter, HTTPException

from src.core.security import SessionDep, UserDep, AdminUserDep
from src.posts.crud.comments import delete_comment


router = APIRouter(prefix="/api/v1/comment", tags=["Комментарии"])


@router.delete("/{comment_id}", summary="Удалить комментарий")
async def delete_comment_by_admin(comment_id: int, user: AdminUserDep, db: SessionDep):
    return await delete_comment(comment_id, db)