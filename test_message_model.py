# run these tests:  python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user = User.signup("testuser", "test@test.com", "HASHED_PASSWORD", None)
        user.id = 1234

        db.session.add(user)
        db.session.commit()

        # from solution code
        u = User.query.get(user.id)    

        self.u = u


    def tearDown(self):
        """Clean up any fowled transactions."""

        db.session.rollback()

    
    def test_Message_model(self):
        """Does basic model work?"""

        text = "The use of 'foo' in a programming is generally credited to the Tech Model Railroad Club (TMRC) of MIT from circa 1960 (-wikipedia)."
        
        msg = Message(text=text, user_id=self.u.id)
        
        db.session.add(msg)
        db.session.commit()

        m = Message.query.get(msg.id)

        self.assertIsInstance(msg, Message)
        self.assertIn("The use of 'foo'", msg.text)
        self.assertIsNotNone(m.timestamp)
        self.assertEqual(m.user_id, self.u.id)


    def test_Message_model_invalid_input(self):
        """Does basic model fail to create a new Message if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        text = "The use of 'foo' in a programming is generally credited to the Tech Model Railroad Club (TMRC) of MIT from circa 1960 (-wikipedia)."
        m = Message(user_id=self.u.id)
        
        db.session.add(m)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()
        
       
