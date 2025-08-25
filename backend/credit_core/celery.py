import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "credit_core.settings")
app = Celery("credit_core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()