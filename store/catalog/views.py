from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.core.paginator import Paginator
from django.shortcuts import render
from catalog.models import Product, Category
from catalog.service import CatalogService


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'


class CatalogView(LoginRequiredMixin, TemplateView):
    template_name = 'catalog/catalog.html'

    def get(self, request, *args, **kwargs):
        params = request.GET

        filters = CatalogService.get_filters_from_params(params)
        products = CatalogService.filter_products(filters)

        search_query = params.get('search', '').strip()
        products = CatalogService.search_products(products, search_query)

        min_price, max_price = CatalogService.get_price_range()
        paginator = Paginator(products, 12)
        page_number = params.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'min_price': min_price,
            'max_price': max_price,
            'min_price_filter': params.get('min_price'),
            'max_price_filter': params.get('max_price'),
            'categories': CatalogService.get_categories_dict(),
            'current_category': params.get('category'),
            'search_query': search_query,
        }

        return render(request, self.template_name, context)
