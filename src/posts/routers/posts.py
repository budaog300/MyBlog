from fastapi import APIRouter, Depends, HTTPException

from src.core.security import SessionDep, UserDep, AdminUserDep, PagninationDep
from src.posts.schemas import AddPostSchema, OutPostSchema
from src.posts.crud.posts import (
    get_posts_by_user,
    create_post_by_user,     
    toggle_like,  
    toggle_bookmark    
)

router = APIRouter(prefix="/api/v1/post", tags=["Посты"])


@router.get("/", summary="Мои посты")
async def get_posts(user: UserDep, pagination: PagninationDep, db: SessionDep) -> list[OutPostSchema]:
    result = await get_posts_by_user(user, pagination, db)
    if not result:
        raise HTTPException(status_code=404, detail="Посты не найдены!")  
    return result


@router.post("/", summary="Создать пост")
async def create_post(post_data: AddPostSchema, user: UserDep, db: SessionDep):
    result = await create_post_by_user(post_data, user, db)
    if not result:
        raise HTTPException(status_code=404, detail=f"Категория {post_data.category_id} не найдена!")
    return {"message": "Пост успешно создан"}


@router.post("/{post_id}/like", summary="Оценить пост")
async def like_post(post_id: int, user: UserDep, db: SessionDep):
    result = await toggle_like(post_id, user, db)
    if not result:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return result


@router.post("/{post_id}/bookmark", summary="Добавить/удалить пост в закладки")
async def bookmark_post(post_id: int, user: UserDep, db: SessionDep):
    result = await toggle_bookmark(post_id, user, db)
    if not result:
        raise HTTPException(status_code=404, detail="Пост не найден")
    return result