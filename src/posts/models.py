from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from src.core.database import Base, Default, int_pk, str_unique
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.users.models import User


class Post(Default):
    __tablename__ = 'posts'

    title: Mapped[str] = mapped_column(index=True, nullable=False)
    content: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True, nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship("Tag", secondary="post_tags", back_populates="posts")
    bookmarks: Mapped[list["Bookmark"]] = relationship("Bookmark", back_populates="post")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post")
    user: Mapped["User"] = relationship("User", back_populates="posts")


class Category(Default):
    __tablename__ = "categories"

    name: Mapped[str_unique]
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="category")


class Tag(Default):
    __tablename__ = "tags"

    name: Mapped[str_unique] = mapped_column(index=True)
    posts: Mapped[list["Post"]] = relationship("Post", secondary="post_tags", back_populates="tags")


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Like(Base):
    __tablename__ = "likes"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), primary_key=True)

    post: Mapped["Post"] = relationship("Post", back_populates="likes")
    user: Mapped["User"] = relationship("User", back_populates="likes")


class Bookmark(Default):
    __tablename__ = "bookmarks"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    post: Mapped["Post"] = relationship("Post", back_populates="bookmarks")
    user: Mapped["User"] = relationship("User", back_populates="bookmarks")

    __table_args__ = (
        UniqueConstraint("post_id", "user_id"),
    )