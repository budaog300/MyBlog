from fastapi import Depends, Request, Response, HTTPException
from typing import Annotated
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from src.users.models import User
from src.core.database import settings, get_db


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = settings.get_auth_data
    encode_jwt = jwt.encode(to_encode, auth_data["secret_key"], auth_data["algorithm"])
    return encode_jwt


def get_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Токен не найден!")
    return token


async def get_current_user(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)):
    try:
        auth_data = settings.get_auth_data
        payload = jwt.decode(token, key=auth_data["secret_key"], algorithms=auth_data["algorithm"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен не валидный!")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не найден ID пользователя!")
    query = select(User).where(User.id == int(user_id))
    try:
        user = await db.execute(query)
        return user.scalar_one_or_none()
    except Exception as e:
        print(f"Пользователь не найден: {e}")
        raise HTTPException(status_code=401, detail="Пользователь не найден!")
  

async def get_curent_admin_user(user: User = Depends(get_current_user)):
    if user.is_admin:
        return user
    raise HTTPException(status_code=403, detail="Недостаточно прав!")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(5, ge=1, le=20, description="Количество записей на странице")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size

    
SessionDep = Annotated[AsyncSession, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]
AdminUserDep = Annotated[User, Depends(get_curent_admin_user)]
PagninationDep = Annotated[PaginationParams, Depends(PaginationParams)]