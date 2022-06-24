"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py
#    FLASK_ENV=production python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError, DataError
from models import db, User, Message, Follows

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

LOREM_IPSUM = '''Lorem ipsum dolor sit amet consectetur adipisicing elit.
Ipsam minus laboriosam vel, architecto laudantium sunt fugit repudiandae voluptate!
Cumque voluptatem consequatur qui repellat obcaecati vel aperiam nisi velit assumenda odit?'''

db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()

        m1 = Message(text='Test Text',user_id=u1.id)
        db.session.add(m1)
        db.session.commit()



        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


    def test_valid_message_model(self):
        u1 = User.query.get(self.u1_id)
        m1 = Message.query.get(self.m1_id)

        self.assertEqual(m1.text,'Test Text')
        self.assertEqual(m1.user_id,u1.id)

        # User should have no messages & no followers

    def test_message_length(self):
        u1 = User.query.get(self.u1_id)
        m2 = Message(text=LOREM_IPSUM,user_id=u1.id)
        db.session.add(m2)

        self.assertRaises(DataError,lambda: db.session.commit())

    def test_user_mesage_relationship(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)
        m1 = Message.query.get(self.m1_id)

        self.assertEqual(m1.user,u1)
        self.assertNotEqual(m1.user,u2)














