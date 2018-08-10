from __future__ import absolute_import
from celery import Celery

app = Celery('crawl_task')    # 创建 Celery 实例
app.config_from_object('conf.celeryconfig')   # 通过 Celery 实例加载配置模块