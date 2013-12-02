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

import sys, os, random, xbmc, xbmcaddon, xbmcgui

sys.path.append( os.path.join( to_utf8(xbmcaddon.Addon().getAddonInfo( 'path' )), 'resources', 'lib', 'libs') )

from xbmcswift2 import Plugin
plugin = Plugin()


import CommonFunctions
common = CommonFunctions
common.dbg = False
common.dbglevel = 0



UserAgents = ['|User-Agent=Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
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
UserAgent = UserAgents[random.randrange(0,len(UserAgents)-1,1)]

def kgontv_playlist(items = [{}], type='video'):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        for item in items:
            listitem = xbmcgui.ListItem(item['title'], iconImage="DefaultVideo.png", thumbnailImage=item['icon'])
            listitem.setInfo( type='Video', infoLabels=item )
            
            try:    listitem.setProperty('duration', item['properties']['duration'])
            except: pass
            try:    listitem.setProperty('fanart_image', item['properties']['fanart_image'])
            except: pass
            
            playlist.add(item['url'], listitem)
            
def get_local_icon(name):
    return os.path.join(plugin.addon.getAddonInfo('path'), 'resources', 'media', str(name) + '.png')
    
def set_color(text = '', colorid = '', isBold = False):
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
		text = text.replace('[/B]','').replace('[B]','')

	return '[COLOR ' + color + ']' + text + '[/COLOR]'

    

