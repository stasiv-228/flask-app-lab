import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })


db = SQLAlchemy(model_class=Base)
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_name=None):
    """Application factory: створює та налаштовує екземпляр застосунку"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Папка instance/ для файлу бази даних SQLite
    os.makedirs(app.instance_path, exist_ok=True)

    # Ініціалізація розширень
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Налаштування маршруту перенаправлення для неавторизованих користувачів
    login_manager.login_view = 'users.login'
    login_manager.login_message = 'Будь ласка, увійдіть, щоб отримати доступ до цієї сторінки.'
    login_manager.login_message_category = 'warning'

    # Реєстрація блюпринтів
    from .views import main_bp
    app.register_blueprint(main_bp)

    from .users import users_bp
    app.register_blueprint(users_bp)

    from .products import products_bp
    app.register_blueprint(products_bp)

    from .posts import post_bp
    app.register_blueprint(post_bp)

    # Обробник помилки 404
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app
