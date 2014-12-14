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


def handler(data):
    data = data.strip()
    if not data:
        return None

    # 按行分隔header
    header = data.split('\r\n')

    # 对header首行的处理
    pattern = r'^(GET|POST|HEAD|PUT|DELETE|TRACE|CONNECT|OPTIONS)\s(http://|https://)?([^/]+)([^\s]*)\s([\s\S]*)'
    regex = re.compile(pattern)
    try:
        first_line = regex.findall(header[0])[0]
    except:
        print data
    # header[0] = first_line[0] + ' ' + first_line[3]
    del header[0]
    # urllib2_header = [(first_line[0] + ' ' + first_line[3])]

    urllib2_header = {}
    for line in header:
        row = line.split(':')
        if not row[0] == 'Accept-Encoding':  # 暂时不支持 gzip
            urllib2_header[row[0]] = row[1]

    # print urllib2_header
    # print header
    print first_line[1] + first_line[2] + first_line[3]

    req = urllib2.Request(first_line[1] + first_line[2] + first_line[3], None, urllib2_header)
    resp = urllib2.urlopen(req, None, 2)
    html = resp.read()
    return html


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
#         self.data = ''
#         time.sleep(0.1)
#         while True:
#             # self.request.setBlocking(0)
#             str_data = self.request.recv(1).strip()
#             if not len(str_data):
#                 break
#             self.data += str_data
#
#         print "{} wrote:".format(self.client_address[0])
#         print self.data
#         # just send back the same data, but upper-cased
#         self.request.sendall(self.data.upper())
#
#
# if __name__ == "__main__":
#     HOST, PORT = "localhost", 1234
#
#     # Create the server, binding to localhost on port 9999
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



import select
import socket
import Queue

#create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
#set option reused
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_address = ('localhost', 1234)
server.bind(server_address)

server.listen(10)

#sockets from which we except to read
inputs = [server]

#sockets from which we expect to write
outputs = []

#Outgoing message queues (socket:Queue)
message_queues = {}

#A optional parameter for select is TIMEOUT

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    # When timeout reached , select return three empty lists
    if not (readable or writable or exceptional):
        break
    for s in readable:
        if s is server:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = Queue.Queue()
        else:
            data = ''
            try:
                while True:
                    str_data = s.recv(2048)
                    if not len(str_data):
                        break
                    data += str_data
            except:
                pass

            if data:
                message_queues[s].put(data)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)
            else:
                #Interpret empty result as closed connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                #remove message queue
                del message_queues[s]
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except:
            if s in outputs:
                outputs.remove(s)
        else:
            try:
                # print len(outputs)
                # print len(inputs)
                # print len(message_queues)
                # s.send(next_msg)
                print next_msg
                s.send(handler(next_msg))
                s.close()
                inputs.remove(s)
                outputs.remove(s)
                del message_queues[s]
            except:
                pass

    for s in exceptional:
        print exceptional
        #stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        #Remove message queue
        del message_queues[s]


# if 0:
#
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.setblocking(False)
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#     # server_address = (socket.gethostbyname(socket.gethostname()), 1234)
#     server_address = ('127.0.0.1', 1234)
#     server.bind(server_address)
#
#     server.listen(10)
#
#     inputs = [server]
#
#     outputs = []
#
#     message = []
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