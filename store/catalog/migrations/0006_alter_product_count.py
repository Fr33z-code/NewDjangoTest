# Generated by Django 5.2.3 on 2025-06-25 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0005_alter_product_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='count',
            field=models.IntegerField(default=150),
        ),
    ]
