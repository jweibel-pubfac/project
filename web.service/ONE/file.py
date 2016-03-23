#!/usr/bin/env python
#coding:utf-8
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import os.path
import urllib.parse
from html.parser import HTMLParser
import io, json, subprocess, tempfile
import sys
from urllib import request


from tornado.options import options, define
define("port", default="8000", help="run on the given pot", type=int)

EXEC = sys.executable
TEMP = tempfile.mkdtemp(suffix='_py', prefix='learn_python_')
r = dict()

def decode(s):
    try:
        return s.decode('utf-8')
    except UnicodeDecodeError:
        return s.decode('gbk')

#在线python生成临时文件
def write_py(code):
    fpath = os.path.join(TEMP, 'pyonline.py')
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Code wrote to: %s' % fpath)
    return fpath
#处理文件上传
class Upload(tornado.web.RequestHandler):

    def post(self):
        try:
            # 文件的暂存路径
            upload_path = os.path.join(os.path.dirname(__file__), 'files')
            # 提取表单中‘name’为‘file’的文件元数据
            file_metas = self.request.files['upload']
            for meta in file_metas:
                filename = meta['filename']
                filepath = os.path.join(upload_path, filename)
                # 有些文件需要已二进制的形式存储，实际中可以更改
                with open(filepath, 'wb') as up:
                    up.write(meta['body'])
            files = getfiles()
            files.sort()
            self.render("file.html", filelist=files)
        except Exception:
            files = getfiles()
            files.sort()
            self.render("file.html", filelist=files)

#处理在线爬虫
class parser(HTMLParser):
    a_text = False
    def __init__(self):   
        HTMLParser.__init__(self)   
        self.ddata=[] 
        self.ttag=[]
    def handle_starttag(self,tag,attr):  
        if tag in self.ttag:  
            self.a_text = True  
            #print (dict(attr))  
              
    def handle_endtag(self,tag):  
        if tag in self.ttag: 
            self.a_text = False  
              
    def handle_data(self,data):  
        if self.a_text:  
            self.ddata.append(data)

hp = parser()
 
#处理下载
class Download(tornado.web.RequestHandler):

    def get(self):
        upload_path = os.path.join(os.path.dirname(__file__), 'files')
        filename = self.get_argument('filename')
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header(
            'Content-Disposition', 'attachment; filename=' + filename)
        filepath = os.path.join(upload_path, filename)
        buf_size = 4096
        with open(os.path.join('', filepath), 'rb') as f:
            while True:
                data = f.read(buf_size)
                if not data:
                    break
                self.write("data")
        self.finish()

#处理删除操作
class Delete(tornado.web.RequestHandler):

    def get(self):
        fileurl = self.get_argument("fileurl")
        os.remove("/root/folder/python/" + fileurl)
        files = getfiles()
        files.sort()
        self.render("file.html", filelist=files)

class Shellstart(tornado.web.RequestHandler):
    def post(self):
        shell=self.get_argument("shell")
        password=self.get_argument("password")
        if password=='liupan':
            os.system(shell)
        files = getfiles()
        files.sort()
        self.render("shell.html")
class Myparser(tornado.web.RequestHandler):
    def post(self):
        try:  
            hp.ttag.append(self.get_argument("tag"))
            self.render("parser.html",result=[],tags=hp.ttag)
        except Exception:
            try:
                file_metas = self.request.files['upload'] 
                upload_path = os.path.join(os.path.dirname(__file__), 'files')
                for meta in file_metas:
                    filename = meta['filename']
                    filepath = os.path.join(upload_path, filename)
                # 有些文件需要已二进制的形式存储，实际中可以更改
                    html=(str(meta['body'], encoding = "utf-8"))
                hp.feed(html)
                self.render("parser.html",result=hp.ddata,tags=[])
                hp.ddata=[]
                hp.ttag=[]
            except Exception:
                try:
                    parsertarger=self.get_argument("targer")
                    with request.urlopen(parsertarger) as f:
                        htmldatas = f.read()
                        HTMLdata=str(htmldatas, encoding = "utf-8")
                        hp.feed(HTMLdata) 
                        self.render("parser.html",result=hp.ddata,tags=[])
                        hp.ddata=[]
                        hp.ttag=[]
                except Exception:
                        hp.ttag=[]
                        hp.ddata=[]
                        self.render("parser.html",result=[],tags=[])

class Runpython(tornado.web.RequestHandler):
    def post(self):
        codes=self.get_argument("code") 
        path = write_py(codes)
        try:
            r['output'] = decode(subprocess.check_output([EXEC, path], stderr=subprocess.STDOUT, timeout=15))
            self.render("result.html",results=r['output'])
        except Exception:
            r['output'] = decode(subprocess.check_output(['/usr/bin/python2', path], stderr=subprocess.STDOUT, timeout=15))
            self.render("result.html",results=r['output'])


#返回页面 
class Index(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
class Fileshare(tornado.web.RequestHandler):
    def get(self):
        files = getfiles()
        files.sort()
        self.render("file.html", filelist=files)
class Shell(tornado.web.RequestHandler):
    def get(self):
        self.render("shell.html")

class parserindex(tornado.web.RequestHandler):
    def get(self):
        self.render("parser.html",result=[],tags=[])
class Pyonline(tornado.web.RequestHandler):
    def get(self):
        self.render("python.html")



#获得已上传文件信息
def getfiles():
    filels = []
    filespath = "/root/folder/python/files"
    for files in os.walk(filespath):
        for f in files[2]:
            filels.append(("/files/" + f, f))
    return filels[:]
    

handlers = [(r"/", Index),
                    (r"/delete", Delete),
                    (r"/download", Download),
                    (r"/upload", Upload),
                    (r"/shell",Shell),
                    (r"/shellstart",Shellstart),
                    (r"/fileshare",Fileshare),
                    (r"/myparser",Myparser),
                    (r"/htmlparser",parserindex),
                    (r"/run",Runpython),
                    (r"/pyonline",Pyonline)
                    ]
settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True
        )
print('Http server start at port 8000')
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app=tornado.web.Application(handlers, **settings)
    httpserver = tornado.httpserver.HTTPServer(app)
    httpserver.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
