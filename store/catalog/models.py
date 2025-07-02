from django.utils.text import slugify
from django.db import models
from cloudinary.models import CloudinaryField


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='URL')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категория'
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    image = CloudinaryField(
        'image',
        default='https://res.cloudinary.com/da74tpgsc/image/upload/v1750327746/images_hqlquy.jpg'
    )
    in_stock = models.BooleanField(default=True, verbose_name='В наличии')
    count = models.PositiveIntegerField(
        default=0,
        verbose_name="Текущий остаток"
    )
    initial_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Изначальное количество"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.pk and self.count > 0:
            self.initial_count = self.count
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']


