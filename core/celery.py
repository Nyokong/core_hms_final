from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.update(
    CELERY_IMPORTS=('api.tasks',)
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure Celery to use Django's logging settings
app.conf.update(
    worker_hijack_root_logger=False,
)