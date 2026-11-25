from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length

CATEGORIES = [
    ('news', 'Новини'),
    ('publication', 'Публікація'),
    ('tech', 'Технології'),
    ('other', 'Інше'),
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
    submit = SubmitField('Зберегти')
