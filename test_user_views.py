# run these tests:  FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()


    def test_follower_page(self):
        """When you’re logged in, can you see the follower / following pages for another user?"""

        with self.client as c:
            # get testuser2 data
            testuser2 = db.session.query(User).filter_by(id=self.testuser2.id).first()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{testuser2.id}/followers")
            html = resp.get_data(as_text=True)

            # run tests as testuser1 who is viewing a page associated with testuser2
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{testuser2.username}', html)
   
   
    def test_following_page(self):
        """When you’re logged in, can you see the follower / following pages for another user?"""

        with self.client as c:
            # get testuser2 data
            testuser2 = db.session.query(User).filter_by(id=self.testuser2.id).first()

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id

            resp = c.get(f"/users/{testuser2.id}/following")
            html = resp.get_data(as_text=True)

            # run tests as testuser1 who is viewing a page associated with testuser2
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{testuser2.username}', html)


