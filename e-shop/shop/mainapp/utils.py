from django.db import models


def recalc_cart(cart):
    """
    Фукция пересчитывает конечную цену и общее количество товаров в корзине.
    :param cart: Объект в корзине.
    """
    cart_data = cart.products.aggregate(models.Sum('final_price'), models.Count('id'))
    if cart_data.get('final_price__sum'):
        cart.final_price = cart_data['final_price__sum']
    else:
        cart.final_price = 0
    cart.total_products = cart_data['id__count']
    cart.save()
