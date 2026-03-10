import re
from pydantic import BaseModel, Field, field_validator, computed_field
from typing import Any
from datetime import datetime

from src.users.schemas import UserSchema


class AddPostSchema(BaseModel):
    title: str = Field(..., min_length=5, max_length=50, description="Заголовок поста")
    content: str = Field(..., min_length=20, max_length=500, description="Контент поста")
    category_id: int = Field(..., description="Категория поста")


class AddCategorySchema(BaseModel):
    name: str = Field(..., min_length=5, max_length=50, description="Название категории")


class AddTagSchema(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Название тега")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Any):
        pattern = r"^\#\w+$"
        if not re.match(pattern, v):
            raise ValueError([f"Неправильный формат тега {v}"])
        return v
    

class OutCategorySchema(BaseModel):
    name: str


class LikeSchema(BaseModel):
    post_id: int
    user_id: int
    

class OutTagSchema(BaseModel):
    name: str
    

class OutPostSchema(BaseModel):
    title: str
    content: str
    created_at: datetime
    likes: list[LikeSchema] = []
    category: OutCategorySchema
    # tags: OutTagSchema
    user: UserSchema   

    @computed_field
    @property
    def likes_count(self) -> int:
        return len(self.likes) if self.likes else 0