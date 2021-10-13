from django.contrib.auth.models import UserManager
from django.http import request, response
from django.test import Client, TestCase
from django.db.models import Max

from .models import User, Post

class NetworkTestCase(TestCase):

    def setUp(self):

        # Creating users
        user1 = User.objects.create(username="user1", email="user1@abc.com", password="user1")
        user2 = User.objects.create(username="user2", email="user2@abc.com", password="user2")
        user3 = User.objects.create(username="user3", email="user3@abc.com", password="user3")

        # Creating posts
        Post.objects.create(content="Post one", author=user1)
        Post.objects.create(content="Post two", author=user1)
        Post.objects.create(content="Post three", author=user1)
        Post.objects.create(content="Post four", author=user1)
        Post.objects.create(content="Post five", author=user1)
        Post.objects.create(content="Post six", author=user2)
        Post.objects.create(content="Post seven", author=user2)
        Post.objects.create(content="Post eight", author=user2)
        Post.objects.create(content="Post nine", author=user2)
        Post.objects.create(content="Post ten", author=user3)
        Post.objects.create(content="Post eleven", author=user3)
        Post.objects.create(content="Post twelve", author=user3)

        # Adding followers
        user1.followers.add(user2)
        user1.followers.add(user3)
        user2.followers.add(user1)
        user3.followers.add(user3)


    def test_all_posts_count(self):
        self.assertEqual(Post.objects.count(), 12)


    def test_user_posts_count(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        user3 = User.objects.get(username="user3")
    
        self.assertEqual(user1.posts.count(), 5)
        self.assertEqual(user2.posts.count(), 4)
        self.assertEqual(user3.posts.count(), 3)


    def test_user_follow_count(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")
        user3 = User.objects.get(username="user3")

        self.assertEqual(user1.followers.count(), 2)
        self.assertEqual(user2.followers.count(), 1)
        self.assertEqual(user3.followers.count(), 1)

        self.assertEqual(user1.following.count(), 1)
        self.assertEqual(user2.following.count(), 1)
        self.assertEqual(user3.following.count(), 2)


    def test_user_valid_follow(self):
        user1 = User.objects.get(username="user1")
        user2 = User.objects.get(username="user2")

        self.assertTrue(user1.is_valid_follow())
        self.assertTrue(user2.is_valid_follow())


    def test_user_invalid_follow(self):
        user3 = User.objects.get(username="user3")

        self.assertFalse(user3.is_valid_follow())

    
    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts_page"]), 10)

        response = c.get("?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts_page"]), 10)

        response = c.get("?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts_page"]), 2)
    

    def test_valid_profile_page(self):
        user1 = User.objects.get(username="user1")

        c = Client()
        response = c.get(f"/profile/{user1.username}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"], user1)
        self.assertEqual(response.context["followers_count"], 2)
        self.assertEqual(response.context["following_count"], 1)
        self.assertEqual(len(response.context["posts_page"]), 5)
        self.assertEqual(response.context["following"], None)

        response = c.get(f"/profile/{user1.username}?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts_page"]), 5)

        user2 = User.objects.get(username="user2")
        user3 = User.objects.get(username="user3")
        
        c.force_login(user2)

        response = c.get(f"/profile/{user1.username}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["following"])

        response = c.get(f"/profile/{user3.username}")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["following"])

        response = c.get(f"/profile/{user2.username}")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["following"])


    def test_valid_following_page(self):
        user1 = User.objects.get(username="user1")

        c = Client()
        c.force_login(user1)
        response = c.get(f"/following")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["posts_page"]), 4)