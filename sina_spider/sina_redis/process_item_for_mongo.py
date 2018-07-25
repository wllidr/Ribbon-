import redis
import pymongo
import json

def process_item():
    # 创建redis连接
    rediscli = redis.Redis(host='127.0.0.1',port=6379,db=0)

    # 创建pymysql连接
    mongocli = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = mongocli.hjz
    sheet = db.novel
    offset = 0

    while True:
        # redis 数据表名 和 数据
        source, data = rediscli.blpop("novel:items")
        if not data:
            break
        offset += 1
        # 将json对象转换为Python对象
        data = json.loads(data)
        # 将数据插入到sheetname表里
        sheet.insert(data)
        print(offset)
    mongocli.close()

if __name__ == '__main__':
    process_item()


