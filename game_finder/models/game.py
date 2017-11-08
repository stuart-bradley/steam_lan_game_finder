from django.db import models
import uuid
from .tag import Tag

class Game(models.Model):
    appid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    is_multiplayer = models.BooleanField()
    price = models.DecimalField(decimal_places=2)
    tags = models.ManyToManyField(Tag)
