from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, ValidationError

from app import db
from .models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Це обов'язкове поле"),
        Length(min=4, max=14, message="Довжина імені має бути від 4 до 14 символів"),
        Regexp(r'^[A-Za-z][A-Za-z0-9_.]*$',
               message="Ім'я має починатися з літери та містити лише літери, цифри, крапки або підкреслення")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Це обов'язкове поле"),
        Email(message="Некоректний формат email")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Це обов'язкове поле"),
        Length(min=6, message="Пароль має містити щонайменше 6 символів")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Це обов'язкове поле"),
        EqualTo('password', message="Паролі не збігаються")
    ])
    submit = SubmitField('Sign up')

    def validate_username(self, field):
        if db.session.scalar(db.select(User).filter_by(username=field.data)):
            raise ValidationError(f"Користувач з іменем {field.data} вже існує")

    def validate_email(self, field):
        if db.session.scalar(db.select(User).filter_by(email=field.data)):
            raise ValidationError(f"Користувач з email {field.data} вже існує")


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Це обов'язкове поле"),
        Email(message="Некоректний формат email")
    ])
    password = PasswordField('Password', validators=[DataRequired(message="Це обов'язкове поле")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
