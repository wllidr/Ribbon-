'''MONGODB类化使用'''
from pymongo import MongoClient
from conf.settings import MONGO_HOST,MONGO_PORT,MONGO_DB,MONGO_SHEET

class MongoUse:
    def __init__(self, host = MONGO_HOST, port = MONGO_PORT, db = MONGO_DB, sheet = MONGO_SHEET):
        self.client = MongoClient(host, port)
        self.db = self.client[db]
        self.sheet = self.db[sheet]

    def db_operat(self, operat, sql):
        if operat == 'insert':
            self.sheet.insert(sql)
        elif operat == 'remove':
            self.sheet.remove(sql)
        elif operat == 'update':
            self.sheet.update(sql)
        self.close()

    def close(self):
        self.client.close()

if __name__ == '__main__':
    mongo = MongoUse()
    sql = {'name':'1', 'age':28}
    mongo.db_operat('insert', sql)
