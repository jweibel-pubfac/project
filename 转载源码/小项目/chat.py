from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore
#asynchat中的async_chat和asyncore中的dispatcher以及asyncore本身
#前面的类是用来处理客户端同服务器的每一次会话，后面的类主要是用来提供socket连接服务
#并且将每一个socket连接都托管给前者（async_chat）来处理。
#定义了基本房间功能，包括登出、登录，以及命令处理
#不同房间有不同方法，loginroom只有登录方法，登录成功进入chatroom，可以调用发送消息方法
#总服务器接受socket请求，然后发送给async_chat，处理没每一个socket的数据

PORT = 5005
NAME = 'TestChat'

class EndSession(Exception):pass
#每个房间的处理类---------------------------------------
class CommandHandler:
        
        def unknown(self, session, cmd):
                session.push('Unknown command: %s\r\n' % cmd)
        #接受完数据后，调用此方法处理---------------------
        def handle(self, session, line):
                if not line.strip(): return
                #如果没有数据则返回

                parts = line.split(' ',1)
                #将数据字符串拆分
                cmd = parts[0]
                #得到第一个命令
                try: line = parts[1].strip()
                #如果有第二个数据
                except IndexError: line = ''
                #是否存在方法
                meth = getattr(self, 'do_'+cmd, None)
                #获得方法，没有默认为None
                try:
                        #尝试使用方法，传递ChatSession类以及数据
                        meth(session, line)
                        #首次使用一般为do_login方法
                except TypeError:
                        #发送数据Unknown command
                        self.unknown(session,cmd)
        #接受完数据后，调用此方法处理---------------------
#每个房间的处理类---------------------------------------
class Room(CommandHandler):
        #这是每个房间的基本功能，各继承类有各自的方法---------
        def __init__(self, server):
                self.server = server
                self.sessions = []

        def add(self, session):
                self.sessions.append(session)

        def remove(self, session):
                self.sessions.remove(session)

        def broadcast(self, line):
                for session in self.sessions:
                        session.push(line)
                        #封装的ChatSession类，调用push，向连接的客户端发送消息
        #离开房间，raise EndSession错误类，在ChatSession接收
        def do_logout(self, session, line):
                raise EndSession
        #这是每个房间的基本功能，各继承类有各自的方法---------
class LoginRoom(Room):

        def add(self,session):
                Room.add(self,session)

                self.broadcast('Welcome to %s\r\n' % self.server.name)

        def unknown(self, session, cmd):
                session.push('Please log in \nUse "login"\r\n')
        #首次登录房间，line为用户名
        def do_login(self, session, line):
                name = line.strip()

                if not name:
                        session.push('Please enter a name\r\n')
                #如果名字在用户列表中
                elif name in self.server.users:
                        session.push('The name "%s" is taken.\r\n' % name)
                        sessoin.push('Please try again.\r\n')
                else:
                        #为ChatSession定义名字
                        #登录到self.server.main_room，即ChatRoom()中
                        session.name = name
                        session.enter(self.server.main_room)

class ChatRoom(Room):
        #登录成功，执行add方法，广播通知
        def add(self, session):
                self.broadcast(session.name + ' has entered the room.\r\n')
                self.server.users[session.name] = session
                #将用户名与socket对应
                Room.add(self, session)
                #加入self.sessionslist中
        #离开房间
        def remove(self, session):
                Room.remove(self, session)

                self.broadcast(session.name + ' has left the room.\r\n')

        def do_say(self, session, line):
                self.broadcast(session.name + ': ' + line + '\r\n')
        #查看房间中的人
        def do_look(self, session, line):
                session.push('The following are in this room:\r\n')
                for other in self.sessions:
                        session.push(other.name + '\r\n')
        #查看注册的名字
        def do_who(self, session, line):
                session.push('The following are logged in:\r\n')
                for name in self.server.users:
                        session.push(name + '\r\n')

class LogoutRoom(Room):
        def add(self, session):
                try: del self.server.users[session.name]
                except KeyError: pass
                #删除用户名对应的socket，如果在loginroom，则发生KeyError

#接受连接的socket，接受数据并处理----------------------------------
class ChatSession(async_chat):

        def __init__(self, server, sock):
                async_chat.__init__(self,sock)
                #继承async_chat，接受socket实例化
                self.server = server
                #确定主服务器
                self.set_terminator('\r\n')
                #当数据出现\r\n，调用found_terminator函数
                self.data = []
                self.name = None

                self.enter(LoginRoom(server))
                

        def enter(self, room):

                try: 
                        cur = self.room
                        #首次加入LoginRoom，无self.room属性，执行出错，不执行else部分
                        #登录成功后，调用无误，执行else部分，将该类从LoginRoom中移除，加入ChatRoom
                except AttributeError: 
                        pass
                else: cur.remove(self)
                self.room = room
                #self.room = LoginRoom(server)，继承room类：def __init__(self, server):self.server = server
                #由此确定其所在服务器
                room.add(self)
                #添加至room类self.sessions列表，并广播出去

        def collect_incoming_data(self, data):
                self.data.append(data)
                #接收客户端发送的消息
        #发现\r\n结束符号，调用此方法
        def found_terminator(self):
                line = ''.join(self.data)
                #由''相隔的字符串
                self.data = []
                try: self.room.handle(self, line)
                #调用继承类CommandHandler方法处理数据
                except EndSession:
                        #调用退出函数
                        self.handle_close()

        def handle_close(self):
                #关闭此类
                async_chat.handle_close(self)
                self.enter(LogoutRoom(self.server))
                #加入登出房间，处理最后一些数据
#接受连接的socket，接受数据并处理----------------------------------

#聊天主服务器-----------------------------------------------------------------
class ChatServer(dispatcher):
                #继承dispatcher类，用于监听客户端发来的连接请求
        def __init__(self, port, name):
                dispatcher.__init__(self)
                self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
                self.bind(('',port))
                self.listen(5)
                #创建socket监听
                self.name = name
                self.users = {}
                self.main_room = ChatRoom(self)
                #确定主聊天室
        #处理发来的客户端请求
        def handle_accept(self):
                conn, addr = self.accept()
                ChatSession(self,conn)
                #接受socket，并将socket交给ChatSession处理
#聊天主服务器-----------------------------------------------------------------
if __name__ == '__main__':
        s = ChatServer(PORT, NAME)
        try: asyncore.loop()
        except KeyboardInterrupt: print
