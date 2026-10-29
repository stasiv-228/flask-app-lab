from flask import Blueprint

# Створюємо Blueprint з префіксом /products
products_bp = Blueprint('products', __name__, template_folder='templates', url_prefix='/products')

from . import views