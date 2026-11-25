from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductForm(FlaskForm):
    name = StringField(
        'Назва товару',
        validators=[
            DataRequired(message="Введіть назву товару"),
            Length(min=3, max=100, message="Назва має містити щонайменше 3 символи")
        ]
    )
    content = TextAreaField(
        'Опис товару',
        render_kw={"rows": 5, "cols": 40},
        validators=[
            DataRequired(message="Введіть опис товару")
        ]
    )
    price = DecimalField(
        'Ціна (грн)',
        places=2,
        validators=[
            DataRequired(message="Введіть ціну товару"),
            NumberRange(min=0.01, message="Ціна має бути додатною (більше 0)")
        ]
    )
    category = SelectField(
        'Категорія',
        choices=[
            ('electronics', 'Електроніка'),
            ('clothing', 'Одяг'),
            ('books', 'Книги'),
            ('home', 'Дім та сад'),
            ('other', 'Інше')
        ],
        validators=[DataRequired(message="Оберіть категорію")]
    )
    quantity = IntegerField(
        'Кількість одиниць',
        validators=[
            DataRequired(message="Введіть кількість"),
            NumberRange(min=0, message="Кількість не може бути від'ємною")
        ]
    )
    image = FileField(
        'Зображення товару',
        validators=[
            FileAllowed(['png', 'jpg', 'jpeg'], message="Дозволені лише формати PNG, JPG або JPEG")
        ]
    )
    submit = SubmitField('Зберегти товар')