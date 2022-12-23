from django.db import transaction
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View

from .models import Dress, Skirt, Category, LatestProducts, Customer, Cart, CartProduct
from .mixins import CategoryDetailMixin, CartMixin
from .forms import OrderForm
from .utils import recalc_cart


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        """
        Функция получает категории для левой боковой панели и товары для главной страницы, а затем отображает
        в base.html шаблон с контекстом.
        :param request: Объект запроса.
        :return: Функция рендеринга возвращается.
        """
        categories = Category.objects.get_categories_for_left_sidebar()
        products = LatestProducts.objects.get_products_for_main_page(
            'dress', 'skirt', with_respect_to='dress'
        )
        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'base.html', context)


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    # Словарь, который сопоставляет имя модели типа контента классу модели.
    CT_MODEL_MODEL_CLASS = {
        'dress': Dress,
        'skirt': Skirt
    }

    def dispatch(self, request, *args, **kwargs):
        """
        Функция отправки вызывается перед методами get или post. Она используется для выполнения любых
        действий, которые необходимо выполнить до вызова методов get или post.
        :param request: Объект запроса.
        :return: Возвращается метод super().dispatch().
        """
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    # Определение context_object_name, template_name и slug_url_kwargs для класса представления сведений
    # о продукте.
    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """
        Она берет контекстные данные из родительского класса (в данном случае общего класса DetailView) и
        добавляет к нему название модели и корзину.
        :return: Контекст возвращается.
        """
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        return context


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    # Определение модели, набора запросов, context_object_name, template_name и slug_url_kwargs для
    # класса CategoryDetailView.
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        """
        Функция берет контекстные данные из родительского класса (в данном случае общего класса DetailView) и
        добавляет к нему корзину.
        :return: Контекст возвращается.
        """
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        """
        Мы получаем тип контента продукта, получаем сам продукт, а затем получаем или
        создаём объект продукта корзины.
        :param request: Объект запроса.
        """
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        # messages.add_message(request, messages.INFO, "Товар успешно добавлен").
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        """
        Она получает товар из корзины, учитывая тип содержимого и идентификатор продукта
        : param request: Объект запроса.
        """
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        # Удаление товара из корзины, а затем повторный расчет корзины.
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        """
        Она принимает запрос, получает продукт, получает продукт в корзине, получает количество из запроса,
        устанавливает количество продуктов корзины, сохраняет продукт в корзине, пересчитывает корзину и
        перенаправляет нас в корзину.
        :param request: Объект запроса.
        :return: HttpResponseRedirect('/cart/').
        """
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        """
        Функция получает категории для левой боковой панели, а затем отображает cart.html шаблон с
        корзиной и категориями в контексте.
        :param request: Объект запроса.
        :return: Корзина возвращается.
        """
        categories = Category.objects.get_categories_for_left_sidebar()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        """
        Она получает категории для левой боковой панели, создает форму заказа и отображает оформление заказа
        страница.
        :param request: Объект запроса.
        :return: Страница оформления заказа возвращается.
        """
        categories = Category.objects.get_categories_for_left_sidebar()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """
        Функция принимает запрос, и если форма действительна, она сохраняет форму, сохраняет корзину и
        перенаправляет на домашнюю страницу.
        :param request: Текущий объект HTTP-запроса.
        :return: Представление возвращает объект HttpResponseRedirect.
        """
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')


