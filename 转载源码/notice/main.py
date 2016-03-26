#!/usr/bin/python

print 'Content-type:text/html\n'
print
#import cgitb:cgitb.enable()
#数据库创建表格
#CREATE TABLE messages(
#    id INT NOT NULL AUTO_INCREMENT,
#    subject VARCHAR(100) NOT NULL,
#    reply_to INT,
#    text MEDIUMTEXT NOT NULL,
#    PRIMARY KEY(id))


import MySQLdb
#连接数据库
conn = MySQLdb.connect(db='usernet',host='127.0.0.1',user='root',passwd='root')

curs = conn.cursor()
#输出页面开头
print '''
<html>
  <head>
    <title>The UserNet</title>
  </head>
  <body>
    <h1>The UserNet</h1>
'''

sql = 'SELECT * FROM message'
curs.execute(sql)
#查询数据库中所有消息
rows = curs.fetchall()
#返回包含所有消息的一个list
toplevel = []
#所有主题贴顶层
children = {}
#分别定义回复贴层次

for row in rows:
#迭代每一条消息
        #reply_to数据列，确定回复贴还是主题贴
        parent_id = row[2]
        if parent_id is None:
                toplevel.append(row)
                #如果无数据，则加入主题贴list
        else:
                children.setdefault(parent_id,[]).append(row)
                #否则加入dict，key为父贴，值为整个数据
        #定义迭代方法，依次呈现主题贴，以及其下回复贴
        def format(row):
                print '<p><a href="view.cgi?id=%i">%s<a>' % (row[0],row[1])
                #打印出主题贴id，主题
                try:
                        kids = children[row[0]]
                        #尝试根据字典找出回复贴
                except KeyError:
                        pass
                else:
                        print '<blockquote>'
                        #迭代，打印出主题下所有回复贴
                        for kid in kids:
                                format(kid)

                        print '</blockquote>'

        print '<p>'

        for row in toplevel:
                format(row)

print '''
</p>
<hr/>
<p><a href="edit.cgi">Post Message</a></p>
</body>
</html>
'''
