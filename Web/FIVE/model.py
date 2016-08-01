#!/usr/bin/env python
#-*- coding:utf-8 -*-
import hashlib
import time
import os.path
import os

class Student(object):
    @classmethod
    def all(cls, db):
    #去除全部文章，可加入分类参数
        students = db.query("SELECT * FROM student")
        return students
    @classmethod
    def get(cls, db, id):
        #获得一篇文章，包括相关，上下页
        student = db.get('SELECT * FROM student WHERE id = %s', id)
        return student


    @classmethod
    def create(cls, db, name, major, sort,teacher,class_hour,telephone,qq):
        return db.execute('insert into student (name,major,sort,teacher,class_hour,telephone,qq,time) \
               values("%s", "%s", "%s","%s","%s","%s","%s",CURRENT_TIMESTAMP())'%(name, major, sort,teacher,class_hour,telephone,qq))
    @classmethod
    def update(cls, db, id, name, major, sort,teacher,class_hour,telephone,qq):
        db.execute("UPDATE student set name=%s, major=%s, \
                sort=%s,teacher=%s,class_hour=%s,telephone=%s,qq=%s WHERE id=%s",name, major, sort,teacher,class_hour,telephone,qq,id)

    @classmethod
    def totalNumber(cls, db):
        return db.execute_rowcount('SELECT * FROM student')
    @classmethod
    def delete(cls, db,id):
        students=db.query("SELECT * FROM student where id=%s",id)
        db.execute('DELETE FROM student WHERE id=%s',id)
    @classmethod
    def new(cls, db):
        #强迫症患者福音，自动排列数据库id，保证永远从1开始不间断
        sum = 0
        students=db.query("SELECT * FROM student")
        for student in students:
            sum=sum+1
            if(student.id != sum ):  
                db.execute("UPDATE student SET id=%s WHERE id=%s",sum,student.id)

#管理员验证
class Auth(object):
    @classmethod
    def authenticate(cls, db, username, password):
        hashPassword = db.get('SELECT password FROM admin \
                WHERE username = %s', username)['password']
        return hashlib.md5(password).hexdigest() == hashPassword
