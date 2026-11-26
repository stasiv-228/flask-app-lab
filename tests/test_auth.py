import unittest

from flask_login import current_user

from app import create_app, db
from app.users.models import User


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def create_user(self, username="oscar", email="oscar@gmail.com", password="secret1"):
        with self.app.app_context():
            user = User(username=username, email=email)
            user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return user.id

    def register(self, **kwargs):
        data = {
            "username": "oscar",
            "email": "oscar@gmail.com",
            "password": "secret1",
            "confirm_password": "secret1",
        }
        data.update(kwargs)
        return self.client.post("/register", data=data, follow_redirects=True)

    def login(self, email="oscar@gmail.com", password="secret1", **kwargs):
        return self.client.post("/login", data={"email": email, "password": password}, **kwargs)

    # ---------- Views Tests ----------
    def test_register_page_loads(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="username"', response.data)
        self.assertIn(b'name="email"', response.data)
        self.assertIn(b'name="confirm_password"', response.data)

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="email"', response.data)
        self.assertIn(b'name="password"', response.data)
        self.assertIn(b'name="remember"', response.data)

    # ---------- Реєстрація ----------
    def test_register_saves_user_with_hashed_password(self):
        response = self.register()
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно створено".encode(), response.data)

        with self.app.app_context():
            user = db.session.scalar(db.select(User).filter_by(username="oscar"))
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "oscar@gmail.com")
            self.assertNotEqual(user.password, "secret1")
            self.assertTrue(user.password.startswith("$2b$"))
            self.assertTrue(user.check_password("secret1"))
            self.assertFalse(user.check_password("wrong"))

    def test_register_redirects_to_login(self):
        response = self.client.post("/register", data={
            "username": "oscar", "email": "oscar@gmail.com",
            "password": "secret1", "confirm_password": "secret1",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_register_duplicate_username_and_email(self):
        self.create_user()
        response = self.register()
        self.assertIn("Користувач з іменем oscar вже існує".encode(), response.data)
        self.assertIn("Користувач з email oscar@gmail.com вже існує".encode(), response.data)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(User.id))), 1)

    def test_register_invalid_data(self):
        response = self.register(username="1x", email="not-an-email", password="123", confirm_password="456")
        html = response.get_data(as_text=True)
        self.assertIn("Некоректний формат email", html)
        self.assertIn("Паролі не збігаються", html)
        self.assertIn("щонайменше 6 символів", html)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(User.id))), 0)

    # ---------- Вхід і вихід ----------
    def test_login_success(self):
        self.create_user()
        with self.client:
            response = self.login(follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Welcome, oscar!", response.data)
            self.assertIn(b"oscar@gmail.com", response.data)
            self.assertTrue(current_user.is_authenticated)
            self.assertEqual(current_user.username, "oscar")

    def test_login_wrong_password(self):
        self.create_user()
        with self.client:
            response = self.login(password="wrong-password", follow_redirects=True)
            self.assertIn("Невірний email або пароль".encode(), response.data)
            self.assertFalse(current_user.is_authenticated)

    def test_login_unknown_email(self):
        response = self.login(email="nobody@gmail.com", follow_redirects=True)
        self.assertIn("Невірний email або пароль".encode(), response.data)

    def test_logout(self):
        self.create_user()
        self.login()
        with self.client:
            response = self.client.get("/logout", follow_redirects=True)
            self.assertIn("успішно вийшли".encode(), response.data)
            self.assertFalse(current_user.is_authenticated)
        self.assertEqual(self.client.get("/account").status_code, 302)

    # ---------- Захист сторінок (login_required) ----------
    def test_account_requires_login(self):
        response = self.client.get("/account")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login?next=", response.headers["Location"])

    def test_users_list_requires_login(self):
        response = self.client.get("/users", follow_redirects=True)
        self.assertIn("Будь ласка, увійдіть".encode(), response.data)

    def test_login_redirects_to_next_page(self):
        self.create_user()
        response = self.client.post("/login?next=/users", data={"email": "oscar@gmail.com", "password": "secret1"})
        self.assertEqual(response.headers["Location"], "/users")

    def test_users_list_shows_users_and_count(self):
        self.create_user()
        self.create_user(username="bella", email="bella@gmail.com")
        self.login()
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Users List (2)", response.data)
        self.assertIn(b"bella@gmail.com", response.data)

    # ---------- Поведінка для авторизованих ----------
    def test_authenticated_user_redirected_from_register_and_login(self):
        self.create_user()
        self.login()
        self.assertTrue(self.client.get("/register").headers["Location"].endswith("/account"))
        self.assertTrue(self.client.get("/login").headers["Location"].endswith("/account"))

    def test_navbar_changes_after_login(self):
        response = self.client.get("/login")
        self.assertIn("Реєстрація".encode(), response.data)
        self.assertNotIn("Вихід".encode(), response.data)

        self.create_user()
        self.login()
        response = self.client.get("/account")
        self.assertIn("Вихід".encode(), response.data)
        self.assertIn("Профіль (oscar)".encode(), response.data)
        self.assertNotIn("Реєстрація".encode(), response.data)


if __name__ == "__main__":
    unittest.main()
