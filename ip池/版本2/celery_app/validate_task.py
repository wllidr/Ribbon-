from celery_app import app
from time import sleep
from util import validatorDBIp

@app.task
def validateDatebase():
    sleep(2)
    validatorDBIp.start_valida()
    return 'validateDatebase Over'

if __name__ == '__main__':
    validateDatebase()