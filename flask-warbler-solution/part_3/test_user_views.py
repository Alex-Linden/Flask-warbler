"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from bs4 import BeautifulSoup

from models import Follows, Like, Message, User, db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)
        u4 = User.signup("u4", "u4@email.com", "password", None)
        db.session.add_all([u1, u2, u3, u4])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id
        self.u4_id = u4.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()


class UserListShowTestCase(UserBaseViewTestCase):
    def test_users_index(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users")

            self.assertIn("@u1", str(resp.data))
            self.assertIn("@u2", str(resp.data))
            self.assertIn("u3", str(resp.data))
            self.assertIn("@u4", str(resp.data))

    def test_users_search(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get("/users?q=1")

            self.assertIn("@u1", str(resp.data))
            self.assertNotIn("@u2", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u1", str(resp.data))


class UserLikeTestCase(UserBaseViewTestCase):
    def setUp(self):
        super().setUp()
        m1 = Message(text="text", user_id=self.u2_id)
        db.session.add_all([m1])
        db.session.flush()
        k1 = Like(user_id=self.u1_id, message_id=m1.id)
        db.session.add_all([k1])
        db.session.commit()

        self.m1_id = m1.id

    def test_user_show_with_likes(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})

            self.assertEqual(len(found), 4)
            self.assertIn("1", found[3].text)  # Test for a count of 1 like

    def test_add_like(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u3_id

            resp = c.post(f"/messages/{self.m1_id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Like.query.filter(Like.message_id == self.m1_id, ).all()
            self.assertEqual(len(likes), 2)

    def test_remove_like(self):
        k = Like.query.filter(
            Like.user_id == self.u1_id and Like.message_id == self.m1_id
        ).one()

        self.assertIsNotNone(k)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/messages/{self.m1_id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Like.query.filter(Like.message_id == self.m1_id).all()
            self.assertEqual(len(likes), 0)


class UserFollowingViewTestCase(UserBaseViewTestCase):
    def setUp(self):
        super().setUp()

        # u1 followed by u2, u3
        # u2 followed by u1
        f1 = Follows(
            user_being_followed_id=self.u1_id,
            user_following_id=self.u2_id)
        f2 = Follows(
            user_being_followed_id=self.u1_id,
            user_following_id=self.u3_id)
        f3 = Follows(
            user_being_followed_id=self.u2_id,
            user_following_id=self.u1_id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u1", str(resp.data))

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})

            self.assertEqual(len(found), 4)
            self.assertIn("1", found[1].text)  # Test for a count of 1 following
            self.assertIn("2", found[2].text)  # Test for a count of 2 follower

    def test_show_following(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u1_id}/following")
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@u1", str(resp.data))
            self.assertIn("@u2", str(resp.data))
            self.assertNotIn("u3", str(resp.data))

    def test_show_followers(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get(f"/users/{self.u2_id}/followers")
            self.assertIn("@u1", str(resp.data))
            self.assertNotIn("@u3", str(resp.data))
