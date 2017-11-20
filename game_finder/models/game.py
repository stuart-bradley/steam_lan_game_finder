from django.db import models
from decimal import Decimal
from .tag import Tag
from datetime import datetime

class Game(models.Model):
    # appid matches Steam appid.
    appid = models.IntegerField(primary_key=True, editable=False)
    title = models.CharField(max_length=200)
    is_multiplayer = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title
