from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from catalog.models import Product, Category
#

@login_required
def home(request):
    return render(request, 'home.html')


@login_required
def catalog(request):
    params = request.GET
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

    products = Product.objects.filter(**filters)

    search_query = params.get('search', '').strip()
    if search_query:
        output = []
        for product in products:
            a = [i.lower() for i in product.name.split()]
            if search_query.lower() in a:
                output.append(product)
        products = output
    # if search_query:
    #     products = products.filter(name__icontains=search_query)

    prices = Product.objects.filter(in_stock=True).values_list('price', flat=True)
    min_catalog_price = min(prices) if prices else None
    max_catalog_price = max(prices) if prices else None

    paginator = Paginator(products, 12)
    page_number = params.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'min_price': min_catalog_price,
        'max_price': max_catalog_price,
        'min_price_filter': params.get('min_price'),
        'max_price_filter': params.get('max_price'),
        'categories': {c.id: c.name for c in Category.objects.all()},
        'current_category': params.get('category'),
        'search_query': search_query,
    }

    return render(request, 'catalog/catalog.html', context)
