Добро пожаловать в наш интернет - магазин "Shining Star".

Чтобы установить магазин на Ваш компьютер, Вам необходимо:
Открыть Visual Studio Code и нажать на Clone Git Repository.
Прописать команду в открытом окошке https://github.com/lvc26/proj.git, выбрать удобную для вас папку, куда установится проект.
Установка готова😊
Если после вышеперечисленных действий у Вас не пропало желание полюбоваться нашим офигенным сайтом, то дальше открываем консоль или терминал и прописываем поэтапно следующие команды:

Для WINDOWS:
Создаем виртуальное окружение Python: python -m venv shop.
Активируем виртуальное окружение Python: shop\Scripts\activate.
C помощью команды cd переходим в папку e-shop.
Устанавливаем нужные библиотеки: pip install -r requirements.txt.
В папке shop создаём две папки с названиями: static, static_dev.
Прописываем команду python manage.py makemigrations, затем python manage.py migrate.
Остается прописать последнюю команду python manage.py runserver и можно наслаждаться нашим сайтом.

Для MAC:
Сначала переходим в папку: cd e-shop, затем cd shop и создаем виртуальное окружение Python: pipenv shell
Устанавливаем нужные библиотеки: pip install -r requirements.txt, pip install pillow, pip install django, pip install django-crispy-forms.
В папке shop создаём две папки с названиями: static, static_dev.
Прописываем команду python3 manage.py makemigrations, затем python3 manage.py migrate.
Остается прописать последнюю команду python3 manage.py runserver и можно наслаждаться нашим сайтом.
Приятного просмотра, с любовью Алиса и Лена ❤️
