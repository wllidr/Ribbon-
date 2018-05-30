import re
from db.mysqlu import MysqlUse

f = open('dict.txt')
mysqluse = MysqlUse()

for string in f:
    try:
        # print(string[0:17])
        data = string[0:17]
        interpret = string[18:]
        datas = re.findall('\w+\s',data)
        word = ''
        for data in datas:
            word += data
        interpret = re.sub('\n','',interpret)
        sql = "insert into words (word,interpret) VALUES ('%s','%s')" %(word,interpret)
        mysqluse.excute(sql=sql)
        print(word,interpret)
    except:
        pass
    # input('1')
mysqluse.close()