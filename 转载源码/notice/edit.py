#!/usr/bin/python

print 'Content-type:text/html\n'

import cgitb;cgitb.enable()

import MySQLdb
conn = MySQLdb.connect(db='usernet',host='127.0.0.1',user='root',passwd='root')
curs = conn.cursor()

import cgi,sys
form = cgi.FieldStorage()
reply_to = form.getvalue('reply_to')
#获取链接传输的参数
#打印编辑页面
print '''
<html>
  <head>
    <title>Compose Message</title>
  </head>
  <body>
    <h1>Compose Message</h1>

    <form action='save.cgi' method='POST'>
    '''

subject = ''
#如果reply_to不是None，则为回复
if reply_to is not None:
        print '<input type="hidden" name="reply_to" value="%s"/>' % reply_to
        #查找相关数据项
        curs.execute('SELECT subject FROM message WHERE id = %s' % reply_to)
        subject = curs.fetchone()[0]
        #如果主题没有Re，则回复的该贴不是回复贴，定义subject
        if not subject.startswith('Re: '):
                subject = 'Re:  ' + subject
print '''
    <b>Subject:</b><br/>
    <input type='text' size='40' name='subject' value='%s' /><br/>
    <b>Sender:</b><br/>
    <input type='text' size='40' name='sender' /><br/>
    <b>Message:</b><br/>
    <textarea name='text' cols='40' rows='20'></textarea><br/>
    <input type='submit' value='Save'/>
    </form>
    <hr/>
    <a href='main.cgi'>back to the main page</a>
    </body>
    </html>
    ''' % subject

