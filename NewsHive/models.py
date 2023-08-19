from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class FavoriteNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField()
    article_url = models.URLField()

    def __str__(self):
        return self.title