#!/usr/bin/python
# -*- coding: utf-8 -*-
import cgi, traceback
from _header import *

BASE_NAME  = 'ТВ'
BASE_LABEL = 'tv'

URLS = {
    'TV1.KG': 'http://tv1.kg',
    '5 канал': 'http://www.ts.kg/stream/5stream',
    'Хамелеон ТВ': 'http://htv.kg/stream/',
    'НБТ': 'http://nbt-tv.kg',
    #'Боорсок ТВ': 'http://boorsoktv.kg/shap/index.html',
    'Любимый город': 'http://www.lctv.kg',
}
ICONS = {
    'TV1.KG': '150',
    '5 канал': '144',
    'Хамелеон ТВ': '',
    'НБТ': '',
    'Боорсок ТВ': '124',
    'Любимый город': '152',
}

@plugin.route('/site/' + BASE_LABEL)
def tv_index():
    plugin.notify('Пожалуйста, подождите...', BASE_NAME, 1000, get_local_icon('noty_icon'))
    item_list = get_channels()
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')


#@plugin.cached()
def get_channels():
    items = []

    for name, url in URLS.iteritems():
        try:
            r = common.fetchPage({
                'link': url,
            })
            if r['status'] == 200:
                html = r['content']
                url = ''

                if ( name == 'TV1.KG' or name == 'Хамелеон ТВ' or name == 'НБТ' or name == 'Любимый город' ):
                    params = cgi.parse_qs( common.parseDOM(html, 'param', attrs = {'name': 'flashvars'}, ret = 'value')[0] )
                    url = params['file'][0]

                elif ( name == '5 канал' ):
                    params = common.parseDOM(html, 'source', ret = 'src')[0]
                    url = params

                items.append({
                    'title': name,
                    'url': url,
                    'icon': get_local_icon('onlinetv/' + ICONS[name]) if ( ICONS[name] != '' ) else ''
                })
        except:
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items