from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=200)
    is_multiplayer = models.BooleanField(default=False)