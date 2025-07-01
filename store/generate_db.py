import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
django.setup()

from catalog.models import Product, Category


def create_categories():
    categories_data = {
        1: 'Меховые изделия',
        2: 'Шубы',
        3: 'Куртки',
        4: 'Аксессуары'
    }

    for id, name in categories_data.items():
        Category.objects.get_or_create(
            id=id,
            defaults={
                'name': name,
                'slug': f'category-{id}'
            }
        )
    print("✅ Категории созданы/проверены")


def create_products():
    create_categories()
    Product.objects.all().delete()
    PRODUCT_TYPES = {
        'Меховые изделия': [
            ('Жилет из лисы', 60000, 120000),
            ('Накидка из кролика', 55000, 110000),
            ('Жакет из овчины', 65000, 130000),
            ('Жилет из енота', 50000, 100000),
            ('Жилет из стриженого кролика', 45000, 90000)
        ],
        'Шубы': [
            ('Норковая шуба', 150000, 300000),
            ('Шуба из чернобурки', 180000, 350000),
            ('Шуба из овчины', 120000, 250000),
            ('Пальто из каракуля', 100000, 220000),
            ('Пальто меховое', 130000, 270000)
        ],
        'Куртки': [
            ('Кожаная куртка', 40000, 80000),
            ('Пуховик удлинённый', 35000, 70000),
            ('Парка с мехом', 30000, 60000),
            ('Куртка зимняя', 25000, 50000),
            ('Куртка демисезонная', 20000, 40000)
        ],
        'Аксессуары': [
            ('Шапка кашемировая', 5000, 10000),
            ('Шарф шерстяной', 3000, 6000),
            ('Перчатки кожаные', 4000, 8000),
            ('Шапка меховая', 6000, 12000),
            ('Шарф-труба', 2500, 5000)
        ]
    }

    items = []
    current_date = timezone.now()
    categories = list(Category.objects.all())
    if not categories:
        raise Exception("Нет категорий в базе данных!")

    for i in range(100):
        category = categories[i % len(categories)]
        category_name = category.name
        product_type = random.choice(PRODUCT_TYPES[category_name])
        name = f"{product_type[0]} «Модель {i + 1}»"
        price = random.randint(product_type[1], product_type[2])
        in_stock = i % 10 != 0
        items.append(Product(
            name=name,
            price=price,
            category=category,
            description=f"Описание для {name}. Категория: {category_name}.",
            in_stock=in_stock,
            created_at=current_date - timedelta(days=i),
            initial_count=150,
            count=150 if in_stock else 0
        ))

    batch_size = 20
    for i in range(0, len(items), batch_size):
        Product.objects.bulk_create(items[i:i + batch_size])

    print(f"✅ Успешно создано {len(items)} товаров")


if __name__ == '__main__':
    create_products()
