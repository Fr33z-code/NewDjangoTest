from tkinter.font import names

from django.test import TestCase
from django.utils import timezone
from catalog.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()


class ProductCatalogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test', password='1qaz2wsx3edc')
        self.client.force_login(self.user)

        category = Category.objects.get(name='Меховые изделия')
        Product.objects.create(
            name="Шуба из овчины «Модель 100»",
            price=10000,
            category=category,
            description="Тёплая шуба",
            in_stock=True,
        )
        Product.objects.create(
            name="Жилет из лисы «Модель 99»",
            price=8000,
            category=category,
            description="Стильный жилет",
            in_stock=True,
        )


    def test_catalog_status_code(self):
        response = self.client.get('/catalog/')
        self.assertEqual(response.status_code, 200)


    def test_product_names_displayed(self):
            response = self.client.get('/catalog/')
            self.assertContains(response, "Шуба из овчины «Модель 100»")
            self.assertContains(response, "Жилет из лисы «Модель 99»")

# def test_filter_by_in_stock_true(self):
#     response = self.client.get('/catalog/?in_stock=true')
#     self.assertContains(response, "Шуба из норки")
#     self.assertNotContains(response, "Шуба из овчины")
#
# def test_filter_by_in_stock_false(self):
#     response = self.client.get('/catalog/?in_stock=false')
#     self.assertContains(response, "Шуба из овчины")
#     self.assertNotContains(response, "Шуба из норки")
#
# def test_filter_by_category(self):
#     response = self.client.get('/catalog/?category=category-2')
#     self.assertContains(response, "Шуба из норки")
#     self.assertContains(response, "Шуба из овчины")
#
#     response = self.client.get('/catalog/?category=category-1')
#     self.assertNotContains(response, "Шуба из норки")
#     self.assertNotContains(response, "Шуба из овчины")
#
# def test_search_by_name(self):
#     response = self.client.get('/catalog/?search=норки')
#     self.assertContains(response, "Шуба из норки")
#     self.assertNotContains(response, "Шуба из овчины")
#
# def test_sort_by_price_asc(self):
#     response = self.client.get('/catalog/?sort=price_asc')
#     products = list(response.context['products'])
#     self.assertLessEqual(products[0].price, products[1].price)
#
# def test_sort_by_price_desc(self):
#     response = self.client.get('/catalog/?sort=price_desc')
#     products = list(response.context['products'])
#     self.assertGreaterEqual(products[0].price, products[1].price)
#
# def test_no_results_message(self):
#     response = self.client.get('/catalog/?search=несуществующий')
#     self.assertContains(response, "Ничего не найдено")
#
# def test_product_in_stock_displayed(self):
#     response = self.client.get('/catalog/')
#     self.assertContains(response, "В наличии")
