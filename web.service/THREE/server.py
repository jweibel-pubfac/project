#coding=utf-8

from xmlrpclib import ServerProxy,Fault
from os.path import join, abspath,isfile
from SimpleXMLRPCServer import SimpleXMLRPCServer
from urlparse import urlparse
import sys
import xmlrpclib
import os

SimpleXMLRPCServer.allow_reuse_address = 1

MAX_HISTORY_LENGTH = 6
#最大查询节点数

UNHANDLED = 100
ACCESS_DENIED = 200
#定义错误类---------------------------------------------------------------------
class UnhandledQuery(Fault):
    '''
    that's show can't handle the query exception
    '''
    def __init__(self,message="Couldn't handle the query"):
        Fault.__init__(self, UNHANDLED, message)

class AccessDenied(Fault):
    '''
    when user try to access the forbiden resources raise exception
    '''
    def __init__(self, message="Access denied"):
        Fault.__init__(self, ACCESS_DENIED, message)
#定义错误类---------------------------------------------------------------------

#绝对路径确认的确存在文件----------------------------------------------------------------
def inside(dir,name):
    '''
    check the dir that user defined is contain the filename the user given
    '''
    dir = abspath(dir)
    name = abspath(name)
    return name.startswith(join(dir,''))
#绝对路径确认的确存在文件确认的确存在文件----------------------------------------------------------------

#获得监听端口--------------------------------
def getPort(url):
    '''
    get the port num from the url
    '''
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])
#获得监听端口--------------------------------
#服务类--------------------------------------------------
class Node:
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()

    def query(self, query, history = []):
        try:
            return self._handle(query)
        except UnhandledQuery:
            history = history + [self.url]
            #传递查询记录，节点查询大于6，终止
            if len(history) > MAX_HISTORY_LENGTH: raise
            return self._broadcast(query,history)
    #添加到已知节点
    def hello(self,other):
        self.known.add(other)
        return 0
    #本地调用fetch，self.query查询文件无，广播出去，调用远程query，如果找到文件，返回文件到本地
    def fetch(self, query, secret):

        if secret != self.secret: raise
        result = self.query(query)
        f = open(join(self.dirname, query),'wb')
        f.write(result.data)
        f.close()
        return 0

    #远程调用方法
    def _start(self):
        s = SimpleXMLRPCServer(("",getPort(self.url)),logRequests=False)
        s.register_instance(self)
        #添加自身类，该方法一启动，整个类都可以远程调用
        s.serve_forever()
    #各服务器本地查询文件是否存在-------------------------
    def _handle(self, query):
        dir = self.dirname
        name = join(dir, query)
        if not isfile(name):raise UnhandledQuery
        if not inside(dir,name):raise AccessDenied
        return xmlrpclib.Binary(open(name,'rb').read())
    #各服务器本地查询文件是否存在-------------------------
    def list(self,history = []):
        return ['【'+ self.url.split('//')[1]+'】'+'文件列表：']+os.listdir(self.dirname)
        #[self.url]
    #广播到已知节点，查询文件------------------------------
    def knownlist(self):
        return list(self.known.copy())
    def _broadcast(self, query, history):
    
        for other in self.known.copy():
            #本地已知节点是否在查询记录中，存在则跳过
            if other in history: continue
            try:
                s = ServerProxy(other)
                return s.query(query, history)
            except Fault, f:
                if f.faultCode == UNHANDLED:pass
                else: self.known.remove(other)
            except:
                self.known.remove(other)

        raise UnhandledQuery
     #广播到已知节点，查询文件------------------------------
#服务类--------------------------------------------------
def main():
    url, directory, secret = sys.argv[1:]
    n = Node(url,directory,secret)
    n._start()

if __name__ == '__main__': 
    main()

