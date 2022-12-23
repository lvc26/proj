from decimal import Decimal
from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Category, Dress, CartProduct, Cart, Customer
from .views import recalc_cart, AddToCartView, BaseView



User = get_user_model()


class ShopTestCases(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser', password='password')
        self.category = Category.objects.create(name='Платья', slug='dress')
        image = SimpleUploadedFile ("dress_image.jpg", content=b'', content_type="image/jpg")
        self.dress = Dress.objects.create(
            category = self.category,
            title = "Test Dress",
            slug = "test-slug",
            image = image,
            price = Decimal('50000.00'),
            style = "little black",
            structure = "cotton",
            cut = "baby doll",
            silhouette = "trapezoid",
            color = "black",
            length = "maxi",
        )
        self.customer = Customer.objects.create (user=self.user, phone="666666", address="Adres")
        self.cart = Cart.objects.create (owner=self.customer)
        self.cart_product = CartProduct.objects.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.dress,
        )


    def test_add_to_cart(self):
        """
        Функция добавляет товар в корзину, пересчитывает корзину, а затем утверждает, что товар находится в
        корзине, что в корзине есть один товар и что окончательная цена составляет 50000,00.
        """
        self.cart.products.add(self.cart_product)
        recalc_cart(self.cart)
        self.assertIn(self.cart_product, self.cart.products.all())
        self.assertEqual(self.cart.products.count(), 1)
        self.assertEqual(self.cart.final_price, Decimal('50000.00'))


    def test_response_from_add_to_cart_view(self):
        """
        Мы тестируем, что ответ из представления "AddToCart" является перенаправлением на страницу корзины.
        """
        factory = RequestFactory()
        request = factory.get('')
        request.user = self.user
        response = AddToCartView.as_view()(request, ct_model="dress", slug="test-slug")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart/')


    def test_mock_homepage(self):
        """
        Я собираюсь имитировать метод get класса BaseView, и я собираюсь вернуть макет объекта
        с кодом состояния 444. Затем я собираюсь вызвать класс BaseView как view, и я буду
        утверждать, что код состояния ответа равен 444.
        """
        mock_data = mock.Mock(status_code=444)
        with mock.patch('mainapp.views.BaseView.get', return_value=mock_data) as mock_data_:
            factory = RequestFactory()
            request = factory.get('')
            request.user=self.user
            response = BaseView.as_view()(request)
            self.assertEqual(response.status_code, 444)

