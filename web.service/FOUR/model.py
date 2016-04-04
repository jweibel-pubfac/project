#!/usr/bin/env python
#-*- coding:utf-8 -*-
import hashlib
import time
import os.path
import os

class Article(object):
    @classmethod
    def all(cls, db,sort=None):
    #去除全部文章，可加入分类参数
        if sort:
            hot=db.query("SELECT * FROM article where sort=%s ORDER BY visit DESC ",sort)
            articles = db.query("SELECT * FROM article where sort=%s ORDER BY time DESC",sort)
            for article in articles:
                article['labels'] = Label.all(db, article.id)
            return articles,hot
        else:
            hot=db.query(" SELECT * FROM article ORDER BY visit DESC")
            articles = db.query("SELECT * FROM article ORDER BY time DESC")
            for article in articles:
                article['labels'] = Label.all(db, article.id)
            return articles,hot     

    @classmethod
    def get(cls, db, id):
        #获得一篇文章，包括相关，上下页
        db.execute("UPDATE article set visit=visit+1 WHERE id=%s",id)
        article = db.get('SELECT * FROM article WHERE id = %s', id)
        try:
            relevant=db.query('SELECT * FROM article WHERE (sort = %s and id<> %s )',article.sort,article.id)
        except:
            relevant=None
        try:
            up=db.get('SELECT * FROM article WHERE id = %s',str(int(id)-1))
        except:
            up=None
        try:
            dn=db.get('SELECT * FROM article WHERE id = %s', str(int(id)+1))
        except:
            dn=None
        if article is None:
            return article,up,dn,relevant
        else:
            article['labels'] = Label.all(db, article.id)
            return article,up,dn,relevant

    @classmethod
    def create(cls, db, title, content_md, content_html,sort):
        return db.execute('insert into article (title, content_md,content_html,sort,time) \
               values("%s", "%s", "%s","%s",CURRENT_TIMESTAMP())'%(title, content_md, content_html,sort))
    @classmethod
    def update(cls, db, id, title, content_md, content_html,sort):
        db.execute("UPDATE article set title=%s, content_md=%s, \
                content_html=%s,sort=%s WHERE id=%s",title, content_md, content_html,sort,id)

    @classmethod
    def totalNumber(cls, db):
        return db.execute_rowcount('SELECT * FROM article')
    @classmethod
    def delete(cls, db,id):
        articles=db.query("SELECT * FROM article where id=%s",id)
        filepath = os.path.join('static/article',articles[0].title)
        if os.path.isfile(filepath):
            os.remove(filepath)
        db.execute('DELETE FROM article WHERE id=%s',id)
        db.execute('DELETE FROM label WHERE article_id=%s'%id)
    @classmethod
    def new(cls, db):
        #强迫症患者福音，自动排列数据库id，保证永远从1开始不间断
        sum = 0
        articles=db.query("SELECT * FROM article")
        for article in articles:
            sum=sum+1
            if(article.id != sum ):  
                db.execute("UPDATE article SET id=%s WHERE id=%s",sum,article.id)   
                db.execute("UPDATE label SET article_id=%s WHERE article_id=%s",sum,article.id) 
        labels=db.query("SELECT * FROM label")
        sum=0
        for label in labels:
            sum=sum+1
            if(label.id != sum ):  
                db.execute("UPDATE label SET id=%s WHERE id=%s",sum,label.id)   
        

       

#标签查询
class Label(object):
    @classmethod
    def all(cls, db, article_id):
        return db.query('SELECT detail FROM label \
                WHERE article_id = %s', article_id)
    @classmethod
    def create(cls, db, article_id, detail):
        db.execute('INSERT INTO label (article_id, detail) \
                VALUES ("%s", "%s")'%(article_id, detail))

    @classmethod
    def deleteAll(cls, db, article_id):
        db.execute('DELETE FROM label WHERE article_id=%s'%article_id)

    @classmethod
    def group(cls, db):
        return db.query('SELECT detail, count(*) AS number \
                FROM label GROUP BY detail ORDER BY number DESC')

#管理员验证
class Auth(object):
    @classmethod
    def authenticate(cls, db, username, password):
        hashPassword = db.get('SELECT password FROM auth \
                WHERE username = %s', username)['password']
        return hashlib.md5(password).hexdigest() == hashPassword

#标签搜索
class Search(object):
    @classmethod
    def all(cls, db, key):
        results = db.query('SELECT a.id, a.title, a.content_md, a.content_html, a.time ,a.visit,a.sort\
                FROM article a, label l \
                WHERE a.id = l.article_id AND l.detail = %s \
                ORDER BY time DESC', key)
        hot = db.query('SELECT a.id, a.title, a.content_md, a.content_html, a.time ,a.visit,a.sort\
                FROM article a, label l \
                WHERE a.id = l.article_id AND l.detail = %s \
                ORDER BY visit DESC', key)
        for result in results:
            result['labels'] = Label.all(db, result.id)
        return results,hot
