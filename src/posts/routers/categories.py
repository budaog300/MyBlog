from fastapi import APIRouter, Depends, HTTPException

from src.core.security import SessionDep, UserDep, AdminUserDep, PagninationDep, get_curent_admin_user, get_current_user
from src.posts.crud.categories import (    
    create_category_by_admin,    
    get_category_posts,
    delete_category_by_id
)
from src.posts.schemas import AddPostSchema, AddCategorySchema, AddTagSchema, OutPostSchema

router = APIRouter(prefix="/api/v1/category", tags=["Категории"])


@router.post("/", summary="Создать категорию")
async def create_category(cat_data: AddCategorySchema, user: AdminUserDep, db: SessionDep):
    await create_category_by_admin(cat_data, db)
    return {"message": "Категория успешно создана!"}


@router.get("/{cat_id}", summary="Получение постов из категории")
async def get_category(cat_id: int, db: SessionDep):
    result = await get_category_posts(cat_id, db)
    if not result:
        raise HTTPException(status_code=404, detail=f"Нет постов у категории {cat_id}")
    return result


@router.delete("/{cat_id}", summary="Удалить категорию")
async def delete_category(cat_id: int, user: AdminUserDep, db: SessionDep):
    result = await delete_category_by_id(cat_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Ошибка удаления категории!")
    return result
