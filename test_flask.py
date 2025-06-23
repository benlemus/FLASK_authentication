from unittest import TestCase
from app import app
from models import db, User, Feedback
from flask import session

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_test_db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True

app.config['WTF_CSRF_ENABLED'] = False

with app.app_context():
    db.drop_all()
    db.create_all()

class TestRoutes(TestCase):
    def setUp(self):
        with app.app_context():
            db.session.rollback()
            Feedback.query.delete()
            db.session.commit()
            User.query.delete()
            db.session.commit()

            user1 = User.register('test_username1', 'test_password1', 'test_email1@testing.com', 'test_first_name1', 'test_last_name1', False)

            user2 = User.register('test_username2', 'test_password2', 'test_email2@testing.com', 'test_first_name2', 'test_last_name2', True)

            feedback1 = Feedback(title='Test_title1', content='this is a feedback test 1.', username='test_username1')

            feedback2 = Feedback(title='Test_title2', content='this is a feedback test 2.', username='test_username2')

            db.session.add_all([user1, user2])
            db.session.add_all([feedback1, feedback2])
            db.session.commit()

            self.feedback1_id = feedback1.id
            self.feedback2_id = feedback2.id

    def tearDown(self):
        with app.app_context():
            db.session.rollback()
            Feedback.query.delete()
            db.session.commit()
            User.query.delete()
            db.session.commit()

    def test_home_page(self):
        with app.test_client() as client:
            res = client.get('/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            
            self.assertIn('<title>Register</title>', html)

    def test_user_registration_get(self):
        with app.test_client() as client:
            res = client.get('/register')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form action="" method="POST">', html)
            self.assertIn('form_username', html)
            self.assertIn('form_password', html)
            self.assertIn('email', html)
            self.assertIn('first_name', html)
            self.assertIn('last_name', html)
            self.assertIn('admin_code', html)

    def test_user_registration_post_no_admin(self):
        with app.test_client() as client:
            data = {
                'form_username': 'NewTestUsername',
                'form_password': 'NewTestPassword',
                'email': 'newTest@testing.com',
                'first_name': 'NewFirstNameTest',
                'last_name': 'NewLastNameTest',
                'admin_code': ''
            }
            res = client.post('/register', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>NewTestUsername</h1>', html)
            self.assertEqual(session['username'], 'NewTestUsername')

            u = User.query.get_or_404('NewTestUsername')
            self.assertIsNotNone(u)
            self.assertEqual('NewFirstNameTest', u.first_name)
            self.assertFalse(u.is_admin)

    def test_user_registration_post_admin(self):
        with app.test_client() as client:
            data = {
                'form_username': 'NewTestUsername',
                'form_password': 'NewTestPassword',
                'email': 'newTest@testing.com',
                'first_name': 'NewFirstNameTest',
                'last_name': 'NewLastNameTest',
                'admin_code': '123'
            }
            res = client.post('/register', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>NewTestUsername</h1>', html)
            self.assertEqual(session['username'], 'NewTestUsername')

            u = User.query.get_or_404('NewTestUsername')
            self.assertIsNotNone(u)
            self.assertEqual('NewFirstNameTest', u.first_name)
            self.assertTrue(u.is_admin)

    def test_login_get(self):
        with app.test_client() as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Login</h1>', html)
            self.assertIn('form_username', html)
            self.assertIn('form_password', html)

    def test_login_post(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username1',
                'form_password': 'test_password1',
            }

            res = client.post('/login', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('test_username1', html)

            u = User.query.get_or_404('test_username1')
            self.assertIsNotNone(u)
            self.assertEqual('test_first_name1', u.first_name)
            self.assertFalse(u.is_admin)

    def test_user_page(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username1',
                'form_password': 'test_password1',
            }
            login = client.post('login', data=data) 

            self.assertIsNotNone(session['username'])

            res = client.get('/users/test_username1')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>test_username1</h1>', html)

            self.assertIsNotNone(session['username'])
            self.assertEqual('test_username1', session['username'])
            self.assertIn('this is a feedback test 1.', html)
    
    def test_user_logout(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username1',
                'form_password': 'test_password1',
            }
            login = client.post('login', data=data) 

            self.assertIsNotNone(session['username'])

            res = client.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>New User Registration</h1>', html)

    def test_delete_user(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username2',
                'form_password': 'test_password2',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            res = client.get('/users/test_username2/delete', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>New User Registration</h1>', html)

    def test_feedback_update_get(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username2',
                'form_password': 'test_password2',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            res = client.get(f'/feedback/{self.feedback2_id}/update')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Edit Feedback</h1>', html)
    
    def test_feedback_update_post(self):
        #TESTING AS ADMIN
        with app.test_client() as client:
            data = {
                'form_username': 'test_username2',
                'form_password': 'test_password2',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            data = {
                'content': 'update feedback test'
            }

            res = client.post(f'/feedback/{self.feedback1_id}/update', data=data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('update feedback test', html)

    def test_feedback_delete(self):
        #TESTING AS ADMIN
        with app.test_client() as client:
            data = {
                'form_username': 'test_username2',
                'form_password': 'test_password2',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            res = client.get(f'/feedback/{self.feedback1_id}/delete', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>test_username1</h1>', html)

    def test_feedback_add_get(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username1',
                'form_password': 'test_password1',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            res = client.get('/users/test_username1/feedback/add')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('title', html)
            self.assertIn('content', html)


    def test_feedback_add_post(self):
        with app.test_client() as client:
            data = {
                'form_username': 'test_username1',
                'form_password': 'test_password1',
            }
            login = client.post('login', data=data)

            self.assertIsNotNone(session['username'])

            feedback_data = {
                'title': 'testing add feedback title',
                'content': 'testing add feedback content',
                'username': 'test_username1'
            }

            res = client.post('/users/test_username1/feedback/add', data=feedback_data, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Testing add feedback title', html)

    def test_404_page(self):
        with app.test_client() as client:
            res = client.get('/doesnotexist')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 404)
            self.assertIn('<h3>404 Not found!</h3>', html)
