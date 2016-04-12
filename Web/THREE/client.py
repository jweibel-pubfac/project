#coding=utf-8

#使用说明
#每个节点创建一个文件夹储存本地文件
#创建url.txt储存已知节点，每次查询会从此输入节点信息，并保存至已知节点中
#python client.py url.txt 本地文件夹名 127.0.0.1:port(服务器监听地址)

from xmlrpclib import ServerProxy, Fault
from cmd import Cmd
from random import choice
from string import lowercase
from server import Node,UNHANDLED  
#引入前面的server
from threading import Thread
from time import sleep

import sys

HEAD_START = 0.1
SECRET_LENGTH = 100
#生成随机密码，防止别人控制本地node服务器---------------------------------
def randomString(length):
    chars = []
    letters = lowercase[:26]
    while length > 0:
        length -= 1
        chars.append(choice(letters))
    return ''.join(chars)
#生成随机密码，防止别人控制本地node服务器---------------------------------
#定义客户端------------------------------------------------------------
class Client(Cmd):
    prompt = '> '

    def __init__(self, url, dirname, urlfile):
    #url本地服务器监听地址，dirname本地文件夹，urlfile所知的节点
        Cmd.__init__(self)
        self.secret = randomString(SECRET_LENGTH)
        #设置服务器
        n = Node(url, dirname, self.secret)
        t = Thread(target = n._start)
        t.setDaemon(1)
        t.start()
        #开启服务器
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        #调用本地服务器方法，如果找不到文件，自动向已知节点广播
        self.urlfile=urlfile

    def do_fetch(self, arg):
        try:
            #每次查询文件时，都添加节点，防止无法及时加入新节点
            for line in open(self.urlfile):
                line = line.strip()
                self.server.hello(line)
            self.server.fetch(arg,self.secret)
        except Fault,f:
            if f.faultCode != UNHANDLED: raise
            print "Couldn't find the file",arg

    def do_exit(self,arg):
        print
        sys.exit()

    do_EOR = do_exit
#定义客户端------------------------------------------------------------
def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()

if __name__ == '__main__':
    main()
