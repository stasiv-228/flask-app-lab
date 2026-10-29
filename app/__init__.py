from flask import Flask

app = Flask(__name__)
# app.config.from_pyfile("../config.py") # Поки закоментуємо, якщо config.py немає

from . import views