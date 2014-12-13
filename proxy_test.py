#!/usr/bin/python
# -*- coding: UTF-8 -*-
import select
import socket
import re
import urllib2
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def handler(data):
    data = data.strip()
    # print data

    # 按行分隔header
    header = data.split('\r\n')

    # 对header首行的处理
    pattern = r'^(GET|POST|HEAD|PUT|DELETE|TRACE|CONNECT|OPTIONS)\s(http|https)?://([^/]+)([^\s]*)\s([\s\S]*)'
    regex = re.compile(pattern)
    first_line = regex.findall(header[0])[0]
    # header[0] = first_line[0] + ' ' + first_line[3]
    del header[0]
    # urllib2_header = [(first_line[0] + ' ' + first_line[3])]

    urllib2_header = {}
    for line in header:
        row = line.split(':')
        urllib2_header[row[0]] = row[1]

    # print urllib2_header
    # print header
    print first_line[1] + '://' + first_line[2] + first_line[3]

    req = urllib2.Request(first_line[1] + '://' + first_line[2] + first_line[3], None, urllib2_header)
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
    #     if not len(snippet):
    #         break
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

if 1:

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # server_address = (socket.gethostbyname(socket.gethostname()), 1234)
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
            try:
                s.send(str(handler(data)))
                s.close()
                inputs.remove(s)
                outputs.remove(s)
            except:
                pass

        for s in exceptional:
            # print " exception condition on ", s.getpeername()
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()