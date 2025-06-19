from unittest import TestCase
from app import app
from models import db, User, Feedback

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_test_db'
# app.config['SQLALCHEMY_ECHO'] = False
# app.config['TESTING'] = True

class TestRoutes(TestCase):
    def setUp(self):
        with app.app_context():
            User.query.delete()

    def tearDown(self):
        pass

    def test_home_page(self):
        with app.test_client() as client:
            res = client.get('/')

            self.assertEqual(res.status_code, 200)

    def test_username_in_session(self):
        pass