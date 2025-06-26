from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from catalog.models import Product


@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def catalog(request):
    category = request.GET.get('category')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(in_stock=True)

    if category:
        products = products.filter(category=category)

    if search_query:
        output = []
        for product in products:
            a = [i.lower() for i in product.name.split()]
            if search_query.lower() in a:
                output.append(product)
        products = output

    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    prices = Product.objects.filter(in_stock=True).values_list('price', flat=True)
    min_catalog_price = min(prices) if prices else None
    max_catalog_price = max(prices) if prices else None

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'min_price': min_catalog_price,
        'max_price': max_catalog_price,
        'min_price_filter': min_price,
        'max_price_filter': max_price,
        'categories': dict(Product.CATEGORY_CHOICES),
        'current_category': category,
        'search_query': search_query,
    }
    return render(request, 'catalog/catalog.html', context)
