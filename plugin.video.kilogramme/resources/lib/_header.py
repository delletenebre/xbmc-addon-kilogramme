#!/usr/bin/python
# -*- coding: utf-8 -*-

def _to_unicode(s):
    """credit : sfaxman"""
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s


def to_utf8(s):
    return _to_unicode(s).encode('utf-8')


def get_url_route(url):
    result = url.rsplit('/')
    del result[0:2]
    return result


import sys, os, platform, random, xbmc, xbmcaddon, xbmcgui

sys.path.append(os.path.join(to_utf8(xbmcaddon.Addon().getAddonInfo('path')), 'resources', 'lib', 'libs'))

from xbmcswift2 import Plugin, actions

plugin = Plugin()

import CommonFunctions

common = CommonFunctions
common.dbg = False
common.dbglevel = 5


def asyncHTTP(url):
    import urllib2, threading

    class aynsHTTPHandler(urllib2.HTTPHandler):
        def http_response(self, req, response):
            return response

    o = urllib2.build_opener(aynsHTTPHandler())
    t = threading.Thread(target=o.open, args=(url,))
    t.start()


# ======== system variables ========
xbmc_var = {
    'screen_resolution': '0x0',
    'user_agent': 'XBMC/null'
}
try:
    xbmc_var = {
        'screen_resolution': xbmc.getInfoLabel('System.ScreenWidth') + 'x' + xbmc.getInfoLabel('System.ScreenHeight'),
        'user_agent': 'XBMC/' + xbmc.getInfoLabel('System.BuildVersion').partition(' ')[
            0] + ' (' + platform.system() + ') ' + plugin.addon.getAddonInfo('name') + '/' + plugin.addon.getAddonInfo(
            'version')
    }
except:
    pass
# ======== END system variables ========


#======== google analytics ========
def ga_generate_client_id():
    import uuid

    return uuid.uuid4()


from UniversalAnalytics import Tracker

if plugin.get_setting('ga_vstr', str) == '':
    plugin.set_setting('ga_vstr', str(ga_generate_client_id()))

GA_VSTR = plugin.get_setting('ga_vstr', str)


def ga_create(ga_code):
    ga_tracker = Tracker.create(ga_code, name='GATracker' + plugin.addon.getAddonInfo('name'), client_id=GA_VSTR,
                                user_agent=xbmc_var['user_agent'])
    ga_tracker.set('sr', xbmc_var['screen_resolution'])
    ga_tracker.set('av', plugin.addon.getAddonInfo('version'));
    ga_tracker.set('cd1', plugin.addon.getAddonInfo('version'));
    return ga_tracker


def ga(ga_code='UA-46965070-1', url=''):
    try:
        from urlparse import urlparse

        ga_tracker = ga_create(ga_code)
        ga_tracker.send('pageview', '{uri.path}'.format(uri=urlparse(url)))
        #ga_tracker.send('event', 'api_request', 'xbmc_request', 'kilogramme')
    except:
        pass


ga(url='/xbmc.kilogramme')
#======== END google analytics ========

#======== net.kg stats ========
def netkg_stats(id, url=None):
    #try:
    from urllib import quote
    from urllib2 import Request
    from random import random
    from urlparse import urlparse
    from urllib import urlencode

    referer = '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))
    if referer == url:
        referer = ''

    net_kg_cookie = 'astratop=1'
    net_kg_url = 'http://www.net.kg/img.php?id=' + str(id) + '&refer=' + quote(str(referer)) + '&page=' + quote(
        url) + '&c=yes&java=now&razresh=' + xbmc_var['screen_resolution'] + '&cvet=24&jscript=1.3&rand=' + str(random())
    net_kg_request = Request(
        net_kg_url,
        headers={
            'User-Agent': xbmc_var['user_agent'],
            'Cookies': net_kg_cookie,
        }
    )

    asyncHTTP(net_kg_request)
    #except: pass


#======== END net.kg stats ========

#======== ALL stats ========
def kg_stats(url, ga_code, netkg_id=None):
    return
    ga(ga_code, url)
    #if netkg_id:
    #netkg_stats(netkg_id, url)

#======== END ALL stats ========


UserAgents = [
    '|User-Agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
    '|User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.110 Safari/537.36',
    '|User-Agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    '|User-Agent=Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    '|User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
    '|User-Agent=Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; chromeframe/12.0.742.112)',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)',
    '|User-Agent=Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)']
UserAgent = UserAgents[random.randint(0, len(UserAgents) - 1)]


def kgontv_playlist(items=[{}], type='video'):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for item in items:
        listitem = xbmcgui.ListItem(item['title'], iconImage="DefaultVideo.png", thumbnailImage=item['icon'])
        listitem.setInfo(type='Video', infoLabels={'Title': item['title']})

        try:
            listitem.setProperty('duration', item['properties']['duration'])
        except:
            pass
        try:
            listitem.setProperty('fanart_image', item['properties']['fanart_image'])
        except:
            pass

        playlist.add(item['url'], listitem)


def get_local_icon(name):
    return os.path.join(plugin.addon.getAddonInfo('path'), 'resources', 'media', str(name) + '.png')


def set_color(text='', colorid='', isBold=False):
    if colorid == 'next':
        color = 'FF11b500'
    elif colorid == 'dialog':
        color = 'FFe37101'
    elif colorid == 'light':
        color = 'FF42aae0'
    elif colorid == 'bright':
        color = 'F0FF00FF'
    elif colorid == 'bold':
        return '[B]' + text + '[/B]'
    else:
        color = colorid

    if isBold == True:
        text = '[B]' + text + '[/B]'
    if isBold == False:
        text = text.replace('[/B]', '').replace('[B]', '')

    return '[COLOR ' + color + ']' + text + '[/COLOR]'


def str2minutes(t):
    time_list = t.split(':')
    if (len(time_list) == 3):
        minutes = (int(time_list[0]) * 60) + int(time_list[1]) + (int(time_list[2]) / 60)
    elif (len(time_list) == 2):
        minutes = int(time_list[0]) + (int(time_list[1]) / 60)
    else:
        minutes = int(time_list[0]) / 60
    return minutes


def KG_get_pagination(current=1, total=1, size=0, offset=0):
    import math

    items = []

    current = int(current)
    total = int(total)
    size = int(size)
    offset = int(offset)

    try:
        pages = {
            'total': total if (size == 0 and offset == 0) else int(math.ceil(total / size + 1)),
            'current': current if (current > 0) else 1
        }
        if pages['total'] < pages['current']:
            pages['current'] = pages['total']

        if pages['current'] > 1:
            items.append({
                'label': set_color('[ Предыдущая страница ]'.decode('utf-8'), 'next', True),
                'icon': get_local_icon('prev'),
                'page': pages['current'] - 1 - offset,
                'search': False
            })
        if pages['current'] < pages['total']:
            items.append({
                'label': set_color('[ Следующая страница ]'.decode('utf-8'), 'next', True),
                'icon': get_local_icon('next'),
                'page': pages['current'] + 1 - offset,
                'search': False
            })
        # if ( (size == 0) and (pages['total'] > 2) ) or ( (size > 0) and (total > size) ):
        #     items.append({
        #         'label' : common.replaceHTMLCodes( set_color(('[ Перейти на страницу ]' + '&emsp;' + str(pages['current']) + ' из ' + str(pages['total']) + ' страниц').decode('utf-8'), 'dialog', True) ),
        #         'icon'  : get_local_icon('page'),
        #         'page'  : pages['current'],
        #         'search': True
        #     })


        total = int(data['total'])
        pages = {
            'total': int(math.ceil(total / size + 1)),
            'current': offset / size + 1
        }


    except:
        pass

    return items


def add_pagination(items, pagination, url, id):
    for item in pagination:
        items.insert(0, {
            'label': item['label'],
            'path': plugin.url_for(url, id=id, page=item['page']),
            'icon': item['icon']
        })

        items.append({
            'label': item['label'],
            'path': plugin.url_for(url, id=id, page=item['page']),
            'icon': item['icon']
        })

    return items