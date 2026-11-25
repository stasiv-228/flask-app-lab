import io
import os
import tempfile
import unittest
from tinydb import TinyDB
from app import create_app
from app.products import views as product_views


class ProductCRUDTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_db = TinyDB(os.path.join(self.temp_dir.name, 'test_products.json'))
        product_views.products_table = self.test_db.table('products')
        product_views.UPLOAD_FOLDER = self.temp_dir.name

    def tearDown(self):
        self.test_db.close()
        self.temp_dir.cleanup()

    def test_create_and_read_product(self):
        data = {
            'name': 'Тестовий монітор',
            'content': '27-дюймовий IPS монітор 144 Гц',
            'price': '450.50',
            'category': 'electronics',
            'quantity': '7',
            'image': (io.BytesIO(b"fake image bytes"), 'monitor.png')
        }
        response = self.client.post('/products/add', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(product_views.products_table), 1)

        item = product_views.products_table.all()[0]
        self.assertEqual(item['name'], 'Тестовий монітор')
        self.assertIsNotNone(item['image'])

        detail_resp = self.client.get(f"/products/{item['id']}")
        self.assertEqual(detail_resp.status_code, 200)
        self.assertIn('Тестовий монітор'.encode('utf-8'), detail_resp.data)

    def test_update_product(self):
        product_views.products_table.insert({
            'id': 1,
            'name': 'Стара назва',
            'content': 'Старий опис',
            'price': 100.00,
            'category': 'books',
            'quantity': 2,
            'image': None,
            'created_at': '2026-11-25 12:00:00'
        })

        update_data = {
            'name': 'Нова назва',
            'content': 'Оновлений опис',
            'price': '199.99',
            'category': 'books',
            'quantity': '5'
        }
        resp = self.client.post('/products/1/edit', data=update_data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        updated = product_views.products_table.all()[0]
        self.assertEqual(updated['name'], 'Нова назва')
        self.assertEqual(updated['price'], 199.99)
        self.assertEqual(updated['created_at'], '2026-11-25 12:00:00')

    def test_delete_product(self):
        product_views.products_table.insert({
            'id': 1,
            'name': 'Товар на видалення',
            'content': 'Опис',
            'price': 50.00,
            'category': 'other',
            'quantity': 1,
            'image': None,
            'created_at': '2026-11-25 12:00:00'
        })

        resp = self.client.post('/products/1/delete', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(product_views.products_table), 0)

    def test_not_found_product(self):
        resp = self.client.get('/products/999')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()