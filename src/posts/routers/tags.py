from fastapi import APIRouter, Depends, HTTPException

from src.core.security import SessionDep, UserDep, AdminUserDep, PagninationDep, get_curent_admin_user, get_current_user
from src.posts.crud.tags import (   
    create_tag_by_admin,  
    delete_tag_by_id,
    toggle_post_tag,
    get_tag_posts,   
)
from src.posts.schemas import AddTagSchema

router = APIRouter(prefix="/api/v1/tag", tags=["Теги"])


@router.get("/{tag_id}", summary="Посты у тега")
async def get_tag(tag_id: int, db: SessionDep):
    result = await get_tag_posts(tag_id, db)
    if not result:
        raise HTTPException(status_code=404, detail=f"Нет постов у тега {tag_id}")
    return result


@router.post("/", summary="Создать тег")
async def create_tag(tag_data: AddTagSchema, user: AdminUserDep, db: SessionDep):
    await create_tag_by_admin(tag_data, db)
    return {"message": "Тег успешно создан!"}


@router.delete("/{tag_id}", summary="Удалить тег", dependencies=[Depends(get_curent_admin_user)], responses={403: {"description": "Требуются права администратора"}})
async def delete_tag(tag_id: int, db: SessionDep):
    await delete_tag_by_id(tag_id, db)  
    return {"message": "Тег успешно удален!"}