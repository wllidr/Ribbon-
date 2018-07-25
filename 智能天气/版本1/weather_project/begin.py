from multiprocessing import Process
from spider_start import start_spider
from httpserver.HttpServer import webstart
from weather.seleniumUse import start_browser


if __name__ == '__main__':
    # p1 = Process(target=start_spider)
    p2 = Process(target=webstart)
    # p1.start()
    p2.start()
    browser = start_browser('http://127.0.0.1:8000')
    # p1.join()
    p2.join()
