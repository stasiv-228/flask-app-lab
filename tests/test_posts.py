import unittest
from datetime import datetime

from app import create_app, db
from app.posts.models import Post, Tag
from app.users.models import User


class PostTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.client = self.app.test_client()

        # Створення бази в контексті додатка
        with self.app.app_context():
            db.create_all()
            db.session.add_all([
                User(username="vlad", email="vlad@example.com", password="hash1"),
                User(username="student", email="student@example.com", password="hash2"),
                Tag(name="Python"), Tag(name="Flask"), Tag(name="ORM"),
            ])
            db.session.commit()

    def tearDown(self):
        # Очищення бази після кожного тесту
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

    def create_post(self, **kwargs):
        """Допоміжний метод: додає пост у БД та повертає його id"""
        data = {
            "title": "Test post",
            "content": "Test content",
            "category": "news",
        }
        data.update(kwargs)
        with self.app.app_context():
            post = Post(**data)
            db.session.add(post)
            db.session.commit()
            return post.id

    def form_data(self, **kwargs):
        data = {
            "title": "My first post",
            "content": "This is TDD!",
            "is_active": "y",
            "publish_date": "2026-11-20T10:30",
            "category": "tech",
            "author_id": "2",
        }
        data.update(kwargs)
        return data

    # ---------- Create ----------
    def test_create_post_page_loads(self):
        response = self.client.get("/post/create")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="title"', response.data)
        self.assertIn(b'name="author_id"', response.data)
        # список авторів завантажується з БД
        self.assertIn(b'<option value="1">vlad</option>', response.data)
        self.assertIn(b'<option value="2">student</option>', response.data)

    def test_create_post(self):
        with self.app.app_context():
            response = self.client.post("/post/create", data=self.form_data(), follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("успішно додано".encode(), response.data)

            post = db.session.scalar(db.select(Post).filter_by(title="My first post"))
            self.assertIsNotNone(post)
            self.assertEqual(post.content, "This is TDD!")
            self.assertEqual(post.category, "tech")
            self.assertTrue(post.is_active)
            self.assertEqual(post.posted, datetime(2026, 11, 20, 10, 30))
            self.assertEqual(post.user.username, "student")

    def test_create_post_redirects_to_list(self):
        response = self.client.post("/post/create", data=self.form_data())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/post/"))

    def test_create_post_unknown_author(self):
        response = self.client.post("/post/create", data=self.form_data(author_id="99"))
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(Post.id))), 0)

    def test_create_post_invalid_data(self):
        response = self.client.post("/post/create", data=self.form_data(title=""), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(db.session.scalar(db.select(db.func.count(Post.id))), 0)

    # ---------- Read ----------
    def test_list_posts_active_sorted_by_date_desc(self):
        self.create_post(title="Older Post", posted=datetime(2026, 1, 1))
        self.create_post(title="Newer Post", posted=datetime(2026, 6, 1))
        self.create_post(title="Hidden Post", is_active=False)

        response = self.client.get("/post/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Newer Post", html)
        self.assertIn("Older Post", html)
        self.assertNotIn("Hidden Post", html)
        self.assertLess(html.index("Newer Post"), html.index("Older Post"))

    def test_list_posts_truncates_content(self):
        self.create_post(content="A" * 150)
        response = self.client.get("/post/")
        self.assertNotIn(b"A" * 150, response.data)
        self.assertIn(b"A" * 100, response.data)

    def test_detail_post(self):
        post_id = self.create_post(title="Detail title", content="Full content of the post", user_id=1)
        response = self.client.get(f"/post/{post_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Detail title", response.data)
        self.assertIn(b"Full content of the post", response.data)
        self.assertIn(b"vlad", response.data)

    def test_detail_post_not_found(self):
        response = self.client.get("/post/999")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"404", response.data)

    # ---------- Update ----------
    def test_update_post_form_prefilled(self):
        post_id = self.create_post(title="Old title", posted=datetime(2026, 3, 15, 9, 45), user_id=2)
        response = self.client.get(f"/post/{post_id}/update")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'value="Old title"', response.data)
        self.assertIn(b'value="2026-03-15T09:45"', response.data)
        self.assertIn(b'<option selected value="2">student</option>', response.data)

    def test_update_post(self):
        post_id = self.create_post(title="Old title", content="Old content", category="news", user_id=2)

        response = self.client.post(
            f"/post/{post_id}/update",
            data=self.form_data(title="New title", content="New content", category="other",
                                publish_date="2026-10-01T12:00", author_id="1"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно оновлено".encode(), response.data)

        with self.app.app_context():
            post = db.session.get(Post, post_id)
            self.assertEqual(post.title, "New title")
            self.assertEqual(post.content, "New content")
            self.assertEqual(post.category, "other")
            self.assertEqual(post.posted, datetime(2026, 10, 1, 12, 0))
            self.assertEqual(post.user_id, 1)

    def test_update_post_not_found(self):
        response = self.client.post("/post/999/update", data=self.form_data())
        self.assertEqual(response.status_code, 404)

    # ---------- Delete ----------
    def test_delete_post_confirm_page(self):
        post_id = self.create_post(title="Post to delete")
        response = self.client.get(f"/post/{post_id}/delete")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Post to delete", response.data)
        self.assertIn(b'method="POST"', response.data)
        with self.app.app_context():
            self.assertIsNotNone(db.session.get(Post, post_id))

    def test_delete_post(self):
        post_id = self.create_post(title="Post to delete")
        response = self.client.post(f"/post/{post_id}/delete", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("успішно видалено".encode(), response.data)
        with self.app.app_context():
            self.assertIsNone(db.session.get(Post, post_id))

    def test_delete_post_not_found(self):
        response = self.client.post("/post/999/delete")
        self.assertEqual(response.status_code, 404)

    # ---------- Tags (Many-to-Many) ----------
    def test_create_post_form_has_tags(self):
        response = self.client.get("/post/create")
        self.assertIn(b'name="tags"', response.data)
        self.assertIn(b'multiple', response.data)
        self.assertIn(b'<option value="1">Python</option>', response.data)

    def test_create_post_with_tags(self):
        self.client.post("/post/create", data=self.form_data(tags=["1", "3"]), follow_redirects=True)
        with self.app.app_context():
            post = db.session.scalar(db.select(Post).filter_by(title="My first post"))
            self.assertEqual(sorted(tag.name for tag in post.tags), ["ORM", "Python"])
            python = db.session.get(Tag, 1)
            self.assertIn(post, python.posts)

    def test_create_post_without_tags(self):
        self.client.post("/post/create", data=self.form_data(), follow_redirects=True)
        with self.app.app_context():
            post = db.session.scalar(db.select(Post).filter_by(title="My first post"))
            self.assertEqual(post.tags, [])

    def test_update_post_tags(self):
        with self.app.app_context():
            post = Post(title="Tagged", content="Text", category="tech", user_id=1)
            post.tags.append(db.session.get(Tag, 1))
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = self.client.get(f"/post/{post_id}/update")
        self.assertIn(b'<option selected value="1">Python</option>', response.data)

        self.client.post(f"/post/{post_id}/update", data=self.form_data(tags=["2", "3"]))
        with self.app.app_context():
            post = db.session.get(Post, post_id)
            self.assertEqual(sorted(tag.name for tag in post.tags), ["Flask", "ORM"])

    def test_detail_post_shows_tags(self):
        with self.app.app_context():
            post = Post(title="Tagged", content="Text", category="tech", user_id=1)
            post.tags.extend([db.session.get(Tag, 1), db.session.get(Tag, 2)])
            db.session.add(post)
            db.session.commit()
            post_id = post.id

        response = self.client.get(f"/post/{post_id}")
        self.assertIn(b'class="post-tag">#Flask', response.data)
        self.assertIn(b'class="post-tag">#Python', response.data)

    # ---------- Errors ----------
    def test_404_page(self):
        response = self.client.get("/this-page-does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Сторінку не знайдено".encode(), response.data)


if __name__ == "__main__":
    unittest.main()
