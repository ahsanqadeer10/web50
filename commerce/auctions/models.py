from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'Listing', blank=True, related_name="watchers")

    pass


class Category(models.Model):
    name = models.CharField(max_length=64)
    image = models.URLField()

    def __str__(self):
        return self.name


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=250)
    starting_bid = models.IntegerField()
    image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=CASCADE, related_name="listings")
    creator = models.ForeignKey(
        User, on_delete=CASCADE, related_name="listings")

    def __str__(self):
        return self.title
