# 电子词典的设计 #

## 一. 数据库的设计 

-  创建资料库dict ---> `create database dict;`
-  创建三个表格history、user、words
`CREATE TABLE history (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(20) DEFAULT NULL,
  time datetime DEFAULT CURRENT_TIMESTAMP,
  word varchar(20) DEFAULT NULL,
  PRIMARY KEY ("id")
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8`   
   `CREATE TABLE user (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(20) DEFAULT NULL,
  passwd varchar(20) DEFAULT NULL,
  PRIMARY KEY ("id")
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8`   
    `CREATE TABLE words (
  id int(11) NOT NULL AUTO_INCREMENT,
  word varchar(20) DEFAULT NULL,
  interpret varchar(150) DEFAULT NULL,
  PRIMARY KEY ("id")
) ENGINE=InnoDB AUTO_INCREMENT=18873 DEFAULT CHARSET=utf8`  
![数据库以及表格创建](https://i.imgur.com/Yl5kru3.png)  

## 二. 功能实现 ##
- 先在test文件夹下的词典导入到数据库表格words中
- 创建conf文档setting.py用于存储配置
- 客户端和服务器的创建，用套接字来进行创建，中间用进程的方式来实现多客户端同时使用，来完成数据的接收发送
- 要同资料库进行交互，创建db文档mysqlu.py，将同资料库的交互进行类化，只要调用类就可以完成数据库的操作
- menu的创建，总共创建两个界面，一个是用于登陆前的界面，一个是用于登陆后开始进行查词操作的界面
![menu界面](https://i.imgur.com/tW450QQ.png)  
- 登陆确认，查找单词，历史资料，以及创建账户。将这四个操作写于dict_operat文件夹中，将其模块化，当需要的时候进行调用

## 三. 使用方式 ##
- 开启sock_use文件夹下的客户端和服务器端，然后再客户端上按提示进行操作这个简单的电子词典
