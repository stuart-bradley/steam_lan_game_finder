from django.db import models
import uuid
from .tag import Tag

class Game(models.Model):
    appid = models.IntegerField(primary_key=True, editable=False)
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    tags = models.ManyToManyField(Tag)
