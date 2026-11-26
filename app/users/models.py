from flask_login import UserMixin
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app import db, bcrypt, login_manager


@login_manager.user_loader
def user_loader(user_id):
    """Завантаження поточного користувача за id, збереженим у сесії"""
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def hash_password(self, password: str) -> None:
        """Хешує пароль за допомогою Flask-Bcrypt і зберігає хеш у полі password"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Перевіряє пароль порівнянням із збереженим хешем"""
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f"User('{self.username}', '{self.email}')"
