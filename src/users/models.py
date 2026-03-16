from src.core.database import Default, str_unique
from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from src.posts.models import Post, Bookmark, Like, Comment

if TYPE_CHECKING:
    from src.posts.models import Post, Bookmark, Like, Comment


class User(Default):
    __tablename__ = "users"

    username: Mapped[str_unique] = mapped_column(index=True)
    email: Mapped[str_unique] = mapped_column(index=True)
    password: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=text("false"), nullable=False)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")
    bookmarks: Mapped[list["Bookmark"]] = relationship("Bookmark", back_populates="user")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="user")