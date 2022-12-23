from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View

from .models import Category, Cart, Customer, Dress, Skirt


class CategoryDetailMixin(SingleObjectMixin):

    # Словарь, который сопоставляет категорию slug с моделью продукта.
    CATEGORY_SLUG2PRODUCT_MODEL = {
        'dress': Dress,
        'skirt': Skirt
    }

    def get_context_data(self, **kwargs):
        """
        Если объект является категорией, то получите модель из словаря, получите контекстные данные из
        суперкласс, получите категории для левой боковой панели и получите продукты для категории
        :return: Контекст возвращается.
        """
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['categories'] = Category.objects.get_categories_for_left_sidebar()
            context['category_products'] = model.objects.all()
            return context
        # Получение контекста из суперкласса, а затем добавление категорий в контекст.
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categories_for_left_sidebar()
        return context


class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        """
        Если пользователь вошел в систему, мы проверяем, есть ли у него корзина, если нет, мы ее создаем.
        Если пользователь не вошёл в систему, мы проверяем, есть ли у него корзина, если нет, мы создаем ее.
        :param request: Объект запроса.
        :return: Возвращается метод super().dispatch().
        """
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(
                    user=request.user
                )
            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)
        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)
        self.cart = cart
        return super().dispatch(request, *args, **kwargs)

