"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
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

db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)


    def test_user_repr(self):

        u1 = User.query.get(self.u1_id)
        self.assertEqual(repr(u1), f"<User #{u1.id}: {u1.username}, {u1.email}>")

    def test_user_model_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        self.assertEqual(u1.is_following(u2),True)
        self.assertEqual(u2.is_following(u1),False)


    def test_user_model_is_followed(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        self.assertEqual(u1.is_followed_by(u2),False)
        self.assertEqual(u2.is_followed_by(u1),True)

    def test_user_model_signup_fail(self):
        User.signup("u1", "u1@email.com", "password", None)

        self.assertRaises(
            IntegrityError,
            lambda: db.session.commit()
        )

    def test_user_model_authenticate(self):
        u1 = User.query.get(self.u1_id)

        self.assertEqual(User.authenticate(u1.username, "password"), u1)




#User.signup(username="u1", email="u1@email.com", password="password", image_url=None),







