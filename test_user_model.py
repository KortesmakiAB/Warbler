"""User model tests."""

# run these tests:  python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user = User.signup("testuser", "test@test.com", "HASHED_PASSWORD", None)
        user.id = 1111

        db.session.add(user)
        db.session.commit()

        # from solution code
        u = User.query.get(1111)    

        self.u = u


    def tearDown(self):
        """Clean up any fowled transaction."""

        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)


    def test_repr_method(self):
        """ Does __repr__ method work?"""

        self.assertEqual(self.u.__repr__(), "<User #1111: testuser, test@test.com>")


############################################################
# User class-methods tests

    def test_User_signup_valid(self):
        """Does User.signup successfully create a new user given valid credentials? """

        u2 = User.signup('testuser2', 'test2@test.com', 'test_pw2', None)
        u2.id = 1234567
        db.session.commit()

        test_u = User.query.get(1234567)

        self.assertIsInstance(test_u, User)
        self.assertEqual(test_u.username, 'testuser2')
        self.assertEqual(test_u.email, 'test2@test.com')
        self.assertNotEqual(test_u.password, 'test_pw2')
        # from solution code
        # Bcrypt strings should start with $2b$
        self.assertTrue(test_u.password.startswith("$2b$"))


    def test_User_signup_invalid(self):
        """Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        with self.assertRaises(TypeError):
            # no username
            u2 = User.signup(None, 'test2@test.com', 'test_pw2', None)
            # not a unique email
            u3 = User.signup('testuser3', 'test@test.com', 'test_pw3', None)
            # no image_url
            u4 = User.signup('testuser4', 'test4@test.com', 'test_pw4')


    def test_User_authenticate_valid(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        u = User.authenticate(self.u.username, 'HASHED_PASSWORD')

        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@test.com')
        self.assertIsNot(u.password, 'test_pw')
    

    def test_pw_match(self):
        """Check to see if Users.check_hashed_pw_match retuns True """

        self.assertEqual(User.check_hashed_pw_match(self.u.password, 'HASHED_PASSWORD'), True)