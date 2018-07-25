import redis
import pymysql
import json

def process_item():
    # 创建redis连接
    rediscli = redis.Redis(host='127.0.0.1',port=6379,db=0)

    # 创建pymysql连接
    mysqlcli = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='12321hjz',db='hjz')

    cursor = mysqlcli.cursor()
    offset = 0
    while True:
        # redis 数据表名 和 数据
        source, data = rediscli.blpop("novel:items")
        offset += 1
        # 将json对象转换为Python对象
        data = json.loads(data)
        # 将数据插入到表里
        sql = "insert into novel (title, url) VALUES ('%s','%s')" %(data['title'],data['url'])
        cursor.execute(sql)
        mysqlcli.commit()
        print(offset)
        cursor.close()
    mysqlcli.close()

if __name__ == '__main__':
    process_item()


