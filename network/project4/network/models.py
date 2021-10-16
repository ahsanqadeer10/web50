from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.reverse_related import OneToOneRel


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    followers = models.ManyToManyField('User', related_name="following")
    
    def is_valid_follow(self):
        return self not in self.followers.all()

class Post(models.Model):
    content = models.TextField(null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, related_name="posts_liked")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
