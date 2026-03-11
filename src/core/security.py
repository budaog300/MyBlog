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
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    auth_data = settings.get_auth_data
    encode_jwt = jwt.encode(to_encode, auth_data["access_secret_key"], auth_data["algorithm"])
    return encode_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    auth_data = settings.get_auth_data
    encode_jwt = jwt.encode(to_encode, auth_data["refresh_secret_key"], auth_data["algorithm"])
    return encode_jwt


def generate_tokens(response: Response, data: dict) -> dict:
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True) 
    return {"access_token": access_token, "refresh_token": refresh_token} 


def get_access_token(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")
    return token


async def refresh_access_token(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> str:
    token = request.cookies.get("refresh_token")    
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token required")
    try:
        auth_data = settings.get_auth_data
        payload = jwt.decode(token, key=auth_data["refresh_secret_key"], algorithms=auth_data["algorithm"])
        if not payload.get("type"):
            raise HTTPException(401, "Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Не найден ID пользователя!")
        query = select(User).where(User.id == int(user_id))        
        user = await db.execute(query)
        if not user:
            raise HTTPException(401, "Пользователь не найден!")
        tokens = generate_tokens(response, {"sub": str(user_id)})
        return {"message": "Tokens refreshed", "access_token": tokens["access_token"], "refresh_token": tokens["refresh_token"]} 
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен не валидный!")


async def get_current_user(token: str = Depends(get_access_token), db: AsyncSession = Depends(get_db)):
    try:
        auth_data = settings.get_auth_data
        payload = jwt.decode(token, key=auth_data["access_secret_key"], algorithms=auth_data["algorithm"])    
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Не найден ID пользователя!")
        query = select(User).where(User.id == int(user_id))    
        user = await db.execute(query)
        return user.scalar_one_or_none()
    except JWTError:
        raise HTTPException(status_code=401, detail="Токен не валидный!")
  

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