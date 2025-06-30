from catalog.models import Product, Category
from core.BaseService import BaseService

class CatalogService(BaseService):
    @staticmethod
    def get_filters_from_params(params):
        filters = {'in_stock': True}
        if params.get('category'):
            filters['category'] = params['category']

        try:
            if params.get('min_price'):
                filters['price__gte'] = float(params['min_price'])
            if params.get('max_price'):
                filters['price__lte'] = float(params['max_price'])
        except ValueError:
            pass

        return filters

    @staticmethod
    def filter_products(filters):
        return Product.objects.filter(**filters)

    @staticmethod
    def search_products(products, search_query):
        if not search_query:
            return products

        output = []
        search_lower = search_query.lower()
        for product in products:
            words = [word.lower() for word in product.name.split()]
            if search_lower in words:
                output.append(product)
        return output

    @staticmethod
    def get_price_range():
        prices = Product.objects.filter(in_stock=True).values_list('price', flat=True)
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None
        return min_price, max_price

    @staticmethod
    def get_categories_dict():
        return {c.id: c.name for c in Category.objects.all()}
