# run these tests:  python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
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
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        # Message.query.delete()
        # Follows.query.delete()

        self.client = app.test_client()

        user = User.signup("testuser", "test@test.com", "HASHED_PASSWORD", None)
        user.id = 1111

        db.session.add(user)
        db.session.commit()

        # from solution code
        u = User.query.get(user.id)    

        self.u = u


    def tearDown(self):
        """Clean up any fowled transactions."""

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
# User.signup class-method tests

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

        with self.assertRaises(exc.IntegrityError):
            # not unique username
            u1 = User.signup(self.u.username, 'test1@test.com', 'test_pw1', None)
            db.session.add(u1)

            db.session.commit()

        with self.assertRaises(exc.InvalidRequestError):
            # no username
            u2 = User.signup(None, 'test2@test.com', 'test_pw2', None)
            db.session.add(u2)

            db.session.commit()

        with self.assertRaises(exc.InvalidRequestError):
            # not a unique email
            u3 = User.signup('testuser3', self.u.email, 'test_pw3', None)
            db.session.add(u3)

            db.session.commit()

        with self.assertRaises(exc.InvalidRequestError):
            # no email
            u4 = User.signup('testuser4', None, 'test_pw4', None)
            db.session.add(u4)

            db.session.commit()
        
            
    def test_User_signup_missing_email(self):
        """"Does User.signup fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        with self.assertRaises(ValueError):
            # missing password
            User.signup('testuser5', 'test5@test.com', None, None)
            # wrong img_url type
            User.signup('testuser5', 'test5@test.com', 'test_pw6', 1)


############################################################
# User.authenticate class-method tests

    def test_User_authenticate_valid(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        u = User.authenticate(self.u.username, 'HASHED_PASSWORD')

        self.assertEqual(u.username, 'testuser')
        self.assertEqual(u.email, 'test@test.com')
        self.assertIsNot(u.password, 'test_pw')
        # Bcrypt strings should start with $2b$
        self.assertTrue(u.password.startswith("$2b$"))
    
    
    def test_User_authenticate_invalid_password(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        u = User.authenticate(self.u.username, 'Not_A_Great_PW')

        self.assertFalse(u)
    
    
    def test_User_authenticate_invalid_username(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        u = User.authenticate('not_real_username', 'HASHED_PASSWORD')

        self.assertFalse(u)
    

############################################################
# User.check_hashed_pw_match class-method tests

    def test_pw_match_valid(self):
        """Check to see if User.check_hashed_pw_match retuns True if valid pw. """

        self.assertTrue(User.check_hashed_pw_match(self.u.password, 'HASHED_PASSWORD'))


    def test_pw_match_invalid_password(self):
        """Check to see if User.check_hashed_pw_match retuns True if invalid password. """

        self.assertFalse(User.check_hashed_pw_match(self.u.password, 'Not_A_Great_PW'))
    
    
    def test_pw_match_invalid_username(self):
        """Check to see if User.check_hashed_pw_match retuns True if invalid username. """

        with self.assertRaises(ValueError):
            User.check_hashed_pw_match('not_real_username', 'HASHED_PASSWORD')


