import unittest

from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.products.models import Product, Category


class ProductModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def test_product_defaults(self):
        product = Product(name="Pc", price=700)
        db.session.add(product)
        db.session.commit()

        self.assertTrue(product.active)
        self.assertIsNotNone(product.created_at)
        self.assertIsNone(product.category)
        self.assertEqual(repr(product), "<Product Pc - $700.0>")

    def test_category_products_relationship(self):
        laptops = Category(name="Laptops")
        product = Product(name="Gaming Laptop", price=1500.00, active=False, category=laptops)
        db.session.add_all([laptops, product])
        db.session.commit()

        self.assertEqual(product.category.name, "Laptops")
        self.assertEqual(product.category_id, laptops.id)
        self.assertEqual(laptops.products, [product])
        self.assertFalse(product.active)

    def test_category_has_many_products(self):
        books = Category(name="Books")
        db.session.add_all([
            Product(name="Novel", price=20.0, category=books),
            Product(name="Poems", price=15.0, category=books),
        ])
        db.session.commit()

        stmt = db.select(Product).join(Product.category).where(Category.name == "Books")
        names = sorted(p.name for p in db.session.scalars(stmt))
        self.assertEqual(names, ["Novel", "Poems"])

    def test_category_name_is_unique(self):
        db.session.add_all([Category(name="Books"), Category(name="Books")])
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_constraint_names_follow_naming_convention(self):
        self.assertIn("fk_products_category_id_categories", {fk.constraint.name for fk in Product.__table__.foreign_keys})
        self.assertEqual(Category.__table__.primary_key.name, "pk_categories")


if __name__ == "__main__":
    unittest.main()
