#!/usr/bin/env python
#-*- coding:utf-8 -*-
#该模块负责处理浏览器请求
#数据库查询在model模块中，文章分页在component模块中
#先调用install.py，初始化数据库，以及设置管理员用户名、密码等
import torndb
import tornado.httpserver
import tornado.web
import tornado.ioloop
import os.path
import markdown
import ConfigParser
import re

from model import Article, Label, Auth, Search
from component import Paginator
from tornado.options import define, options
import sys
from threading import Timer  

reload(sys)
sys.setdefaultencoding( "utf-8" )



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/article/(\d+)', ArticleHandler),
            (r"/about", AboutHandler),
            (r"/music", MusicHandler),
            (r"/prose", ProseHandler),
            (r"/program", ProgramHandler),
            (r'/createArticle', CreateArticleHandler),
            (r'/preview', PreviewHandler),
            (r'/article/edit/(\d+)', EditArticleHandler),
            (r'/article/delete/(\d+)', DeleteHandler),
            (r'/search', SearchHandler),
            (r'/article/update/(\d+)', UpdateArticleHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/auth', AuthHandler),
        ]
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            autoescape=None,
            xsrf_cookies=True,
            cookie_secret='6de683f6e8f038f62863fe27a17573e5',
            login_url='/login',
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = torndb.Connection(
            host=options.mysql_host, database=options.mysql_database,
            user=options.mysql_user, password=options.mysql_password
        )


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def write_error(self, status_code, **kwargs):
        if status_code == 400:
            error = "400: Bad Request"
            self.render('error.html', error=error, home_title=options.home_title)
        if status_code == 405:
            error = "405: Method Not Allowed"
            self.render('error.html', error=error, home_title=options.home_title)
        if status_code == 404:
            error = "404: Page Not Found"
            self.render('error.html', error=error, home_title=options.home_title)

    def get_current_user(self):
        return self.get_secure_cookie('user')

    def isAdmin(self):
        if self.get_secure_cookie('user'):
            return True
        else:
            return False

class AboutHandler(BaseHandler):
    def get(self):
        self.render("about.html",home_title=options.home_title)
class MusicHandler(BaseHandler):
    def get(self):
        self.render("music.html",home_title=options.home_title)
class ProseHandler(BaseHandler):
    def get(self):
        articles,hot=Article.all(self.db,'prose')
        p = Paginator(articles, 6)
        total=p.count
        hottotal=len(hot)
        page_count=p.page_range
        nowpage = int(self.get_argument('page', '1'))
        page = p.page(nowpage)
        isAdmin = self.isAdmin()
        self.render('prose.html',articles=page.object_list,isAdmin=isAdmin,total=total,
                     page_count=page_count,nowpage=nowpage,hots=hot,hottotal=hottotal,home_title=options.home_title)
class ProgramHandler(BaseHandler):
    def get(self):
        nowpage = int(self.get_argument('page', '1'))
        articles,hot=Article.all(self.db,'program')
        #动态为三个sort分页 -------------------------------
        python=[[]]
        js=[[]]
        security=[[]]
        p=0
        j=0
        s=0
        for article in articles:
            for label in article.labels:
                if 'python' in label.detail:
                    if p % 8 == 0 and p != 0:
                        python.append([])
                    python[p/8].append(article)
                    p+=1
                if 'javascript' in label.detail:
                    if j % 8 == 0 and j != 0:
                        js.append([])
                    js[j/8].append(article)
                    j+=1
                if 'security' in label.detail:
                    if s % 8 == 0 and s != 0:
                        security.append([])
                    security[s/8].append(article)
                    s+=1
        if nowpage>len(python):
            pyarticle=python[-1]
        else:
            pyarticle=python[nowpage-1]
        if nowpage>len(js):
            jsarticle=js[-1]
        else:
            jsarticle=js[nowpage-1]
        if nowpage>len(security):
            searticle=security[-1]
        else:
            searticle=security[nowpage-1]
        #动态为三个sort分页 -------------------------------
        p = Paginator(articles,8)
        total=p.count
        hottotal=len(hot)
        page_count=[i+1 for i in range(max(len(python),len(js),len(security)))]
        if nowpage>page_count:
            now=page_count
        else:
            now=nowpage
        page = p.page(nowpage)
        isAdmin = self.isAdmin()
        self.render('program.html',isAdmin=isAdmin,total=total,page_count=page_count,
                     nowpage=now,hots=hot,hottotal=hottotal,python=pyarticle,js=jsarticle,security=searticle,home_title=options.home_title)
class HomeHandler(BaseHandler):
    def get(self):
        nowpage = int(self.get_argument('page', '1'))
        articles,hot=Article.all(self.db)
        p= Paginator(articles, 5)
        total=p.count
        page = p.page(nowpage)
        page_count=p.page_range
        hottotal=len(hot)
        isAdmin = self.isAdmin()
        #如果想加入标签列表，可在模板中加入label_list
        label_list = Label.group(self.db)
        self.render('index.html', articles=page.object_list, label_list=label_list,
                isAdmin=isAdmin,total=total,page_count=page_count,nowpage=nowpage,
                    hots=hot,hottotal=hottotal,new=articles,home_title=options.home_title)

class ArticleHandler(BaseHandler):
    def get(self, id):
        other,hot=Article.all(self.db)
        hottotal=len(hot)
        visit=False
        ip=self.request.headers['X-Real-Ip']
        if ip not in options.ip:
            options.ip.append(ip)
            visit=True
        article,up,dn,relevant = Article.get(self.db, id,visit)
        #包括上下页，和相关文章
        if article is None:
            error = '404: Page Not Found'
            visit=False
            self.render('error.html', error=error, home_title=options.home_title)
        else:
            isAdmin = self.isAdmin()
            visit=False
            self.render('article.html', article=article, isAdmin=isAdmin,
             up=up,dn=dn,relevants=relevant,hots=hot,hottotal=hottotal,home_title=options.home_title)


class PreviewHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        title = self.get_argument('title')
        sort=self.get_argument('sort')
        content_md = self.get_argument('content')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = str(markdown.markdown(content_md, ['codehilite']))
        image=self.get_argument('image')
        article = {}
        article['image']=image
        article['sort']=sort
        article['title'] = title
        article['content_html'] = content_html
        article['labels'] = [{'detail': label[1:-1].strip()} for label in labels]

        data = {}
        data['image']=image
        data['sort']=sort
        data['title'] = title
        data['labels'] = self.get_argument('labels')
        data['content'] = content_md

        self.render('preview.html', article=article, data=data,
                user=options.user, photo=options.photo)

#删除文章，需要权限验证
class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,id):
         Article.delete(self.db, id)
         Article.new(self.db)
         self.redirect('/')

class EditArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        article,up,dn,relevant = Article.get(self.db, id,False)
        if article is None:
            error = '404: Page Not Found'
            self.render('error.html', error=error, home_title=options.home_title)
        else:
            labels = ' '.join(map(lambda item: '[' + item['detail'] + ']', article['labels']))
            options.oldimage=str(article.title)
            #尝试更改封面，先保存旧名称
            self.render('editArticle.html', article=article, labels=labels)


class UpdateArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, id):
        title = self.get_argument('title')
        image=self.get_argument('image')
        content_md = self.get_argument('content')
        sort = self.get_argument('sort')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = str(markdown.markdown(content_md, ['codehilite']))
        
        try:
            Article.update(self.db, id, title, content_md.replace('\"','\''), content_html.replace('\"','\''),sort,image)
            Label.deleteAll(self.db, id)
            for label in labels:
                detail = label[1:-1].strip()
                Label.create(self.db, id, detail)
            Article.new(self.db)
            self.redirect('/article/' + id, permanent=True)
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)

#创建文章
class CreateArticleHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('createArticle.html')

    @tornado.web.authenticated
    def post(self):
        title = self.get_argument('title')
        content_md = self.get_argument('content')
        sort = self.get_argument('sort')
        image=self.get_argument('image')
        pattern = r'\[[^\[\]]+\]'
        labels = re.findall(pattern, self.get_argument('labels'))
        content_html = str(markdown.markdown(content_md, ['codehilite']))
        strinfo = re.compile('%')
        new_html = strinfo.sub('%%',content_html)
        new_md = strinfo.sub('%%',content_md)
        article_id = Article.create(self.db, title, new_md.replace('\"','\''), new_html.replace('\"','\''),sort,image)   
        for label in labels:
            detail = label[1:-1].strip()
            Label.create(self.db, article_id, detail)
        Article.new(self.db)
        try:
            self.redirect('/', permanent=True)
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)

#按照标签搜索
class SearchHandler(BaseHandler):
    def get(self):
        key = self.get_argument('key', '').strip()
        nowpage = int(self.get_argument('page', '1'))
        if len(key) == 0:
            results,hot = Article.all(self.db)
            
        else:
            results,hot= Search.all(self.db, key)
        p = Paginator(results, 5)
        total=p.count
        page = p.page(nowpage)
        page_count=p.page_range

        hottotal=len(hot)

        isAdmin = self.isAdmin()
        label_list = Label.group(self.db)

        self.render('search.html', articles=page.object_list, label_list=label_list,
                isAdmin=isAdmin,total=total,page_count=page_count,nowpage=nowpage,hots=hot,
                       hottotal=hottotal,key=key,new=results,home_title=options.home_title)

class LoginHandler(BaseHandler):
    def get(self):
        next = self.get_argument('next', '/')
        self.render('login.html', next=next)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.redirect('/', permanent=True)

#管理员验证--------------------------------------------------------------------------
class AuthHandler(BaseHandler):
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        try:
            if self.validate(username) is None:
                raise

            if Auth.authenticate(self.db, username, password):
                self.set_secure_cookie("user", "admin", expires_days=1)
                self.redirect(self.get_argument('next', '/'), permanent=True)
            else:
                error = "Authentication failure"
                self.render('error.html', error=error, home_title=options.home_title)
        except:
            error = "The user not exists"
            self.render('error.html', error=error, home_title=options.home_title)

    def validate(self, username):
        regex = re.compile(r'^[\w\d]+$')
        return regex.match(username)
#管理员验证--------------------------------------------------------------------------

def clean():  
    options.ip=[]  

def main():
    config = ConfigParser.ConfigParser()
    config.read('blog.cfg')
    mysql = dict(config.items('mysql'))
    blog = dict(config.items('blog'))
    define("ip",default=[], type=list)
    define("port", default=int(blog['port']), type=int)
    define("mysql_host", default="127.0.0.1:3306")
    define("mysql_database", default=mysql['database'])
    define("mysql_user", default=mysql['user'])
    define("mysql_password", default=mysql['password'])
    define("blog_hostname", default=blog['hostname'])
    define("user", default=blog['user'])
    define("home_title", default=blog['home_title'])
    define("photo", default=blog['photo'])
    define("oldimage", default='')
    define("timer_interval", default=int(60*60*24))

    t=Timer(options.timer_interval,clean)  
    t.start()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
