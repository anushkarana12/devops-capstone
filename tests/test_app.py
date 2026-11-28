
import unittest
import sqlite3
import tempfile
import os
import app as app_module
from werkzeug.security import generate_password_hash


class TaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_tasks.db")

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

        self.original_get_db = app_module.get_db
        self.original_username = app_module.ADMIN_USERNAME
        self.original_password_hash = app_module.ADMIN_PASSWORD_HASH
        self.original_testing = app_module.app.config.get("TESTING")
        self.original_secret_key = app_module.app.config.get("SECRET_KEY")
        self.original_csrf_enabled = app_module.app.config.get(
            "WTF_CSRF_ENABLED", True
        )

        app_module.ADMIN_USERNAME = "admin"
        app_module.ADMIN_PASSWORD_HASH = generate_password_hash("testpass123")

        app_module.app.config["TESTING"] = True
        app_module.app.config["SECRET_KEY"] = "test-secret-key"

        # Disable CSRF validation only during automated tests.
        app_module.app.config["WTF_CSRF_ENABLED"] = False

        def test_get_db():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

        app_module.get_db = test_get_db
        self.client = app_module.app.test_client()

        self.client.post(
            "/login",
            data={"username": "admin", "password": "testpass123"}
        )

    def tearDown(self):
        app_module.get_db = self.original_get_db
        app_module.ADMIN_USERNAME = self.original_username
        app_module.ADMIN_PASSWORD_HASH = self.original_password_hash

        app_module.app.config["TESTING"] = self.original_testing
        app_module.app.config["SECRET_KEY"] = self.original_secret_key
        app_module.app.config["WTF_CSRF_ENABLED"] = (
            self.original_csrf_enabled
        )

        self.temp_dir.cleanup()

    def test_login(self):
        client = app_module.app.test_client()

        response = client.post(
            "/login",
            data={"username": "admin", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)

        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        client = app_module.app.test_client()

        response = client.get("/")
        self.assertEqual(response.status_code, 302)

        response = client.get("/api/tasks")
        self.assertEqual(response.status_code, 302)

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task Management System", response.data)

    def test_add_task(self):
        response = self.client.post(
            "/add",
            data={"title": "Test Task"}
        )
        self.assertEqual(response.status_code, 302)

        api_response = self.client.get("/api/tasks")
        self.assertEqual(api_response.status_code, 200)
        self.assertEqual(
            api_response.json["tasks"][0]["title"],
            "Test Task"
        )

    def test_api_tasks(self):
        self.client.post(
            "/add",
            data={"title": "API Test Task"}
        )

        response = self.client.get("/api/tasks")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["tasks"]), 1)
        self.assertEqual(
            response.json["tasks"][0]["title"],
            "API Test Task"
        )

    def test_delete_task(self):
        self.client.post(
            "/add",
            data={"title": "Delete Test Task"}
        )

        api_response = self.client.get("/api/tasks")
        task_id = api_response.json["tasks"][0]["id"]

        response = self.client.post(f"/delete/{task_id}")
        self.assertEqual(response.status_code, 302)

        api_response = self.client.get("/api/tasks")
        self.assertEqual(len(api_response.json["tasks"]), 0)

    def test_update_task(self):
        self.client.post(
            "/add",
            data={"title": "Old Task"}
        )

        api_response = self.client.get("/api/tasks")
        task_id = api_response.json["tasks"][0]["id"]

        response = self.client.post(
            f"/update/{task_id}",
            data={"title": "Updated Task"}
        )
        self.assertEqual(response.status_code, 302)

        api_response = self.client.get("/api/tasks")

        self.assertEqual(
            api_response.json["tasks"][0]["title"],
            "Updated Task"
        )

    def test_empty_task(self):
        response = self.client.post(
            "/add",
            data={"title": "   "}
        )
        self.assertEqual(response.status_code, 400)

    def test_update_invalid_task(self):
        response = self.client.post(
            "/update/9999",
            data={"title": "Updated Task"}
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_invalid_task(self):
        response = self.client.post("/delete/9999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
