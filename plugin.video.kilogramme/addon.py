#!/usr/bin/python
# -*- coding: utf-8 -*-

import cookielib
import urllib2
cookiejar = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
opener = urllib2.build_opener(cookie_handler)

if __name__ == '__main__':
    from resources.lib.index import plugin
    plugin.run()