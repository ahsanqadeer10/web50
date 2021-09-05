from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE, PROTECT
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
    highest_bid = models.IntegerField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=CASCADE, related_name="listings")
    creator = models.ForeignKey(
        User, on_delete=CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        User, on_delete=PROTECT, related_name="wins", null=True, blank=True, default=None)

    def __str__(self):
        return self.title


class Bid(models.Model):
    value = models.IntegerField()
    bidder = models.ForeignKey(User, on_delete=CASCADE, related_name="bids")
    listing = models.ForeignKey(
        Listing, on_delete=CASCADE, related_name="bids")

    def __str__(self):
        return f'{self.value} on {self.listing} by {self.bidder}'
