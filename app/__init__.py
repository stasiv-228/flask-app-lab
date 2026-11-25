import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


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
    migrate.init_app(app, db)

    # Реєстрація блюпринтів
    from .views import main_bp
    app.register_blueprint(main_bp)

    from .users import users_bp
    app.register_blueprint(users_bp)

    from .products import products_bp
    app.register_blueprint(products_bp)

    # Обробник помилки 404
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    return app
