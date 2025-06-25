from django.db import models


class Category(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
