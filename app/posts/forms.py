from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, SelectChoice
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

from app import db
from app.users.models import User

CATEGORIES = [
    SelectChoice('news', 'Новини'),
    SelectChoice('publication', 'Публікація'),
    SelectChoice('tech', 'Технології'),
    SelectChoice('other', 'Інше'),
]


class PostForm(FlaskForm):
    title = StringField(
        'Заголовок',
        validators=[
            DataRequired(message="Введіть заголовок поста"),
            Length(min=2, max=150, message="Заголовок має містити від 2 до 150 символів")
        ]
    )
    content = TextAreaField(
        'Текст поста',
        render_kw={"rows": 6, "cols": 40},
        validators=[DataRequired(message="Введіть текст поста")]
    )
    is_active = BooleanField('Активний пост', default=True)  # Чекбокс для відмітки активності поста
    publish_date = DateTimeLocalField(
        'Дата публікації',
        format="%Y-%m-%dT%H:%M",
        default=datetime.now,  # Поле для вибору дати публікації
        validators=[DataRequired(message="Вкажіть дату та час публікації")]
    )
    category = SelectField(
        'Категорія',
        choices=CATEGORIES,
        validators=[DataRequired(message="Оберіть категорію")]
    )
    author_id = SelectField('Автор', coerce=int, validators=[DataRequired(message="Оберіть автора")])
    submit = SubmitField('Зберегти')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Список авторів із БД (синтаксис SQLAlchemy 2.0)
        users = db.session.scalars(db.select(User).order_by(User.id)).all()
        self.author_id.choices = [SelectChoice(user.id, user.username) for user in users]
