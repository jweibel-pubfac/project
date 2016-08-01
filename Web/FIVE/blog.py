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

from model import Student, Auth
from component import Paginator
from tornado.options import define, options
import sys
from threading import Timer

#系统默认编码为ascii，此处设置默认为utf-8
reload(sys)
sys.setdefaultencoding( "utf-8" )



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/edit/(\d+)', EditHandler),
            (r'/delete/(\d+)', DeleteHandler),
            (r'/update/(\d+)', UpdateHandler),
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

#删除文章，需要权限验证
class DeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,id):
         Student.delete(self.db, id)
         Student.new(self.db)
         self.redirect('/')

#编辑信息
class EditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, id):
        student = Student.get(self.db, id)
        if student is None:
            error = '404: Page Not Found'
            self.render('error.html', error=error, home_title=options.home_title)
        else:
            self.render('edit.html', student=student)

#更新信息
class UpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, id):
        name = self.get_argument('name')
        major=self.get_argument('major')
        sort = self.get_argument('sort')
        teacher=self.get_argument('teacher')
        class_hour=self.get_argument('class_hour')
        telephone=self.get_argument('telephone')
        qq=self.get_argument('qq')

        try:
            Student.update(self.db, name, major, sort,teacher,class_hour,telephone,qq)
            Student.new(self.db)
            self.redirect('/', permanent=True)
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)

#首页
class HomeHandler(BaseHandler):
    def get(self):
        isAdmin = self.isAdmin()
        students=Student.all(self.db)
        self.render('index.html',students=students,isAdmin = isAdmin)

    def post(self):
        name = self.get_argument('name')
        major=self.get_argument('major')
        sort = self.get_argument('sort')
        teacher=self.get_argument('teacher')
        class_hour=self.get_argument('class_hour')
        telephone=self.get_argument('telephone')
        qq=self.get_argument('qq')
        Student.create(self.db, name, major, sort,teacher,class_hour,telephone,qq)
        Student.new(self.db)
        try:
            self.render('success.html')
        except:
            error = "The post data invalid"
            self.render('error.html', error=error, home_title=options.home_title)

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


    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
