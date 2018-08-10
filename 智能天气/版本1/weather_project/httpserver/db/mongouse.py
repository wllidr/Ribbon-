from pymongo import MongoClient
import json
from conf.settings import MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION

def conveydata(city):
    client = MongoClient(MONGO_HOST,MONGO_PORT)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    airQuality = []
    humidity = []
    temperature = []
    jsondocument = {}
    cursors = collection.find({'city':city},{'id':0})
    client.close()
    for i in range(8):
        p = cursors[0]['weather'][3 * i].values()
        for infos in p:
            airQuality.append(int(infos[0]['airQuality']))
            humidity.append(int(infos[1]['humidity'].split('%')[0]))
            temperature.append(int(infos[2]['temperature'].split('℃')[0]))
    jsondocument['air'] = airQuality
    jsondocument['temperature'] = temperature
    jsondocument['humidity'] = humidity
    return json.dumps(jsondocument, ensure_ascii=False)

if __name__ == '__main__':
    print(conveydata('广州'))