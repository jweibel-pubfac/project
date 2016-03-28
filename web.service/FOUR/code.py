#!/usr/bin/python
#coding=utf-8
import time
import os.path
import torndb
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import argparse
import MySQLdb
from tornado.options import define, options

#设置数据库连接参数------------------------------------------------------
define("port", default=8888, help="run port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="db host")
define("mysql_database", default="blogs", help="db name")
define("mysql_user", default="root", help="db user")
define("mysql_password", default="", help="db password")
#设置数据库连接参数------------------------------------------------------
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", IndexHandler), 
                        (r"/about", AboutHandler),
                        (r"/music", MusicHandler),
                        (r"/newlist", NewlistHandler),
                        (r"/program", ProgramHandler),
                        (r"/view", ViewHandler),
			(r"/blog/new", NewHandler),
			(r"/blog/edit", EditHandler),
			(r"/blog/delete", DeleteHandler),
		]
		settings = dict(
			template_path = TEMPLATE_PATH, 
			static_path = STATIC_PATH, 
			debug = True
		)
		tornado.web.Application.__init__(self, handlers, **settings)
		self.db = torndb.Connection(
			host = options.mysql_host, 
			database = options.mysql_database, 
			user = options.mysql_user, 
			password = options.mysql_password
		)

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		db = self.application.db
		myblog = db.query("select * from blogs")
		self.render("index.html",blogs=myblog)
class AboutHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("about.html")
class ViewHandler(tornado.web.RequestHandler):
	def get(self):
                db = self.application.db
                id = self.get_argument('id')
		blog = db.query("select * from blogs where id=%s",int(id))
		self.render("article.html",article=blog)
class MusicHandler(tornado.web.RequestHandler):
	def get(self):
                db = self.application.db
		blog = db.query("select * from blogs where class='music'")
		self.render("music.html",article=blog)
class NewlistHandler(tornado.web.RequestHandler):
	def get(self):
                db = self.application.db
		blog = db.query("select * from blogs where class='prose'")
		self.render("prose.html",article=blog)
class ProgramHandler(tornado.web.RequestHandler):
	def get(self):
                db = self.application.db
		blog = db.query("select * from blogs where class='program'")
		self.render("program.html",article=blog)

class NewHandler(tornado.web.RequestHandler):
	def post(self,):
		title = self.get_argument("title")
		if not title:
			return None
		db = self.application.db
		db.execute('insert into blogs (title, post_date) values("%s", UTC_TIMESTAMP())'%title)
		self.redirect("/")

class EditHandler(tornado.web.RequestHandler):
	def get(self, id):
		db = self.application.db
		blogss = db.query("select * from blogs where id=%s", int(id))
		blogs = blogss[0]
		if not blogs:
			return None
		return self.render("edit.html", blogs=blogs)

	def post(self, id):
		db = self.application.db
		blogss = db.query("select * from blogs where id=%s", int(id))
		blogs = blogss[0]
		if not blogs:
			return None
		title = self.get_argument("title")
		db.execute("update blogs set title=%s, post_date=UTC_TIMESTAMP() where id=%s", \
			title, int(id))
		self.redirect("/")
#更新数据库-------------------------------------------------------------------------------------------

#删除数据-----------------------------------------------------------------------
class DeleteHandler(tornado.web.RequestHandler):
	def get(self, id):
		db = self.application.db
		blogs = db.query("select * from blogs where id=%s", int(id))
		if not blogs:
			return None
		db.execute("delete from blogs where id=%s", int(id))
		self.redirect("/")
#删除数据-----------------------------------------------------------------------



#使用参数--setup，自动完成数据库设置----------------------------------------------------------------------
def dbSetup():
	conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="")
	try:
#		conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="",db="test")
		cur = conn.cursor()
		cur.execute("create database blogs")
		time.sleep(2)
		cur.execute("use blogs")
		cur.execute("create table blogs(id int(2) not null primary key auto_increment,class text,title text,article text,post_date text)default charset=utf8;")
		print 'Database setup completed. Now run the app without --setup.'
	except:
		print 'App database already exists. Run the app without --setup.'
	finally:
		conn.close()
#使用参数--setup，自动完成数据库设置----------------------------------------------------------------------

def main():
	tornado.options.parse_command_line()
	app = tornado.httpserver.HTTPServer(Application())
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Run the Flask blogs app')
	parser.add_argument('--setup', dest='run_setup', action='store_true')

	args = parser.parse_args()
	if args.run_setup:
		dbSetup()
	else:
	    main()
