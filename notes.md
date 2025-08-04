# Notes to setup and run

## new app needs new FIELD_ENCRYPTION_KEY

```bash
cd backend
python generate_encryption_key.py
-- save to djanproj/settings.py
```

## Django app

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### dev only user and pass

jakub
jakub123456

## Redis for Celery task queue

in docker

## Celery start on windows

```bash
cd .\backend\
celery -A djanproj worker -l info --pool=solo 
```

## test individual functions

```bash
python manage.py shell
```

```python
from apps.upgates_integration.sync_logic import process_stock_adjustments
process_stock_adjustments()
```

```python
from apps.upgates_integration.tasks import process_stock_adjustments_task
process_stock_adjustments_task.delay() # for celery test
process_stock_adjustments_task() # w/o celery
```

## Frontend

```bash
cd .\frontend\
npm start
```