from xml.sax.handler import ContentHandler
from xml.sax import parse
import os
#处理xml，生成目录文件夹，并保存各类文章html文件

#处理xml，dispatch根据返回的标签名，确定调用什么函数------------------
class Dispatcher:
        def dispatch(self, prefix, name, attrs=None):
                mname = prefix + name.capitalize()
                dname = 'default' + prefix.capitalize()
                method = getattr(self, mname, None)
                if callable(method): args = ()
                else:
                        method = getattr(self, dname, None)
                        args = name,
                if prefix == 'start': args += attrs,
                if callable(method): method(*args)

        def startElement(self, name, attrs):
                self.dispatch('start', name, attrs)

        def endElement(self, name):
                self.dispatch('end', name)
#处理xml，dispatch根据返回的标签名，确定调用什么函数------------------
#多重继承，处理函数
class WebsiteConstructor(Dispatcher, ContentHandler):
        passthrough = False

        def __init__(self, directory):
                self.directory = [directory]
                #通过list添加删除，动态改变路径
                self.ensureDirectory()
        #确认是否存在文件夹，不存在则创建-------------------------
        def ensureDirectory(self):
                path = os.path.join(*self.directory)
                print path
                print '----'
                if not os.path.isdir(path): os.makedirs(path)
        #确认是否存在文件夹，不存在则创建-------------------------
        #每次遇到page标签，passthrough = true，该函数处理文章内容------
        def characters(self, chars):
                if self.passthrough: self.out.write(chars)
        #每次遇到page标签，passthrough = true，该函数处理文章内容------
        
        #page内标签默认使用该函数，直接打印出标签以及属性-------------------------------
        def defaultStart(self, name, attrs):
        if self.passthrough:
                        self.out.write('<' + name)
                        for key, val in attrs.items():
                                self.out.write(' %s="%s"' %(key, val))
                        self.out.write('>')
        def defaultEnd(self, name):
                if self.passthrough:
                        self.out.write('</%s>' % name)
        #page内标签默认使用该函数，直接打印出标签以及属性-------------------------------
        #目录的开始
        def startDirectory(self, attrs):
                self.directory.append(attrs['name'])
                #添加路径
                self.ensureDirectory()
                #不存在目录文件夹，则创建
        def endDirectory(self):
                print 'endDirectory'
                self.directory.pop()
        #page标签开始
        def startPage(self, attrs):
                print 'startPage'
                #添加路径，创建文章文件
                filename = os.path.join(*self.directory + [attrs['name']+'.html'])
                self.out = open(filename, 'w')
                self.writeHeader(attrs['title'])
                #html文件开头
                self.passthrough = True
                #self.passthrough = True，以处理文章内容
        #文章结束
        def endPage(self):
                print 'endPage'
                self.passthrough = False
                self.writeFooter()
                #html结束
                self.out.close()
        
        def writeHeader(self, title):
                self.out.write('<html>\n <head>\n   <title>')
                self.out.write(title)
                self.out.write('</title>\n </head>\n  <body>\n')

        def writeFooter(self):
                self.out.write('\n </body>\n</html>\n')

parse('website.xml',WebsiteConstructor('public_html'))
