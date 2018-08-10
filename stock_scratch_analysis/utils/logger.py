'''
    Author: Ribbon Huang
    Date : 2018 - 08 - 07
    记录日常日志模块调用
'''
import logging

class Logger:
    def __init__(self):
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    def createLogger(self, loggerName):
        self.logger = logging.getLogger(loggerName)
        self.fileHandler = logging.FileHandler(loggerName + '.log')
        self.fileHandler.setFormatter(self.formatter)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.fileHandler)
        return self.logger

    def removeLogger(self):
        self.logger.removeHandler(self.fileHandler)

LOGGER = Logger()