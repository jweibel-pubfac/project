#!/usr/bin/python
#coding=utf-8

#数据库使用说明---------------------------------------------------------------------------------------------
#使用mysql数据库
#建立database:todo
#建立表格:todo
#列：id(int) title(txt) finished(int,默认值为0) post_data(时间戳)
#create database todo;
#use todo;
#create table users(id int(2) not null primary key auto_increment,title txt,finished int(2) default 0,post_data text)default charset=utf8;
#数据库使用说明---------------------------------------------------------------------------------------------
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
define("mysql_database", default="todo", help="db name")
define("mysql_user", default="root", help="db user")
define("mysql_password", default="", help="db password")
#设置数据库连接参数------------------------------------------------------
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", IndexHandler), 
			(r"/todo/new", NewHandler),
			(r"/todo/(\d+)/edit", EditHandler),
			(r"/todo/(\d+)/delete", DeleteHandler),
			(r"/todo/(\d+)/finish", FinishHandler),
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

#连接数据库，显示已有title-----------------------------------------------------------
class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		title = "todo"
		db = self.application.db
		todos = db.query("select * from todo order by post_date desc")
                print(todos)
		self.render("index.html", todos=todos, title=title)
#连接数据库，显示已有title-----------------------------------------------------------

#设置新数据-------------------------------------------------------------------------------------------
class NewHandler(tornado.web.RequestHandler):
	def post(self):
		title = self.get_argument("title")
		if not title:
			return None
		db = self.application.db
                #注意插入变量的语句
		db.execute('insert into todo (title, post_date) values("%s", UTC_TIMESTAMP())'%title)
		self.redirect("/")
                #重定向
#设置新数据-------------------------------------------------------------------------------------------

#更新数据库-------------------------------------------------------------------------------------------
class EditHandler(tornado.web.RequestHandler):
	def get(self, id):
		db = self.application.db
		todos = db.query("select * from todo where id=%s", int(id))
		todo = todos[0]
		if not todo:
			return None
		return self.render("edit.html", todo=todo)

	def post(self, id):
		db = self.application.db
		todos = db.query("select * from todo where id=%s", int(id))
		todo = todos[0]
		if not todo:
			return None
		title = self.get_argument("title")
		db.execute("update todo set title=%s, post_date=UTC_TIMESTAMP() where id=%s", \
			title, int(id))
		self.redirect("/")
#更新数据库-------------------------------------------------------------------------------------------

#删除数据-----------------------------------------------------------------------
class DeleteHandler(tornado.web.RequestHandler):
	def get(self, id):
		db = self.application.db
		todo = db.query("select * from todo where id=%s", int(id))
		if not todo:
			return None
		db.execute("delete from todo where id=%s", int(id))
		self.redirect("/")
#删除数据-----------------------------------------------------------------------

#设置finished值，表示完成与否---------------------------------------------------------
class FinishHandler(tornado.web.RequestHandler):
	def get(self, id):
		db = self.application.db
		todo = db.query("select * from todo where id=%s", int(id))
		if not todo:
			return None
		status = self.get_argument("status", "yes")
		if status == "yes":
			finished = 1
		elif status == "no":
			finished = 0
		else:
			return None
		db.execute("update todo set finished=%s where id=%s", finished, id)
		self.redirect("/")
#设置finished值，表示完成与否---------------------------------------------------------

#使用参数--setup，自动完成数据库设置----------------------------------------------------------------------
def dbSetup():
	conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="")
	try:
#		conn = MySQLdb.connect(host="127.0.0.1",user="root",passwd="",db="test")
		cur = conn.cursor()
		cur.execute("create database todo")
		time.sleep(2)
		cur.execute("use todo")
		cur.execute("create table todo(id int(2) not null primary key auto_increment,finished int default 0,title text,post_data text)default charset=utf8;")
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

	parser = argparse.ArgumentParser(description='Run the Flask todo app')
	parser.add_argument('--setup', dest='run_setup', action='store_true')

	args = parser.parse_args()
	if args.run_setup:
		dbSetup()
	else:
	    main()
