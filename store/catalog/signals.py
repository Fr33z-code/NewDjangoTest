from django.db.models.signals import pre_save
from django.dispatch import receiver
from catalog.models import Product


@receiver(pre_save, sender=Product)
def update_in_stock(sender, instance, **kwargs):
    instance.in_stock = instance.count > 0
