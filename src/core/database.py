from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from typing import Annotated
from src.core.config import settings


DATABASE_URL = settings.get_db_url
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, unique=True)]
str_unique = Annotated[str, mapped_column(nullable=False, unique=True)]


class Base(DeclarativeBase):
    __abstract__ = True

    def repr(self):
        _attrs = []
        if hasattr(self, "id"):
            _attrs.append(f"id={self.id}")
        else:
            for col in self.__table__.primary_key.columns:
                if hasattr(self, col.name):
                    _attrs.append(f"{col.name}={getattr(self, col.name)}")
        return f"{self.__class__.__name__} ({', '.join(_attrs)})"


class Default(Base):   
    __abstract__ = True
    
    id: Mapped[int_pk]
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=text("TIMEZONE('utc', now())"))


async def get_db():
    async with async_session() as session:
        yield session