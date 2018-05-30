from db.mysqlu import MysqlUse

def findword(word, name):
    string = ''
    msql = MysqlUse()
    sql = "select word,interpret from words where word='%s' "%word
    datas = msql.fetch(sql)

    if datas:
        sql = "insert into history (name,word)values ('%s','%s')" % (name, word)
        msql.excute(sql)
        for data in datas:
            string += data[0] + '\t' + data[1] + '\n'
        return string
    else:
        return '没有查到该单词'

def findhistory():
    string = ''
    msql = MysqlUse()
    sql = "select name,time,word from history limit 10"
    datas = msql.fetch(sql)
    for data in datas:
        string += data[0] + '\t' + data[2] + '\t' + str(data[1]) + '\n'
    return string