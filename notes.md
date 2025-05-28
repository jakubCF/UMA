# Notes to setup and run

## new app needs new FIELD_ENCRYPTION_KEY

```bash
cd backend
python generate_encryption_key.py
-- save to djanproj/settings.py
```

## Celery start on windows

```bash
celery -A djanproj worker -l info --pool=solo 
```

