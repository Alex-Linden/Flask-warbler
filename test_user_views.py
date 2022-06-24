from unittest import TestCase

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows
#from http import client

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, do_login

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class UserViewsAppTestCase(TestCase):
    """Test flask app of Boggle."""

    def setUp(self):
        """Stuff to do before every test."""
        User.query.delete()

        self.client = app.test_client()
        app.config['TESTING'] = True

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id


    def tearDown(self):
        db.session.rollback()

    def test_logged_out_follower_views(self):
        """When user logged out can't view user's followers page"""
        u1 = User.query.get(self.u1_id)
        with self.client as client:
            response = client.get(f"/users/{u1.id}/followers")

            self.assertEqual(response.status_code, 302)

    def test_logged_out_following_views(self):
        """When user logged out can't view user's followers page"""
        u1 = User.query.get(self.u1_id)
        with self.client as client:
            response = client.get(f"/users/{u1.id}/following")

            self.assertEqual(response.status_code, 302)

    def test_logged_in_follower_views(self):
        u1 = User.query.get(self.u1_id)
        with self.client as client:
            with client.session_transaction() as session:
                session["curr_user"] = u1.id

            response = client.get(f"/users/{u1.id}/followers")

            self.assertEqual(response.status_code, 200)

    def test_logged_in_add_message_page(self):
        u1 = User.query.get(self.u1_id)
        with self.client as client:
            with client.session_transaction() as session:
                session["curr_user"] = u1.id

            response = client.get('/messages/new')
            self.assertEqual(response.status_code, 200)




