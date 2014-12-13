#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib2
import select
import socket
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def receive(data):
    print data.strip()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_address = ('127.0.0.1', 1234)
server.bind(server_address)

server.listen(10)

inputs = [server]

outputs = []

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)

    if not (readable or writable or exceptional):
        break

    for s in readable:
        if s is server:
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
        else:
            data = ''
            try:
                while True:
                    str_data = s.recv(1024)
                    if not len(str_data):
                        break
                    data += str_data
            except:
                pass

            if data:
                # print " received ", data, "from ", s.getpeername()
                if s not in outputs:
                    outputs.append(s)
            else:
                # print "  closing", client_address
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()

    for s in writable:
        # s.send(str(len(outputs)))
        # s.send(str(s.getpeername()))
        outputs.remove(s)
        receive(data)
        response = urllib2.urlopen('http://www.douban.com', timeout=10)
        s.send(response.read())
        s.close()
        inputs.remove(s)

    for s in exceptional:
        # print " exception condition on ", s.getpeername()
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()