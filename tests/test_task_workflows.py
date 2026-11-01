import os
import unittest

# Keep test data separate from the database used by the interactive UI.
os.environ["DATABASE_URL"] = "sqlite:///test-database.db"

from main import app
from app.models import ToDo, User, db


class TaskWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the real Flask application and its root route.
        app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY="test-only-secret",
        )
        cls.app = app

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        user = User(username="demo-user", password="demo-password")
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

        self.client = self.app.test_client()
        response = self.client.post(
            "/auth/login",
            data={"username": "demo-user", "password": "demo-password"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_task(self, description="Review the maintenance demo"):
        task = ToDo(description=description, id_user=self.user_id)
        db.session.add(task)
        db.session.commit()
        return task.id

    def test_create_task(self):
        response = self.client.post(
            "/todo/create",
            data={"description": "Prepare the demo"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Prepare the demo", response.data)

        task = ToDo.query.filter_by(description="Prepare the demo").first()
        self.assertIsNotNone(task)
        self.assertFalse(task.done)

    def test_new_task_is_rendered_as_pending(self):
        self.create_task()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'bg-primary rounded-pill fs-6">Pending</span>', response.data)
        self.assertNotIn(b'bg-success rounded-pill fs-6">Done</span>', response.data)

    def test_mark_task_done(self):
        task_id = self.create_task()

        response = self.client.post(
            f"/todo/done/{task_id}",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'bg-success rounded-pill fs-6">Done</span>', response.data)

        task = db.session.get(ToDo, task_id)
        self.assertIsNotNone(task)
        self.assertTrue(task.done)

    def test_completing_one_task_keeps_other_task_pending(self):
        completed_id = self.create_task("Task to complete")
        pending_id = self.create_task("Task to keep pending")

        response = self.client.post(
            f"/todo/done/{completed_id}",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Task to complete", response.data)
        self.assertIn(b"Task to keep pending", response.data)

        completed_task = db.session.get(ToDo, completed_id)
        pending_task = db.session.get(ToDo, pending_id)
        self.assertTrue(completed_task.done)
        self.assertFalse(pending_task.done)

    def test_delete_task(self):
        task_id = self.create_task()

        response = self.client.post(
            f"/todo/delete/{task_id}",
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(db.session.get(ToDo, task_id))


if __name__ == "__main__":
    unittest.main()
