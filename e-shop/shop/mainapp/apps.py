from django.apps import AppConfig


class MainappConfig(AppConfig):
    # Создаем новое приложение под названием mainapp.
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'
