import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, abort, current_app
from werkzeug.utils import secure_filename
from tinydb import TinyDB, Query
from . import products_bp
from .forms import ProductForm

# Шлях до JSON-бази у папці data/ в корені проєкту
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

db = TinyDB(os.path.join(DATA_DIR, 'products.json'), ensure_ascii=False, indent=4)
products_table = db.table('products')
ProductQuery = Query()

# Папка для збереження зображень блюпринта
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_image(file_storage):
    """Зберігає файл з унікальним UUID-іменем та повертає відносний шлях для static"""
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file_storage.save(file_path)
    return f"uploads/{unique_name}"


def delete_image_file(image_rel_path):
    """Видаляє старий файл зображення з диска, якщо він існує"""
    if not image_rel_path:
        return
    full_path = os.path.join(os.path.dirname(__file__), 'static', image_rel_path)
    if os.path.exists(full_path):
        os.remove(full_path)


def seed_initial_products():
    """Заповнює базу початковими товарами, якщо вона ще порожня"""
    if len(products_table) == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        initial_items = [
            {
                "id": 1,
                "name": "Laptop",
                "content": "Потужний ноутбук з процесором Intel Core i7, 16 ГБ оперативної пам’яті та SSD на 512 ГБ.",
                "price": 1200.00,
                "category": "electronics",
                "quantity": 5,
                "image": None,
                "created_at": now
            },
            {
                "id": 2,
                "name": "Phone",
                "content": "Смартфон із 6.5-дюймовим OLED-дисплеєм, подвійною камерою та акумулятором на 5000 мА·год.",
                "price": 800.00,
                "category": "electronics",
                "quantity": 10,
                "image": None,
                "created_at": now
            },
            {
                "id": 3,
                "name": "PC",
                "content": "Настільний комп’ютер для ігор або роботи з графікою: RTX 4070, 32 ГБ RAM, 1 ТБ SSD.",
                "price": 1800.00,
                "category": "electronics",
                "quantity": 3,
                "image": None,
                "created_at": now
            }
        ]
        for item in initial_items:
            products_table.insert(item)


seed_initial_products()


@products_bp.route('/')
def list_products():
    """Перегляд списку всіх товарів (Read)"""
    all_products = products_table.all()
    return render_template('products/products.html', products=all_products)


@products_bp.route('/<int:product_id>')
def detail_product(product_id):
    """Перегляд детальної інформації про товар"""
    product = products_table.get(ProductQuery.id == product_id)
    if product is None:
        abort(404)
    return render_template('products/detail_product.html', product=product)


@products_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    """Додавання нового товару (Create)"""
    form = ProductForm()
    if form.validate_on_submit():
        all_items = products_table.all()
        next_id = max((item.get('id', 0) for item in all_items), default=0) + 1
        image_path = save_image(form.image.data)

        new_product = {
            "id": next_id,
            "name": form.name.data,
            "content": form.content.data,
            "price": round(float(form.price.data), 2),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        products_table.insert(new_product)
        flash(f"Товар «{new_product['name']}» успішно додано!", "success")
        return redirect(url_for('products.list_products'))

    if form.is_submitted() and not form.validate():
        flash("Помилка валідації! Перевірте введені дані.", "danger")

    return render_template('products/product_form.html', form=form, title="Додати новий товар")


@products_bp.route('/<int:product_id>/edit', methods=['GET', 'POST'])
def edit_product(product_id):
    """Редагування існуючого товару (Update)"""
    product = products_table.get(ProductQuery.id == product_id)
    if product is None:
        abort(404)

    form = ProductForm(data=product)
    if form.is_submitted() is False:
        form.image.data = None

    if form.validate_on_submit():
        image_path = product.get('image')
        if hasattr(form.image.data, 'filename') and form.image.data.filename:
            delete_image_file(image_path)
            image_path = save_image(form.image.data)

        updated_data = {
            "name": form.name.data,
            "content": form.content.data,
            "price": round(float(form.price.data), 2),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": image_path
        }
        products_table.update(updated_data, ProductQuery.id == product_id)
        flash(f"Товар «{form.name.data}» успішно оновлено!", "success")
        return redirect(url_for('products.detail_product', product_id=product_id))

    if form.is_submitted() and not form.validate():
        flash("Помилка валідації при редагуванні товару.", "danger")

    return render_template('products/product_form.html', form=form, title="Редагувати товар", product=product)


@products_bp.route('/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    """Видалення товару (Delete)"""
    product = products_table.get(ProductQuery.id == product_id)
    if product is None:
        abort(404)

    delete_image_file(product.get('image'))
    products_table.remove(ProductQuery.id == product_id)
    flash(f"Товар «{product['name']}» видалено.", "warning")
    return redirect(url_for('products.list_products'))