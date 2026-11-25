"""Insert data into products table

Revision ID: f5e6377b76b2
Revises: 1177c90570ff
Create Date: 2026-11-26 01:46:25.700645

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = 'f5e6377b76b2'
down_revision = '1177c90570ff'
branch_labels = None
depends_on = None

CATEGORIES = ['Electronics', 'Books', 'Clothing']

# (назва товару, ціна, активний, назва категорії)
PRODUCTS = [
    ('Laptop', 1200.0, True, 'Electronics'),
    ('Smartphone LG', 800.0, True, 'Electronics'),
    ('Novel', 20.0, True, 'Books'),
    ('T-Shirt', 25.0, False, 'Clothing'),
]


def upgrade():
    # --- Опис таблиці для bulk_insert ---
    categories_table = table('categories', column('id', sa.Integer), column('name', sa.String))

    # --- Вставка категорій ---
    op.bulk_insert(categories_table, [{'name': name} for name in CATEGORIES])

    # --- Вставка продуктів ---
    # category_id беремо за назвою категорії, а не жорстко заданим id,
    # бо в таблиці categories вже можуть бути інші записи
    conn = op.get_bind()
    for name, price, active, category in PRODUCTS:
        conn.execute(
            sa.text(
                "INSERT INTO products (name, price, active, category_id) "
                "SELECT :name, :price, :active, id FROM categories WHERE name = :category"
            ),
            {'name': name, 'price': price, 'active': active, 'category': category},
        )


def downgrade():
    # Видаляємо тільки вставлені продукти та категорії
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM products WHERE name IN :names").bindparams(
            sa.bindparam('names', expanding=True)),
        {'names': [p[0] for p in PRODUCTS]},
    )
    conn.execute(
        sa.text("DELETE FROM categories WHERE name IN :names").bindparams(
            sa.bindparam('names', expanding=True)),
        {'names': CATEGORIES},
    )
