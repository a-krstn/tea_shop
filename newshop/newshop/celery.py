import os
from celery import Celery

# задать стандартный модуль настроек Django для программы celery

# задается переменная окружения для встроенной в Celery программы командной строки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newshop.settings')
# создается экземпляр приложения
app = Celery('newshop')
# загружается любая конкретно-прикладная конфигурация из настроек проекта
app.config_from_object('django.conf:settings', namespace='CELERY')
# Celery будет автоматически обнаруживать асинхр. задания в приложениях
app.autodiscover_tasks()
