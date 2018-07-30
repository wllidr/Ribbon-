from sina.util.sqlUtil import DBUtil

ips = []
dbUtil = DBUtil(db='pool')
sql = 'SELECT * FROM useip WHERE isuse=1'
datas = dbUtil.fetchAll(sql)
for data in datas:
    ip = data[1] + ':' + data[2]
    ips.append({'ip_port':ip, 'type':data[3]})
PROXIES = ips
# print(ips)

