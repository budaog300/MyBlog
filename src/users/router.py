from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from src.users.schemas import AddUserSchema, LoginUserSchema
from src.users.crud import get_users, change_role_user, delete_user_by_id
from src.users.auth import get_password_hash, create_user, authenticate
from src.core.security import create_access_token, SessionDep, UserDep, AdminUserDep

router = APIRouter(prefix="/api/v1/users", tags=["Пользователи"])


@router.post("/register", summary="Регистрация пользователя")
async def register_user(db: SessionDep, user_data: AddUserSchema, response: Response):
    user_data_dict = user_data.model_dump()
    user_data_dict["password"] = get_password_hash(user_data_dict["password"])
    if not await create_user(db, user_data_dict):
        raise HTTPException(status_code=409, detail="Пользователь с таким email уже существует")    
    user = await authenticate(db, {"login": user_data.email, "password": user_data.password})
    print(user, user.id)
    if not user:
        raise HTTPException(status_code=401, detail="Ошибка входа в систему")
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Вы успешно зарегистрированы!", "access_token": access_token, "refresh_token": None}


@router.post("/login", summary="Вход в систему")
async def login_user(db: SessionDep, user_data: LoginUserSchema, response: Response):
    user_data = user_data.model_dump()
    user = await authenticate(db, user_data)
    if not user:
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"message": "Вы вошли в систему!", "access_token": access_token, "refresh_token": None}


@router.post("/logout", summary="Выход из системы")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Вы вышли из системы!"}


@router.get("/profile", summary="Профиль пользователя")
async def get_profile(user: UserDep):
    return user


@router.get("/all_users", summary="Все пользователи")
async def get_all_users(user: AdminUserDep, db: SessionDep):
    return await get_users(db)


@router.patch("/{user_id}/role", summary="Изменить роль пользователю")
async def patch_user_role(user_id: int, role: str, user: AdminUserDep, db: SessionDep):
    return await change_role_user(user_id, role, db)


@router.delete("/{user_id}", summary="Удалить пользователя")
async def delete_user(user_id: int, user: AdminUserDep, db: SessionDep):
    await delete_user_by_id(user_id, db)
    return {"message": "Пользователь успешно удален!"}