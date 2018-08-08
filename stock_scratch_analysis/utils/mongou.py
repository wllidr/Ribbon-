'''
    Author: Ribbon Huang
    MongoDB的调用的封装
'''
from utils.logger import LOGGER
import pymongo
from conf.settings import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_SHEET, LOGGER_MONGO_NAME
from pymongo.errors import WriteError, WTimeoutError, ConnectionFailure
import numpy as np
import pandas as pd

# 记录日常日志
logger = LOGGER.createLogger(LOGGER_MONGO_NAME)

class MongoUse:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(host = MONGO_HOST, port = MONGO_PORT)
        except ConnectionFailure:
            logger.warning('MongoDB ConnectionFailure')
        except TypeError:
            logger.warning('MongoDB Variables is error')

        db = self.client[MONGO_DB]
        self.sheet = db[MONGO_SHEET]

    def insertDb(self, info):
        try:
            self.sheet.insert(info)
        except WriteError:
            logger.warning('Write Error')
        except WTimeoutError:
            logger.warning('Write Timeout Error')

    def find(self):
        try:
            datas = self.sheet.find({}, {'_id':0}).sort('code', pymongo.ASCENDING)
            for data in datas:
                df = pd.DataFrame(np.array(data['line']), columns=['date', 'price', 'other'])
                yield df
            # return datas
        except TypeError:
            logger.warning('Type Error')

    def close(self):
        self.client.close()

if __name__ == '__main__':
    mongo = MongoUse()
    mongo.find()

LOGGER.removeLogger()