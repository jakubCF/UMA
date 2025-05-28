import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
# This ensures Celery picks up your Django project's settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djanproj.settings') # <--- CHANGE IS HERE
# Or, if you have a base.py, you might set it to 'djanproj.settings.base'
# and let local.py/production.py handle overrides.
# For simplicity, during development, 'djanproj.settings.local' is often used.

app = Celery('djanproj') # Create a Celery application instance named 'djanproj'

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# This tells Celery to look for `tasks.py` files inside each app in INSTALLED_APPS.
app.autodiscover_tasks()

# Optional: Add a simple debug task for testing Celery setup
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')