from flask import Flask

app = Flask(__name__)

from . import views

# Реєстрація Blueprint users
from .users import users_bp
app.register_blueprint(users_bp)