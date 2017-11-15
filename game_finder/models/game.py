from django.db import models
from decimal import Decimal
from .tag import Tag

class Game(models.Model):
    appid = models.IntegerField(primary_key=True, editable=False)
    title = models.CharField(max_length=200)
    is_multiplayer = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    tags = models.ManyToManyField(Tag)
