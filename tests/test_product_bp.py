import unittest
from app import create_app

class FlaskProductTestCase(unittest.TestCase):
    def setUp(self):
        """Налаштування клієнта тестування перед кожним тестом."""
        self.app = create_app("testing")
        self.client = self.app.test_client()

    def test_products_list_page(self):
        """Тест маршруту /products/ (список товарів)."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        # Перевіряємо, чи є на сторінці назви товарів (у байтовому форматі)
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"Phone", response.data)

    def test_product_detail_page(self):
        """Тест маршруту /products/<id> (деталі конкретного товару)."""
        response = self.client.get("/products/1")
        self.assertEqual(response.status_code, 200)
        # Перевіряємо деталі першого товару
        self.assertIn(b"Laptop", response.data)
        self.assertIn(b"1200", response.data)

    def test_product_not_found(self):
        """Тест на неіснуючий товар (помилка 404)."""
        response = self.client.get("/products/999")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()