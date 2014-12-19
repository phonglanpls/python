#!/usr/bin/python
# -*- coding: UTF-8 -*-
import select
import socket
import re
import urllib2
import SocketServer
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def target_client_exchange(client, _target):
    socs = [client, _target]
    finished = False
    while not finished:
        receive, _, error = select.select(socs, [], socs, 3)
        if error:
            break
        if len(receive) == 0:
            break
        if receive:
            for in_ in receive:
                data = in_.recv(9999999)
                print data
                if len(data) == 0:
                    finished = True
                    break
                if in_ is client:
                    out = _target
                else:
                    out = client
                if data:
                    out.send(data)
                    print data


def handler_https(first_line, header, sock, source_data):
    # 建立socket用以连接URL指定的机器
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # soc.settimeout(4)
    # 尝试连接
    try:
        soc.connect((str(socket.gethostbyname(first_line[2])), int(first_line[4])))
    except socket.error, arg:
        sock.sendall("/1.1" + str(arg[0]) + " Fail\r\n\r\n")
        sock.close()
        soc.close()
    else:  # 若连接成功
        sock.sendall('HTTP/1.1 200 Connection established\r\n\r\n')
        # 数据缓冲区
        # 读取浏览器给出的消息
        try:
            target_client_exchange(sock, soc)
        except:
            sock.close()
            soc.close()


def handler(data, sock):
    data = data.strip()
    if not data:
        return None

    # 按行分隔header
    header = data.split('\r\n')

    '''
GET http://ku6cdn.com/crossdomain.xml HTTP/1.1
CONNECT www.google.com.hk:443 HTTP/1.1
Host: www.google.com.hk
Proxy-Connection: keep-alive
User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36
    '''

    # 对header首行的处理
    pattern = r'^(GET|POST|HEAD|PUT|DELETE|TRACE|CONNECT|OPTIONS)\s' \
              r'(http://|https://)?([^/:]+)(:(\d{0,5}))?([^\s]*)\s([\s\S]*)'
    regex = re.compile(pattern)
    first_line = regex.findall(header[0])[0]
    del header[0]

    if first_line[0] == 'CONNECT':  # HTTPS
        return handler_https(first_line, header, sock, data)

    urllib2_header = {}
    for line in header:
        row = line.split(':')
        if not row[0] == 'Accept-Encoding':  # 暂时不支持 gzip
            urllib2_header[row[0]] = row[1]

    print first_line
    print first_line[1] + first_line[2] + first_line[5]

    req = urllib2.Request(first_line[1] + first_line[2] + first_line[5], None, urllib2_header)
    resp = urllib2.urlopen(req, None, 2)
    html = resp.read()
    soc.sendall(html)


if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 1234))
    server.listen(5)

    while True:
        soc, address = server.accept()
        handler(soc.recv(99999999), soc)


# import select
# import socket
# import Queue
#
# # create a socket
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setblocking(False)
# # set option reused
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# server_address = ('localhost', 1234)
# server.bind(server_address)
#
# server.listen(10)
#
# # sockets from which we except to read
# inputs = [server]
#
# # sockets from which we expect to write
# outputs = []
#
# # Outgoing message queues (socket:Queue)
# message_queues = {}
#
# # A optional parameter for select is TIMEOUT
#
# while inputs:
# readable, writable, exceptional = select.select(inputs, outputs, inputs)
#
# # When timeout reached , select return three empty lists
# if not (readable or writable or exceptional):
# break
#
# for s in readable:
# if s is server:
# # A "readable" socket is ready to accept a connection
# connection, client_address = s.accept()
# connection.setblocking(0)
# inputs.append(connection)
# message_queues[connection] = Queue.Queue()
# else:
# last_ws = s
# # print 11111111
# # print s
# # print 111111111
# data = ''
# try:
# while True:
# str_data = s.recv(2048)
# if not len(str_data):
# break
#                     data += str_data
#             except:
#                 pass
#
#             if data:
#                 message_queues[s].put(data)
#                 # Add output channel for response
#                 if s not in outputs:
#                     outputs.append(s)
#             else:
#                 # Interpret empty result as closed connection
#                 if s in outputs:
#                     outputs.remove(s)
#                 inputs.remove(s)
#                 s.close()
#                 # remove message queue
#                 del message_queues[s]
#     for s in writable:
#         try:
#             next_msg = message_queues[s].get_nowait()
#         except:
#             if s in outputs:
#                 outputs.remove(s)
#         else:
#             try:
#                 # print len(outputs)
#                 # print len(inputs)
#                 # print len(message_queues)
#                 # s.send(next_msg)
#                 s.send(handler(next_msg, s, last_ws))
#                 s.close()
#                 inputs.remove(s)
#                 outputs.remove(s)
#                 del message_queues[s]
#             except:
#                 pass
#
#     for s in exceptional:
#         print exceptional
#         # stop listening for input on the connection
#         inputs.remove(s)
#         if s in outputs:
#             outputs.remove(s)
#         s.close()
#         # Remove message queue
#         del message_queues[s]
#

# if 0:
#
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setblocking(False)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
# # server_address = (socket.gethostbyname(socket.gethostname()), 1234)
# server_address = ('127.0.0.1', 1234)
# server.bind(server_address)
#
# server.listen(10)
#
# inputs = [server]
#
# outputs = []
#
# message = []
#
#     while inputs:
#         readable, writable, exceptional = select.select(inputs, outputs, inputs)
#
#         if not (readable or writable or exceptional):
#             break
#
#         for s in readable:
#             if s is server:
#                 connection, client_address = s.accept()
#                 connection.setblocking(0)
#                 inputs.append(connection)
#             else:
#                 data = ''
#                 try:
#                     while True:
#                         str_data = s.recv(1024)
#                         if not len(str_data):
#                             break
#                         data += str_data
#                 except:
#                     pass
#
#                 if data:
#                     message[client_address[1]] = data
#                     if s not in outputs:
#                         outputs.append(s)
#                 else:
#                     if s in outputs:
#                         outputs.remove(s)
#                     inputs.remove(s)
#                     s.close()
#
#         for s in writable:
#             print s
#             try:
#                 print message[client_address[1]]
#                 # str(handler(data))
#                 s.send('11111')
#                 s.close()
#                 inputs.remove(s)
#                 outputs.remove(s)
#             except:
#                 pass
#
#         for s in exceptional:
#             # print " exception condition on ", s.getpeername()
#             inputs.remove(s)
#             if s in outputs:
#                 outputs.remove(s)
#             s.close()




# for line in header:
# if line.startswith('Accept-Encoding'):
# del header[header.index(line)]
#
# print 1
# head_str = ('\r\n'.join(header)) + '\r\n\r\n '
# # print head_str
# ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print 2
# ss.connect((first_line[2], 80))
# print 3
# ss.send(head_str)
# print 4
# # html = ss.recv(100000040)
# html = ''
# while True:
# snippet = ''
# try:
# snippet = ss.recv(100000040)
#
# except:
# pass
# html += snippet
# if not len(snippet):
# break
# print 5
# ss.close()
# print 6
# # print html
# print first_line
# return html  # return str(first_line) + '\r\n' + host + '\r\n' + ('\r\n'.join(header))


# streamStr = StringIO.StringIO(gzipStr)
# gzipFIle = gzip.GzipFile(fileobj=streamStr)
# html = gzipFIle.read()

# i = re.compile(self.crawlReg)
# all = i.findall(html)  # return ( 0 = url , 1 = title )
# print all
# return all
# except:
# return ()
#
# class MyTCPHandler(SocketServer.BaseRequestHandler):
# """
# The RequestHandler class for our server.
#
# It is instantiated once per connection to the server, and must
# override the handle() method to implement communication to the
# client.
# """
#
# def handle(self):
# # self.request is the TCP socket connected to the client
# # self.request.setBlocking(0)
# self.data = ''
# time.sleep(0.1)
# while True:
# # self.request.setBlocking(0)
# str_data = self.request.recv(1).strip()
# if not len(str_data):
# break
# self.data += str_data
#
# print "{} wrote:".format(self.client_address[0])
# print self.data
# # just send back the same data, but upper-cased
# self.request.sendall(self.data.upper())
#
#
# if __name__ == "__main__":
# HOST, PORT = "localhost", 1234
#
# # Create the server, binding to localhost on port 9999
#     server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
#
#     # Activate the server; this will keep running until you
#     # interrupt the program with Ctrl-C
#     server.serve_forever()
#
# if not __name__ == "__main__":
#     host = "localhost"  # 主机名，可以是ip,像localhost的主机名,或""
#     port = 1234  # 端口
#
#     # ThreadingTCPServer从ThreadingMixIn和TCPServer继承
#     # class ThreadingTCPServer(ThreadingMixIn, TCPServer): pass
#     server = SocketServer.ThreadingTCPServer((host, port), MyStreamRequestHandlerr)
#     server.serve_forever()
