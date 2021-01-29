# import pdb
# pdb.set_trace()

# run these tests:  FLASK_ENV=production python -m unittest test_message_views.py


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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()


############################################################
# Add and Delete Messages while logged-in tests

    def test_add_message(self):
        """When you’re logged in, can you add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")


    def test_delete_message(self):
        """When you’re logged in, can you delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # create a new message which will be deleted, and get message id from db
            c.post("/messages/new", data={"text": "Pls delete me!"})
            
            msg = db.session.query(Message).first()
            
            resp = c.post(f'/messages/{msg.id}/delete')

            self.assertEqual(resp.status_code, 302)
            self.assertIn(f'/users/{msg.user_id}', resp.location)

            # msg is no longer in db
            self.assertIsNone(Message.query.get(msg.id))
            

############################################################
# Message Add/Delete protection if not logged in tests

    def test_authorization_msg_add(self):
        """When you’re logged out, are you prohibited from adding messages?"""

        with self.client as c:
            # unauthorized post results in a redirect
            resp1 = c.post('/messages/new', data={"text": "Unathorized Add Attempt"})
            self.assertEqual(resp1.status_code, 302)

            # follow re-direct
            resp2 = c.post('/messages/new', data={"text": "I'm not allowed to add a new message."}, follow_redirects=True)
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)
            self.assertIn("Access unauthorized.", html)

            # db is empty
            empty_db = Message.query.all()
            self.assertEqual(len(empty_db), 0)


    def test_authorization_msg_delete(self):
        """When you’re logged out, are you prohibited from deleting messages?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            # add a new message as a logged-in user
            resp1 = c.post('/messages/new', data={"text": "This message won't be deleted."})
            
            msg = db.session.query(Message).first()

            # logout
            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY]

            # now, try to delete the above message.
            resp2 = c.post(f'/messages/{msg.id}/delete', follow_redirects=True)
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp2.status_code, 200)

            # db still has 1 message
            one_msg = Message.query.all()
            self.assertEqual(len(one_msg), 1)
            