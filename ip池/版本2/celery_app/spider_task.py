from spider import Spider
from celery_app import app
import time

@app.task
def spiderTask():
    time.sleep(2)
    Spider.spider_start()
    return 'Over'


