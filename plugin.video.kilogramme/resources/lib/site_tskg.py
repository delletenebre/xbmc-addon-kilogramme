#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json
from _header import *

BASE_URL   = 'http://www.ts.kg/'
BASE_NAME  = 'TS.KG'
BASE_LABEL = 'ts'
SETT_DAYS  = plugin.get_setting('tskg_news_count', int)
SETT_PROV  = plugin.get_setting('tskg_provider', str)

@plugin.route('/site/' + BASE_LABEL)
def ts_index():
    item_list = get_categories(BASE_URL)
    
    items = [{
        'label': item['title'],
        'path' : plugin.url_for('ts_tvshows', category = item['category']),
        'icon' : item['icon'],
        'properties': {'fanart_image':item['fanart']},
    } for item in item_list]

    items = [{
        'label': set_color('[ Поиск ]', 'dialog', True),
        'path' : plugin.url_for('ts_search'),
        'icon' : get_local_icon('find')
    },{
        'label': set_color('Последние поступления', 'light', True),
        'path' : plugin.url_for('ts_lastadded', category = 'last')
    }] + items
    return items


@plugin.route('/site/' + BASE_LABEL + '/search')
def ts_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if(search_val):
        item_list = get_search(search_val)
        
        items     = [{
            'label': item['title'],
            'path' : plugin.url_for('ts_seasons', category = item['category'], name = item['name'], title = item['label'] ),
            'icon' : BASE_URL + 'covers/' + item['name'] + '.jpg',
        } for item in item_list]
        
        return items
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL)


@plugin.route('/site/' + BASE_LABEL + '/last')
def ts_lastadded():
    category  = plugin.request.args['category'][0]
    item_list = get_lastadded(BASE_URL)
    
    items = [{
        'label'       : item['title'],
        'path'        : plugin.url_for('ts_seasons', category = item['category'], name = item['name'], title = to_utf8(item['label']) ) if (not item['is_playable']) else item['url'],
        'icon'        : BASE_URL + 'covers/' + item['name'] + '.jpg',
        'is_playable' : item['is_playable']
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/<category>')
def ts_tvshows(category):
    item_list = get_tvshows(BASE_URL + category)
    
    items = [{
        'label': item['title'],
        'path' : plugin.url_for('ts_seasons', category = category, name = item['name'], title = to_utf8(item['title']) ),
        'icon' : item['icon']
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/<category>/<name>')
def ts_seasons(category, name):
    title     = plugin.request.args['title'][0]
    item_list = get_seasons_list(BASE_URL + category + '/' + name, title)
    items     = [{
        'label'      : item['title'],
        'path'       : plugin.url_for('ts_season', category = category, name = name, season = item['season'], title = title),
        'icon'       : BASE_URL + 'covers/' + name + '.jpg'#item['icon'],
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/<category>/<name>/<season>')
def ts_season(category, name, season):
    item_list = get_videos_by_season(BASE_URL + category + '/' + name, plugin.request.args['title'][0], season)
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')




#method
def get_lastadded(url):
    items = []
    try:
        result = common.fetchPage({'link': url})
        
        if result['status'] == 200:
            html = result['content']
            
            news_table = common.parseDOM(html, 'table', attrs = {'class': 'news-table'})
            items_list = common.parseDOM(news_table, 'tr')
            days       = 0
            days_show  = SETT_DAYS + 1
            day_title  = ''
            
            for item in items_list:
                day = common.parseDOM(item, 'h3')
                if(day):
                    day_title = day[0]
                    days     += 1
                
                if(days <= days_show):
                    title = common.parseDOM(item, 'a')
                    href  = common.parseDOM(item, 'a', ret='href')
                    
                    try:   badge = '&emsp;[B]' + common.parseDOM(item, 'span')[0] + '[/B]'
                    except:badge = ''

                    if(title and to_utf8(badge).find('ВАЖНО') < 0):
                        route       = get_url_route(href[0])
                        is_playable = len(route) > 3
                        label       = common.replaceHTMLCodes( day_title[0:5] + '&emsp;' + title[0] + badge )
                        label2      = common.replaceHTMLCodes( title[0] )
                        
                        items.append({'title':label, 'icon':'', 'is_playable':is_playable, 'url':get_url_for_video(href[0]) if(is_playable) else href[0], 'name':route[2], 'category':route[1], 'label':label2})
    except:
        pass
    return items


#method
def get_categories(url):
    items = []
    try:
        result = common.fetchPage({'link': url})
        
        if result['status'] == 200:
            html = result['content']
            
            #branding = common.parseDOM(html, 'body', ret = 'style')[0]
            branding = ''#re.compile("url\(\'(.+?)\'\)").findall(branding)[0]
        
            
            nav_tabs = common.parseDOM(html, 'ul', attrs = {'class': 'nav nav-tabs'})
            li       = common.parseDOM(nav_tabs, 'li')
            for item in li:
                is_external = common.parseDOM(item, 'a', ret = 'class')
                if(not is_external):
                    title = common.parseDOM(item, 'a')
                    href  = common.parseDOM(item, 'a', ret = 'href')
                    icon  = ''
                    
                    category = get_url_route(href[0])[1]
                    if(category == 'tvshows' or category == 'rushows'):
                        title = [title[0] + ' ТВ-шоу'.decode('utf-8')]
                    
                    if(category != 'megogo'):
                        items.append({'title':title[0], 'category':category, 'icon':icon, 'fanart':branding})
    except:
        pass
    return items


#method
def get_tvshows(url):
    items = []
    try:
        result = common.fetchPage({'link': url})
        if result['status'] == 200:
            html = result['content']
            div_list = common.parseDOM(html, 'div', attrs = {'class': 'categoryblocks'})
            for item in div_list:
                title = common.parseDOM(item, 'span', attrs = {'class': 'caption'})
                href  = common.parseDOM(item, 'a',    ret = 'href')
                icon  = common.parseDOM(item, 'img',  ret = 'src')
                
                name = get_url_route(href[0])[2]
                items.append({'title':title[0], 'name':name, 'icon':icon[0]})
    except:
        pass
    return items


#method
def get_seasons_list(url, title):
    items = []
    url_prefix = ''
    try:
        result = common.fetchPage({'link': url})
        if result['status'] == 200:
            html = result['content']
            div_main = common.parseDOM(html,     'div', attrs = {'class': 'episodes'})
            seasons  = common.parseDOM(div_main, 'ul',  attrs = {'class': 'breadcrumb'})
            for item in seasons:
                season_number = common.parseDOM(item, 'h4')
                
                for i in range(0, len(season_number)):
                    label = common.replaceHTMLCodes( title.decode('utf-8') + ' &emsp; ' + season_number[i] )
                    
                    items.append({'title':label, 'url':url, 'icon':'', 'season':season_number[i][6:]})
            
            if(len(seasons) > 1):
                items = [{'title': '[B]' + title + '   Все сезоны[/B]', 'url':url, 'icon':'', 'season':0}] + items
    except:
        pass
    return items
    

#method
def get_videos_by_season(url, title, season):
    items = []
    season = int(season)
    try:
        result = common.fetchPage({'link': url})
        if result['status'] == 200:
            html = result['content']
            div_main = common.parseDOM(html,     'div', attrs = {'class': 'episodes'})
            seasons  = common.parseDOM(div_main, 'ul',  attrs = {'class': 'breadcrumb'})
            for item in seasons:
                season_number        = common.parseDOM(item, 'h4')
                title_episode_number = common.parseDOM(item, 'a')
                title_original       = common.parseDOM(item, 'a', ret = 'data-original-title')
                href_list            = common.parseDOM(item, 'a', ret = 'href')
                
                for i in range(0, len(title_episode_number)):
                    if(int(season_number[0][6:]) == season or season == 0):
                        try:    suffix = ' &emsp; ' + common.replaceHTMLCodes(title_original[i])
                        except: suffix = ''
                        
                        s_num_e_num = 's' + season_number[0][6:] + 'e' + title_episode_number[i]

                        for l in range(len(s_num_e_num), 6):
                            s_num_e_num += '&ensp;'
                        
                        label = common.replaceHTMLCodes( title.decode('utf-8') + ' &emsp; ' + s_num_e_num + suffix )
                        href  = get_url_for_video(href_list[i])
                        icon  = ''
                        
                        items.append({'title':label, 'url':href, 'icon':icon})
                    else:
                        pass
    except:
        pass
    return items


#method
def get_search(search_value):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'js/search'})
        if result['status'] == 200:
            html = result['content']
            data = re.compile('data = {(.+?),}').findall(html)
            data = json.loads('{'+data[0]+'}')
            
            for key, val in data.iteritems():
                _key = key.encode('utf-8')
                if(search_value.lower() in _key.lower()):
                    route       = get_url_route(val)
                    label       = _key
                    a           = _key.find(' (')
                    label2      = _key if(a < 0) else _key[:a]
                    
                    items.append({'title':label, 'icon':'', 'url':val, 'name':route[2], 'category':route[1], 'label':label2})
    except: pass
    return items


def get_url_for_video(url):
    data_prefix = 'datakt' if(SETT_PROV == 'Кыргызтелеком') else 'data2'
    return url.replace('http://www.ts.kg/', 'http://' + data_prefix + '.ts.kg/video/') + '.mp4'+UserAgent
