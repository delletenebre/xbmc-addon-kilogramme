#!/usr/bin/python
# -*- coding: utf-8 -*-

import cookielib, urllib2, socket
cookiejar = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)

socket.setdefaulttimeout(3)

if __name__ == '__main__':
    from resources.lib.index import plugin
    plugin.run()