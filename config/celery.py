# celery.py
import os
from celery import Celery
from django.conf import settings

# Establecer la configuración de Django para Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Configurar Celery usando settings de Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Cargar tareas desde todas las apps registradas
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
