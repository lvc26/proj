from django.forms import ModelChoiceField, ModelForm
from django.contrib import admin

from .models import *


class SkirtAdminForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')



class DressAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'category':
            return ModelChoiceField(Category.objects.filter(slug='dress'))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SkirtAdmin(admin.ModelAdmin):

    change_form_template = 'admin.html'
    form = SkirtAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
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

