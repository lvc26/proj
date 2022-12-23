from django import forms

from .models import Order


class OrderForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        """
        Функция __init__ вызывается при создании экземпляра класса.
        Функция super() используется для предоставления доступа к методам и свойствам родительского или родственного
        класс.
        *args и **kwargs используются для передачи функции переменного числа аргументов.
        Атрибут label используется для указания текста для метки.
        """
        super().__init__(*args, **kwargs)
        self.fields['order_date'].label = 'Дата получения заказа'

    # Установка типа поля ввода на дату.
    order_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
    # Определение полей, которые будут отображаться в форме.
        model = Order
        fields = (
            'first_name', 'last_name', 'phone', 'address', 'buying_type', 'order_date', 'comment'
        )
