#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, json, urllib
from _header import *

BASE_URL    = 'http://namba.kg/serials/'
BASE_API    = 'http://namba.kg/api'
BASE_NAME   = 'Namba.Сериалы'
BASE_LABEL  = 'nbts'

@plugin.route('/site/' + BASE_LABEL)
def nbts_index():
    item_list = get_categories()
    items     = []
    
    if item_list:
        items = [{
            'label'     : item['title'],
            'path'      : plugin.url_for('nbts_serials_by_category', id = item['id']),
            'thumbnail' : item['icon'],
        } for item in item_list]

        items = [{
            'label': set_color('[ Поиск ]', 'dialog', True),
            'path' : plugin.url_for('nbts_search'),
            'icon' : get_local_icon('find')
        },{
            'label': set_color('Последние поступления', 'bright', True),
            'path' : plugin.url_for('nbts_top30', type = 'new')
        },{
            'label': set_color('Популярные - ТОП 30', 'bright', True),
            'path' : plugin.url_for('nbts_top30', type = 'popular')
        }] + items
    else:
        plugin.notify('Сервер недоступен', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/top30/<type>')
def nbts_top30(type):
    item_list = get_top30(type)
    
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('nbts_seasons', serial_id = item['id']),
        'thumbnail' : item['icon'],
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/category/<id>')
def nbts_serials_by_category(id):
    item_list = get_serials_by_category(id)
    
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('nbts_seasons', serial_id = item['id']),
        'thumbnail' : item['icon'],
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/serial/<serial_id>')
def nbts_seasons(serial_id):
    item_list = get_seasons(serial_id, 0)
    xbmc.log(str(item_list))

    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('nbts_season', serial_id = item['serial_id'], season_id = item['season_id']),
        'thumbnail' : item['icon'],
        'is_not_folder': False if item['season_id'] == '0' else True
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/serialw/<serial_id>/season/<season_id>')
def nbts_season(serial_id, season_id):
    plugin.notify('Пожалуйста, подождите...', BASE_NAME, 3000, get_local_icon('noty_' + BASE_LABEL))

    item_list = get_seasons(serial_id, season_id)
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')


@plugin.route('/site/' + BASE_LABEL + '/search')
def nbts_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if(search_val):
        item_list = get_search_results(str(search_val))
        items = []
        if item_list:
            items = [{
                'label'     : item['title'],
                'path'      : plugin.url_for('nbts_seasons', serial_id = item['id']),
                'thumbnail' : item['icon'],
            } for item in item_list]
        else:
            plugin.notify('Сериалы не найдены', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))
        
        return items
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL)




#method
def get_search_results(search_query):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'all_serials.php'})
        if result['status'] == 200:
            html = result['content']

            serials    = common.parseDOM(html, 'ul', attrs={'class':'last-serials serials-list'})
            serials_li = common.parseDOM(serials, 'li')

            for item in serials_li:
                title = common.parseDOM(item, 'img', ret='title')[0]
                icon  = common.parseDOM(item, 'img', ret='src')[0]
                href  = common.parseDOM(item, 'a', ret='href')[0]
                param = common.getParameters(href)

                title_lower = title.lower().encode('utf-8')
                if (search_query != '' and title_lower.find(search_query.lower()) > -1):
                    items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'id':param['id']})
    except: pass
    return items

#method
def get_top30(type = 'new'):
    #type = popular || new
    items = []
    try:
        result = common.fetchPage({'link': BASE_API + '/?type=' + type + '&service=home&action=serials&limit=30'})
        if result['status'] == 200:
            result_json = json.loads(result['content'])
            
            for item in result_json:
                name = common.replaceHTMLCodes( item['title'] )
                id   = item['id']
                icon = item['picture_url'] if item['picture_url'] != '' else item['image']

                #items.append(get_seasons(id))
                items.append({'title':name, 'icon':icon, 'id':id})
    except: pass
    return items


#method
def get_categories():
    items = []
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 720)
        return cache['categories']
    except:
        try:
            result = common.fetchPage({'link': BASE_URL})
            if result['status'] == 200:
                html = result['content']
                
                categories = common.parseDOM(html, 'ul', attrs={'class':'categories-menu'})
                categories_li = common.parseDOM(categories, 'li')

                for item in categories_li:
                    title = common.parseDOM(item, 'a')[0]
                    href  = common.parseDOM(item, 'a', ret='href')[0]
                    param = common.getParameters(href)
                    id    = ''

                    if param.get('id'):
                        id = param['id']
                    else:
                        id = param['type']

                    items.append({'title':title, 'icon':'', 'id':id})
                    cache['categories'] = items
        except: pass
    return items
    
#method
def get_serials_by_category(id):
    items = []
    try:
        if id.isdigit() == True:
            link = BASE_URL + 'category.php?id=' + str(id)
        else:
            link = BASE_URL + 'listco.php?type=' + urllib.quote(id)
        
        result = common.fetchPage({'link': link})
        if result['status'] == 200:
            html = result['content']
            
            serials = common.parseDOM(html, 'ul', attrs={'class':'serials-list'})
            serials_li = common.parseDOM(serials, 'li')

            for item in serials_li:
                title = common.parseDOM(item, 'img', ret='title')[0]
                icon  = common.parseDOM(item, 'img', ret='src')[0]
                href  = common.parseDOM(item, 'a', ret='href')[0]
                param = common.getParameters(href)

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'id':param['id']})
    except: pass
    return items


#method
def get_seasons(serial_id, season_id = 0):
    items = []
    serial_id = int(serial_id)
    season_id = int(season_id)

    try:
        if season_id == 0:
            link = BASE_URL + 'serial.php?id=' + str(serial_id)
        else:
            link = BASE_URL + 'season.php?serial_id=' + str(serial_id) + '&season_id=' + str(season_id)

        result = common.fetchPage({'link': link})
        if result['status'] == 200:
            html = result['content']
            
            if season_id == 0:
                desc = common.parseDOM(html, 'div', attrs={'class':'content-side'})
                name = common.parseDOM(desc, 'h1')[0]
                icon = common.parseDOM(desc, 'img', ret = 'src')[0]

                seasons = common.parseDOM(html, 'div', attrs={'class':'panel-title'})

                for i in range(0, len(seasons)):
                    seasons_h2 = common.parseDOM(seasons[i], 'h2')[0]
                    title     = name + '&emsp;' + seasons_h2
                    season_id = seasons_h2[6:]

                    items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'serial_id':serial_id, 'season_id':season_id})
                    
            else:
                panl       = common.parseDOM(html, 'div', attrs={'class':'panel-title'})
                name       = common.parseDOM(panl[0], 'a')[0]
                season_num = panl[1]

                desc = common.parseDOM(html, 'div', attrs={'class':'serial-description'})[0]

                videos     = common.parseDOM(html,   'ul',  attrs={'class':'videos-pane'})
                videos_li  = common.parseDOM(videos, 'li')

                for item in videos_li:
                    title = name + '&emsp;' + season_num + '&emsp;' + common.parseDOM(item, 'div', attrs={'class':'grey'})[0]
                    href  = common.parseDOM(item, 'a', ret = 'href')[0]
                    param = common.getParameters(href)
                    icon  = common.parseDOM(item, 'img', ret = 'src')[0]

                    items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'url':get_movie_url(param['id'])})
            
    except: pass
    return items


#method
def get_movie_url(id):
    href = ''
    try:
        result = common.fetchPage({'link': BASE_URL + 'watch.php?id=' + str(id)})
        if result['status'] == 200:
            html     = result['content']
            video_id = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(html)[0]

            result = common.fetchPage({'link': BASE_API + '/?service=video&action=video&id=' + video_id})
            if result['status'] == 200:
                result_json = json.loads(result['content'])

                name = result_json['video']['title']
                href = result_json['video']['download']['flv']
    except: pass
    return href