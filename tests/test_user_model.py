import unittest
import time
from app import create_app, db
from app.models import Permission, Role, User, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='dog')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='dog')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verufication(self):
        u = User(password='dog')
        self.assertTrue(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cat'))

    def test_password_salts_are_random(self):
        u1 = User(password='dog')
        u2 = User(password='cat')
        self.assertTrue(u1.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='dog')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password='dog')
        u2 = User(password='cat')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token =u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def text_expired_confirmation_token(self):
        u = User(password='dog')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):
        u = User(password='dog')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(u.reset_password(token, 'cat'))
        self.assertTrue(u.verify_password('cat'))

    def test_invalid_reset_token(self):
        u1 = User(password='dog')
        u2 = User(password='cat')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_reset_token()
        self.assertFalse(u2.reset_password(token, 'bat'))
        self.assertTrue(u2.verify_password('cat'))

    def test_valid_email_change_token(self):
        u = User(email='gon@example.com', password='dog')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('kirua@example.com')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email=='kirua@example.com')

    def test_invalid_email_change_token(self):
        u1 = User(email='gon@example.com', password='dog')
        u2 = User(email='kirua@example.com', password='fox')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('kurapika@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email=='kirua@example.com')

    def test_duplicate_email_change_token(self):
        u1 = User(email='gon@example.com', password='dog')
        u2 = User(email='kirua@example.com', password='fox')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('gon@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email=='kirua@example.com')

    def test_roles_and_permissions(self):
        u = User(email='kirua@example.com', password='fox')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
