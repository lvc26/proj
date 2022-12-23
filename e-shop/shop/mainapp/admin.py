from django.forms import ModelChoiceField, ModelForm
from django.contrib import admin

from .models import *




class DressAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Если поле является внешним ключом к модели категории, то верните ModelChoiceField, которое только
        содержит категорию с надписью "dress"
        :param db_field: Поле, которое запрашивается
        :param request: Текущий объект запроса
        ::return: Возвращается метод ключа формы field_for_foreign.
        """
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='dress'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SkirtAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Если поле является внешним ключом к модели категории, то верните ModelChoiceField, которое только
        содержит категорию с надписью "skirt".
        :param db_field: Поле, которое запрашивается.
        :param request: Текущий объект запроса.
        ::return: Возвращается метод ключа формы field_for_foreign.
        """
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='skirt'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Dress, DressAdmin)
admin.site.register(Skirt, SkirtAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)


