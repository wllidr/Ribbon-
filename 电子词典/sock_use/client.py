from socket import *
import sys
import os
from menu.menu import menu,menu2
from conf.settings import IP,PORT


def useapp(ADDR, sk):
    while True:
        menu2()
        choice = input('请输入功能选择（1-3）：')
        if choice == '3':
            sk.send(choice.encode())
            break
        elif choice == '1':
            sk.send(choice.encode())
            sk.recv(1024)
            while True:
                word = input('输入单词(QUIT退出)：')
                sk.send(word.encode())
                if word == 'QUIT':
                    break
                data = sk.recv(1024)
                print(data.decode())

        elif choice == '2':
            sk.send(choice.encode())
            data = sk.recv(1024)
            print(data.decode())
        else:
            print('输入有问题，麻烦按要求输入选择功能')

def main():
    ADDR = (IP, PORT)
    sk = socket(AF_INET, SOCK_STREAM)
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sk.connect(ADDR)
    while True:
        menu()
        message = input('请按照菜单格式输入:')
        if message == 'quit':
            sk.close()
            sys.exit(0)
        else:
            sk.send(message.encode())
            data = sk.recv(1024)
            print(data.decode())
            if data.decode() == 'OK':
                useapp(ADDR, sk)

if __name__ == '__main__':
    main()
