from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

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

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title}', category='{self.category}')>"
