# 套接字IP端口
IP = '127.0.0.1'
PORT = 8000

# 设置静态网页文件路径
HTML_ROOT_DIR = 'httpserver/templates/static'

# 存放python方法
PYTHON_DIR = 'httpserver/templates/wsgiPy'

# 导入框架所需参数
MODUL_NAME = 'webFrame'
MODUL_APP = 'app'

# Mysql数据库
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DB = 'weather'
MYSQL_USER = 'root'
MYSQL_PASSWD = '12321hjz'

# MongoDB数据库
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = 'weather'
MONGO_COLLECTION = 'total'

# urlpatterns
URLPATTERNS = [
    ("/", '/index.html'),  # 返回首页index.html
    ("/Login", '/index1LoginReturn.html'),  # 登陆返回的页面index1.html
    ("/forget_pwd", '/index2ForgetPwd.html'),  # 返回首页index2.html
    ("/Register", '/index3RegisterSu.html'),  # 注册成功返回的页面index3.html
    # ("/Voice/", voice),  # ajax实现异步数据交互  以单词"startVoice"开启语音接口（post方式），返回json文档给前端解析
    # ("/Request/", requestHandler),  # ajax实现异步数据交互  以post方式{cityName:c_name}发送，返回尽可能多的信息给前端解析
]