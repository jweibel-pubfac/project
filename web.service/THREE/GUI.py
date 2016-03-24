#coding=utf-8
from xmlrpclib import ServerProxy,Fault
from server import Node,UNHANDLED 
from threading import Thread
from time import sleep
from os import listdir
from random import choice
from string import lowercase
import sys
import wx

HEAD_START = 0.1 #Seconds
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

#查询本地文件夹已有文件---------------------
class ListableNode(Node):
    def list(self):
        return listdir(self.dirname)
#查询本地文件夹已有文件---------------------

class Client(wx.App):
    def __init__(self, url, dirname, urlfile):
        self.secret = randomString(SECRET_LENGTH)
        n = ListableNode(url,dirname, self.secret)
        t = Thread(target=n._start)
        t.setDaemon(1)
        t.start()

        sleep(HEAD_START)
        self.server = ServerProxy(url)
        self.urlfile=urlfile

        #run gui
        #继承父类
        super(Client, self).__init__()
    #更新本地文件列表--------------------------
    def updateList(self):
        self.files.Set(self.server.list())
    #更新本地文件列表--------------------------
    def OnInit(self):
        #设置框架
        win = wx.Frame(None, title="File Sharing Client",size=(400,399))
        #框架上设置面板bkg
        bkg = wx.Panel(win)
        #面板上设置输入框
        self.input = input = wx.TextCtrl(bkg)
        #面板上设置按钮，Fetch
        submit = wx.Button(bkg, label="Fetch",size=(80,25))
        submit.Bind(wx.EVT_BUTTON, self.fetchHandler)
        #按钮时间放声，触发self.fetchHandler

        hbox = wx.BoxSizer()

        hbox.Add(input, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        hbox.Add(submit, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        #设置列表box:self.files，列出本地文件
        self.files = files = wx.ListBox(bkg)
        self.updateList()

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND)
        vbox.Add(files, proportion=1,flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        bkg.SetSizer(vbox)

        win.Show()

        return True

    def fetchHandler(self, event):
        #获取输入框的文本内容
        query =self.input.GetValue()
        for line in open(self.urlfile):
            line = line.strip()
            self.server.hello(line)
        try:
            #调用服务器查询下载文件
            self.server.fetch(query, self.secret)
            self.updateList()
            #更新列表

        except Fault,f:
            if f.faultCode != UNHANDLED: raise
            print "Counldn't find the file",query

def main():
    urlfile, directory,url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.MainLoop()

if __name__ == '__main__':
    main()
