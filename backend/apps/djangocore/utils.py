from django.core.cache import cache
from .models import AppSetting

def get_app_setting(key, default=None):
    value = cache.get(f'app_setting_{key}')
    if value is None:
        try:
            value = AppSetting.objects.get(key=key).value
            cache.set(f'app_setting_{key}', value, timeout=60*60)  # cache for 1 hour
        except AppSetting.DoesNotExist:
            value = default
    return value