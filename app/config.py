import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Завантажуємо змінні середовища з файлу .env у корені проєкту
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Config:
    """Базова конфігурація для всіх середовищ"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key-for-lab6'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Журналювання SQL-запитів: SQLALCHEMY_ECHO=1 у змінних середовища
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO') == '1'


class DevelopmentConfig(Config):
    """Конфігурація за замовчуванням у режимі розробки"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'data.sqlite')


class TestingConfig(Config):
    """Конфігурація для тестів із in-memory SQLite"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Конфігурація для продакшену"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'prod_data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
