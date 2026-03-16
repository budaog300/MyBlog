from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from src.core.security import SessionDep, UserDep, AdminUserDep, PagninationDep
from src.posts.schemas import AddPostSchema, OutPostSchema, PostFilterSchema, AddCommentSchema
from src.posts.crud.posts import (
    get_posts_by_user,
    get_all_posts,
    create_post_by_user,     
    toggle_like,  
    toggle_bookmark    
)
from src.posts.crud.comments import add_comment
router = APIRouter(prefix="/api/v1/post", tags=["Посты"])

FilterDep = Annotated[PostFilterSchema, Depends(PostFilterSchema)]


@router.get("/", summary="Все посты")
async def get_posts(
    pagination: PagninationDep, 
    db: SessionDep, 
    filters: FilterDep, 
    search: str = "",
    sort_by: str = "created_at",
    order: str = "desc"
) -> list[OutPostSchema]:
    result = await get_all_posts(
        pagination, db, 
        search=search, 
        sort_by=sort_by, 
        order=order, 
        **filters.model_dump()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Посты не найдены!")  
    return result


@router.get("/me", summary="Мои посты")
async def get_user_posts(user: UserDep, pagination: PagninationDep, db: SessionDep) -> list[OutPostSchema]:
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


@router.post("/{post_id}/comment", summary="Оставить комментарий")
async def create_comment(post_id: int, data: AddCommentSchema, user: UserDep, db: SessionDep):
    result = await add_comment(post_id, data, user, db)
    if not result:
        raise HTTPException(status_code=404, detail="Ошибка при оставлении комментария!")
    return result