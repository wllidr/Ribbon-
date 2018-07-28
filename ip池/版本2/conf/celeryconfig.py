from datetime import timedelta
from celery.schedules import crontab

# Broker and Backend
BROKER_URL = "redis://localhost:6379/2"  # 指定 Broker
# CELERY_RESULT_BACKEND = "redis://localhost:6379/3"  # 指定 Backend

# Timezone
CELERY_TIMEZONE = 'Asia/Shanghai'  # 指定时区，不指定默认为 'UTC'

# import
CELERY_IMPORTS = (
    'celery_app.spider_task',
    'celery_app.validate_task'
)

# schedules
CELERYBEAT_SCHEDULE = {
    'spider-fixed-time': {
        'task': 'celery_app.spider_task.spiderTask',
        'schedule': crontab(hour=11, minute=30),  # 每 30 秒执行一次
    },
    'validate-every-2-hours': {
        'task': 'celery_app.validate_task.validateDatebase',
        'schedule': timedelta(hours=2),
    }
}

