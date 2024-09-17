"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        u1 = User.signup("testing", "testing@test.com", "password", None)
        m1 = Message(text="text")
        u1.messages.append(m1)
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        u = User.query.get(self.u1_id)

        # User should have 1 message
        self.assertEqual(len(u.messages), 1)
        self.assertEqual(u.messages[0].text, "text")

    def test_message_likes(self):
        u = User.query.get(self.u1_id)
        m1 = Message.query.get(self.m1_id)
        m2 = Message(text="text-2", user_id=self.u1_id)

        db.session.add_all([m2])
        u.liked_messages.append(m1)
        db.session.commit()

        k = Like.query.filter(Like.user_id == u.id).all()
        self.assertEqual(len(k), 1)
        self.assertEqual(k[0].message_id, m1.id)
