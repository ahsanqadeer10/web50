from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField

class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    followers = models.ManyToManyField('User', related_name="following")
    profile_picture = models.ImageField(upload_to="images/", null=True)
    bio = models.CharField(max_length=512, null=True, blank=True)
    
    def is_valid_follow(self):
        return self not in self.followers.all()

    def profile_picture_url(self):
        default_url = "/media/images/default-profile-pic.png"
        if self.profile_picture:
            return self.profile_picture.url
        else:
            return default_url

class Post(models.Model):
    content = models.TextField(null=False, blank=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User, related_name="posts_liked")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
