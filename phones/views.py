from django.shortcuts import render, get_object_or_404
from .models import Phone


def show_catalog(request):
    sort = request.GET.get('sort')
    phones = Phone.objects.all()

    if sort == 'name':
        phones = phones.order_by('name')
    elif sort == 'min_price':
        phones = phones.order_by('price')
    elif sort == 'max_price':
        phones = phones.order_by('-price')
    else:
        # дефолтная сортировка
        phones = phones.order_by('name')

    context = {
        'phones': phones,
    }
    return render(request, 'catalog.html', context)


def show_product(request, slug):
    phone = get_object_or_404(Phone, slug=slug)
    context = {'phone': phone}
    return render(request, 'product.html', context)

