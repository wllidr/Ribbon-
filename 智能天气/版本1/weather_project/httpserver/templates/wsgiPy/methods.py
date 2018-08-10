import time
from conf.settings import HTML_ROOT_DIR

def mainPage(env, set_headers):
    status = '200 OK'
    headers = []
    set_headers(status, headers)
    file = open(HTML_ROOT_DIR + '/index.html', 'rb')
    file_data = file.read()
    file.close()
    return file_data.decode()


def login(env, set_headers):
    status = '200 OK'
    headers = []
    set_headers(status, headers)
    file = open(HTML_ROOT_DIR + '/index1LoginReturn.html', 'rb')
    file_data = file.read()
    file.close()
    return file_data.decode()

def forget(env, set_headers):
    status = '200 OK'
    headers = []
    set_headers(status, headers)
    file = open(HTML_ROOT_DIR + '/index2ForgetPwd.html', 'rb')
    file_data = file.read()
    file.close()
    return file_data.decode()

def request(env, set_headers):
    status = '200 OK'
    headers = []
    set_headers(status, headers)
    file = open(HTML_ROOT_DIR + '/index3RegisterSu.html', 'rb')
    file_data = file.read()
    file.close()
    return file_data.decode()

def voice(env, set_headers):
    pass

def requestHandler(env, set_headers):
    status = '200 OK'
    headers = []
    set_headers(status, headers)
    return 'Hello World'

