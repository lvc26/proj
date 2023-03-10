import sys
from PIL import Image
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.utils import timezone
from io import BytesIO

'''C помощью этой команды, мы говорим django, что хотим использовать именно того пользователя, который указан в settings_AUTH_USER_MODEL'''
User = get_user_model()


def get_models_for_count(*model_names):
    '''
    Функция принимает переменное количество аргументов и возвращает список объектов `Count`, по одному для каждого аргумента
    :возвращает: список объектов Count.

    '''
    return [models.Count(model_name) for model_name in model_names]


def get_product_url(obj, viewname):
    '''
    
   Функция принимает объект и имя представления и возвращает URL страницы сведений об объекте
 
   :параметр obj: Объект, для которого вы хотите получить URL-адрес 
   :param viewname: имя представления, которое вы хотите изменить
   :возвращает: URL
   
    '''
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        '''
        Функция возвращает список объектов заданных моделей, отсортированных по названию модели
        :возвращает: список объектов разных типов.
        '''
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:5]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products, key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to), reverse=True
                    )
        return products



class LatestProducts:

    objects = LatestProductsManager()



# Класс, который используется для управления категориями.
class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Платья': 'dress__count',
        'Юбки': 'skirt__count'
    }

    def get_queryset(self):
        '''
        Функция возвращает набор запросов суперкласса.
        :return: Возвращается набор запросов.

        '''
        return super().get_queryset()

      '''

    Функция получает категории для левой боковой панели и аннотирует их количеством платьев и юбок в каждой категории
    :возвращает: список словарей. 
    
      '''
    def get_categories_for_left_sidebar(self):
        models = get_models_for_count('dress', 'skirt')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name]))
            for c in qs
        ]
        return data


''' 
Класс Category является подклассом класса Model. 
Класс Category имеет атрибут name, атрибут slug и атрибут objects.
: name - название категории (строковое поле)
: slug - алиас продукта или по-другому его URL.
: objects - менеджер категорий.
Класс Category имеет метод __str__, который возвращает атрибут name.
Класс Category имеет метод get_absolute_url, который возвращает URL.
URL-адрес генерируется обратной функцией, которой передается представление category_detail и slug

'''
class Category(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


''' 
Класс продукта - это абстрактный класс, который определяет поля, общие для всех продуктов
: category - Категория продукта.  ForeignKey - это отношение "многие к одному": продукт относится к одной категории, а категория содержит несколько продуктов
: title - название продукта
: slug - URL продукта
: image - изображение
: description - описание товара
: price - стоимость

'''
class Product(models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображение')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def get_model_name(self):
        '''
        Возвращает имя класса

        '''
        return self.__class__.__name__.lower()

        """
        
        Он берет изображение, преобразует его в RGB, изменяет его размер, сохраняет его в filestream, а затем сохраняет filestream в поле image
        
        """
    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((400, 400), Image.ANTIALIAS)
        filestream = BytesIO()
        resized_new_img.save(filestream, 'JPEG', quality=90)
        filestream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        print(self.image. name, name)
        self.image = InMemoryUploadedFile(
            filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(filestream), None
        )
        super().save(*args, **kwargs)


'''Платье - наш продукт, который имеет стиль, структуру, крой, силуэт, цвет и длину.'''
class Dress(Product):

    style = models.CharField(max_length=255, verbose_name='Фасон')
    structure = models.CharField(max_length=255, verbose_name='Состав')
    cut= models.CharField(max_length=255, verbose_name='Крой')
    silhouette = models.CharField(max_length=255, verbose_name='Силуэт')
    color = models.CharField(max_length=255, verbose_name='Цвет')
    length = models.CharField(max_length=255, verbose_name='Длина')

    def __str__(self):
        '''
        Функция __str__ - это специальная функция, которая вызывается, когда вы вызываете str() для объекта. 
        Функция __str__ должна возвращать строковое представление объекта
        :возвращает: название категории и заголовок сообщения.
        '''
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        '''
        Функция возвращает URL страницы сведений о продукте для экземпляра продукта
        :возвращает: Возвращается представление product_detail.
        
        '''
        return get_product_url(self, 'product_detail')


''' Юбка - наш продукт, который имеет стиль, структуру, крой, силуэт, посадку и длину.'''
class Skirt(Product):

    style = models.CharField(max_length=255, verbose_name='Фасон')
    structure = models.CharField(max_length=255, verbose_name='Состав')
    cut = models.CharField(max_length=255, verbose_name='Крой')
    silhouette = models.CharField(max_length=255, verbose_name='Силуэт')
    landing = models.CharField(max_length=255, verbose_name='Посадка')
    length = models.CharField(max_length=255, verbose_name='Длина')


    def __str__(self):
        '''
        Функция __str__ - это специальная функция, которая вызывается, когда вы вызываете str() для объекта. 
        Функция __str__ должна возвращать строковое представление объекта
        :возвращает: название категории и заголовок сообщения.

        '''
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        '''
        Функция возвращает URL страницы сведений о продукте для экземпляра продукта
       :возвращает: Представление product_detail.
        '''
        return get_product_url(self, 'product_detail')


'''Товар в корзине - это товар, который находится в корзине.'''
class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        '''
        Метод __str__ вызывается, когда вы вызываете str() для объекта.
        :возвращает: Название продукта

        '''
        return "Продукт: {} (для корзины)".format(self.content_object.title)

    def save(self, *args, **kwargs):
        '''
        Функция принимает количество товара и умножает его на цену товара

        '''
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


'''Корзина позволяет пользователям выбирать нужные продукты и временно хранить их'''
class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        """
        Функция возвращает индентификатор объекта.
        
        """
        return str(self.id)

    
''' Клиент, который использует магазин. 
    :user - пользователь 
    :phone - телефон
    :address - адресс
    :orders - заказы покупателя. ManyToManyField - отношение многие ко многим. То есть у покупателя может быть много заказов, а у заказа может быть много покупателей
'''

class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_order')

    def __str__(self):
      """
      Метод __str__ должен возвращать строковое представление объекта
      :возвращает: Покупатель: Иван Иванов
      
      """
        return "Покупатель: {} {}".format(self.user.first_name, self.user.last_name)


''' Класс Заказ:
    :customer - покупатель
    :first_name - имя покупателя
    :last_name - фамилия покупателя
    :phone - телефон
    :cart - корзина
    :address - адресс
    :status - статус закааза 
    :comment - комментарий к заказу
    :created_at - дата создания
    :order_date - дата получения
'''
class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', related_name='related_orders', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(
        max_length=100,
        verbose_name='Статус заказ',
        choices=STATUS_CHOICES,
        default=STATUS_NEW
    )
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return str(self.id)
