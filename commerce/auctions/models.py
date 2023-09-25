from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to = "media/")
    description = models.CharField(max_length=500, default='-')
    category = models.CharField(max_length=64, default='-')
    created = models.DateTimeField(default=timezone.now)
    in_watchlist = models.CharField(max_length=64, default='no')


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ManyToManyField(AuctionListing)
    added = models.DateTimeField(default=timezone.now)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ManyToManyField(AuctionListing)
    comment = models.CharField(max_length=500, default='-')
    created = models.DateTimeField(default=timezone.now)
