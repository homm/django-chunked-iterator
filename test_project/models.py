from django.db import models


class Item(models.Model):
    created = models.DateTimeField(unique=True)
