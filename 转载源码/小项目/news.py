#!/usr/bin/python
# encoding: utf-8
#这个程序的主要功能是用来从指定的来源（这里是Usenet新闻组）收集信息
#然后讲这些信息保存到指定的目的文件中（这里使用了两种形式：纯文本和html文件）
#这个程序的用处有些类似于现在的博客订阅工具或者叫RSS订阅器

from nntplib import NNTP
#NNTP专门用于从新闻服务器接受信息
from time import strftime,time,localtime
from email import message_from_string
from urllib import urlopen
import textwrap
import re

day = 24*60*60
#定义一天的秒数，接下来从服务器查文章，会用到时间
def wrap(string,max=70):
        '''

        '''
        return '\n'.join(textwrap.wrap(string)) + '\n'
#wrap()函数，把字符串拆分成了一个序列，在这个序列中，每个元素的长度是一样的，默认值为70
#.join将list合并成一个字符串，中间插入/n换行，最终达到每行70字的格式

class NewsAgent:
        '''
        '''
        def __init__(self):
                self.sources = []
                #此时是两个封装类，已经传入参数
                #新闻的来源
                self.destinations = []
                #处理函数列表
        def addSource(self,source):
                self.sources.append(source)
                #添加来源
        def addDestination(self,dest):
                self.destinations.append(dest)
                #添加处理函数
        def distribute(self):

                items = []
                for source in self.sources:
                        items.extend(source.getItems())
                        #itens添加多个NewsItem(title,body)封装类
                for dest in self.destinations:
                        dest.receiveItems(items)

class NewsItem:
        def __init__(self,title,body):
                self.title = title
                self.body = body
#新闻服务起处理函数
class NNTPSource:
        def __init__(self,servername,group,window):
                self.servername = servername
                self.group = group
                self.window = window

        def getItems(self):
                start = localtime(time() - self.window*day)
                #处理时间，确定获取哪一天的文章，day为一天的秒数
                date = strftime('%y%m%d',start)
                hour = strftime('%H%M%S',start)
                #获取新闻-------------------------------------------------------
                server = NNTP(self.servername)

                ids = server.newnews(self.group,date,hour)[1]

                for id in ids:
                        lines = server.article(id)[3]
                        message = message_from_string('\n'.join(lines))

                        title = message['subject']
                        body = message.get_payload()
                        if message.is_multipart():
                                body = body[0]
                #获取新闻-------------------------------------------------------
                        yield NewsItem(title,body)
                        #此时多次循环，返回一个一个list，包含多个NewsItem(title,body)封装类
                server.quit()

class SimpleWebSource:

        def __init__(self,url,titlePattern,bodyPattern):
                self.url = url
                self.titlePattern = re.compile(titlePattern)
                self.bodyPattern = re.compile(bodyPattern)
                #re.compile对象，可利用正则表达式查找text符合规则的字符串，返回一个list
                #接受参数，url、需要查找的标签正则表达式

        def getItems(self):
                #读取页面内容
                text = urlopen(self.url).read()
                titles = self.titlePattern.findall(text)
                bodies = self.bodyPattern.findall(text)
                for title,body in zip(titles,bodies):
                                  #zip用于处理两个list，返回多个list，原两个list元素两两配对  
                        yield NewsItem(title,wrap(body))
                #此时多次循环，返回一个一个list，包含多个NewsItem(title,body)封装类

#处理函数，打印出每篇文章信息
class PlainDestination:

        def receiveItems(self,items):
                for item in items:
                        print item.title
                        print '-'*len(item.title)
                        print item.body
#生成html文件的处理函数
class HTMLDestination:

        def __init__(self,filename):
                self.filename = filename
                #保存的文件名
        def receiveItems(self,items):
                out = open(self.filename,'w')
                print >> out,'''
                <html>
                <head>
                 <title>Today's News</title>
                </head>
                <body>
                <h1>Today's News</hi>
                '''

                print >> out, '<ul>'
                id = 0
                for item in items:
                        id += 1
                        print >> out, '<li><a href="#">%s</a></li>' % (id,item.title)
                        #使用id作引索，先打印文章题目
                print >> out, '</ul>'

                id = 0
                for item in items:
                        id += 1
                        print >> out, '<h2><a name="%i">%s</a></h2>' % (id,item.title)
                        print >> out, '<pre>%s</pre>' % item.body
                        #打印文章正文

                print >> out, '''
                </body>
                </html>
                '''
def runDefaultSetup():

        agent = NewsAgent()
        #正则表达式，寻要匹配的文章标签
        bbc_url = 'http://news.bbc.co.uk/text_only.stm'
        bbc_title = r'(?s)a href="[^"]*">\s*<b>\s*(.*?)\s*</b>'
        bbc_body = r'(?s)</a>\s*<br/>\s*(.*?)\s*<'
        bbc = SimpleWebSource(bbc_url, bbc_title, bbc_body)
        #封装类，添加到来源中
        agent.addSource(bbc)

        clpa_server = 'news2.neva.ru'
        clpa_group = 'alt.sex.telephone'
        clpa_window = 1
        clpa = NNTPSource(clpa_server,clpa_group,clpa_window)
        
        agent.addSource(clpa)

        agent.addDestination(PlainDestination())
        agent.addDestination(HTMLDestination('news.html'))

        agent.distribute()
if __name__ == '__main__':
        runDefaultSetup()
