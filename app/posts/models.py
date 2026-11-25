from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Enum, Boolean, ForeignKey, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db

CATEGORIES = ('news', 'publication', 'tech', 'other')


def utcnow():
    """Поточний час UTC (аналог datetime.utcnow)"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Post(db.Model):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    category: Mapped[str] = mapped_column(
        Enum(*CATEGORIES, name='post_category'),
        default='other'
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', category='{self.category}')>"
