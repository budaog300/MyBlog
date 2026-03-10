from pydantic import BaseModel, EmailStr, Field


class AddUserSchema(BaseModel):
    username: str = Field(..., min_length=5, max_length=20, description="Введите логин пользователя")
    email: EmailStr = Field(..., min_length=10, description="Введите почту пользователя")
    password: str = Field(..., min_length=5, max_length=50, description="Введите пароль пользователя")


class LoginUserSchema(BaseModel):
    login: str = Field(..., description="Введите почту или логин пользователя")
    password: str = Field(..., min_length=5, max_length=50, description="Введите пароль пользователя")


class UserSchema(BaseModel):
    username: str
    email: str   
    is_admin: bool 