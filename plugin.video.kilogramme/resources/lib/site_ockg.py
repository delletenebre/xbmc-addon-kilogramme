#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json, time, math
from _header import *

BASE_URL     = 'http://cinemaonline.kg/'
BASE_NAME    = 'Cinema Online'
BASE_LABEL   = 'oc'

@plugin.cached()
def get_cookie():
    result = {'phpsessid':'', 'utmp':'', 'set':''}
    try:
        a = common.fetchPage({'link': BASE_URL})
        b = common.fetchPage({'link': BASE_URL + 'cinema.png?' + str(int(time.time()))})
        
        result['set'] = a['header']['Set-Cookie'] + '; ' + b['header']['Set-Cookie']
        
        cookies = common.getCookieInfoAsHTML()
        result['phpsessid'] = common.parseDOM(cookies, 'cookie', attrs={'name': 'PHPSESSID'}, ret='value')[0]
        result['utmp']      = common.parseDOM(cookies, 'cookie', attrs={'name': '_utmp'},     ret='value')[0]
    except: pass
    
    return result
    
COOKIE       = get_cookie()
BASE_API_URL = BASE_URL + 'api.php?format=ajax&' + COOKIE['phpsessid'] + '&JsHttpRequest='+str(int(time.time()))+'-xml'

@plugin.route('/site/' + BASE_LABEL)
def oc_index():
    items = [{
        'label': set_color('[ Поиск ]', 'dialog', True),
        'path' : plugin.url_for('oc_search'),
        'icon' : get_local_icon('find')
    },{
        'label': set_color('Новинки на CinemaOnline', 'light', True),
        'path' : plugin.url_for('oc_category', id = 0)
    },{
        'label': 'Бестселлеры',
        'path' : plugin.url_for('oc_bestsellers')
    },{
        'label': 'Лучшие по версии IMDB',
        'path' : plugin.url_for('oc_category', id = 2)
    },{
        'label': 'Лучшие по версии КиноПоиск',
        'path' : plugin.url_for('oc_category', id = 9)
    }]
    
    return items

@plugin.route('/site/' + BASE_LABEL + '/bestsellers')
def oc_bestsellers():
    item_list = get_bestsellers()
    
    items     = [{
        'label'       : item['label'],
        'path'        : plugin.url_for('oc_movie', id = item['id']),
        'icon'        : item['icon'],
    } for item in item_list]

    return items
    
@plugin.route('/site/' + BASE_LABEL + '/category/<id>')
def oc_category(id):
    item_list = get_movie_list(id)
    
    items     = [{
        'label'       : item['label'],
        'path'        : plugin.url_for('oc_movie', id = item['id']),
        'properties'  : item['properties'],
        'icon'        : item['icon'],
    } for item in item_list['items']]
    
    if(item_list['sys_items']):
        for item in item_list['sys_items']:
            items.insert(0, {
                'label': item['label'],
                'path' : plugin.url_for('oc_go_to_page', id = id, page = item['page']) if('search' in item) else plugin.url_for('oc_category_pagination', id = id, page = item['page']),
                'icon' : item['icon']
            })

    return items
    
@plugin.route('/site/' + BASE_LABEL + '/category/<id>/<page>')
def oc_category_pagination(id, page = '1'):
    page = int(page)
    item_list = get_movie_list(id, page)
    items     = [{
        'label'       : item['label'],
        'path'        : plugin.url_for('oc_movie', id = item['id']),
        'properties'  : item['properties'],
        'icon'        : item['icon'],
    } for item in item_list['items']]

    if(item_list['sys_items']):
        for item in item_list['sys_items']:
            items.insert(0, {
                'label': item['label'],
                'path' : plugin.url_for('oc_go_to_page', id = id, page = item['page']) if('search' in item) else plugin.url_for('oc_category_pagination', id = id, page = item['page']),
                'icon' : item['icon']
            })

    return plugin.finish(items, update_listing=True)
    
@plugin.route('/site/' + BASE_LABEL + '/to_page/category/<id>/<page>')
def oc_go_to_page(id, page = 1):
    search_page = common.getUserInputNumbers('Укажите страницу')
    if(search_page):
        search_page = int(search_page) - 1 if (int(search_page) > 0) else 1
        item_list = get_movie_list(id, search_page)
        
        items     = [{
            'label'       : item['label'],
            'path'        : plugin.url_for('oc_movie', id = item['id']),
            'properties'  : item['properties'],
            'icon'        : item['icon'],
        } for item in item_list['items']]

        if(item_list['sys_items']):
            for item in item_list['sys_items']:
                items.insert(0, {
                    'label': item['label'],
                    'path' : plugin.url_for('oc_go_to_page', id = id, page = item['page']) if('search' in item) else plugin.url_for('oc_category_pagination', id = id, page = item['page']),
                    'icon' : item['icon']
                })

        return plugin.finish(items, update_listing=True)
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL + '/category/' + id + '/' + str(int(page) - 1))
    

@plugin.route('/site/' + BASE_LABEL + '/movie/<id>')
def oc_movie(id):
    item_list = get_movie(id)
    
    items = [{
        'label'       : item['label'],
        'path'        : item['url'],
        'thumbnail'   : item['icon'],
        'properties'  : item['properties'],
        'is_playable' : True
    } for item in item_list['items']]

    if(item_list['playlist']):
        kgontv_playlist(item_list['items'])
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')
    else:
        return items

@plugin.route('/site/' + BASE_LABEL + '/search')
def oc_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if(search_val):
        item_list = get_search_results(str(search_val))
        
        items     = [{
            'label': item['label'],
            'path' : plugin.url_for('oc_movie', id = item['id'] ),
            'icon' : item['icon'],
        } for item in item_list]
        
        return items
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL)


#method
def get_bestsellers():
    items = []
    try:
        result = common.fetchPage({'link': BASE_API_URL, 'cookie':COOKIE['set'], 'post_data':{'action[0]':'Video.getBestsellers'}})
        
        if result['status'] == 200:
            html = result['content']
            data = json.loads(html)
            for item in data['js'][0]['response']['bestsellers']:
                for video in item['movies']:
                    label       = video['name'] + ' [' + item['name'] + ']'
                    icon        = BASE_URL + video['cover']
                    video_id    = video['movie_id']
                        
                    items.append({
                        'label'      : label,
                        'icon'       : icon,
                        'id'         : video_id
                    })
    except:
        pass
    return items


#method
def get_movie_list(order_id, page = '0'):
    sys_items = []
    items = []
    size = 40
    try:
        offset = int(page) * size
        
        result = common.fetchPage({'link': BASE_API_URL, 'cookie':COOKIE['set'], 'post_data':{'action[0]':'Video.getCatalog', 'offset[0]':str(offset), 'size[0]':str(size), 'order[0]':order_id}})
        
        if result['status'] == 200:
            data = json.loads(result['content'])
            data = data['js'][0]['response']
            
            total = int(data['total'])
            pages = {
                'total'  : int(math.ceil(total / size + 1)),
                'current': offset / size + 1
            }
            
            if pages['current'] > 1:
                sys_items.append({
                    'label' : set_color('[ Предыдущая страница ]'.decode('utf-8'), 'next', True),
                    'icon'  : get_local_icon('prev'),
                    'page'  : pages['current'] - 2
                })
            if pages['current'] < pages['total']:
                sys_items.append({
                    'label' : set_color('[ Следующая страница ]'.decode('utf-8'), 'next', True),
                    'icon'  : get_local_icon('next'),
                    'page'  : pages['current']
                })
            if total > size:
                sys_items.append({
                    'label' : common.replaceHTMLCodes( set_color(('[ Перейти на страницу ]' + '&emsp;' + str(pages['current']) + ' из ' + str(pages['total']) + ' страниц').decode('utf-8'), 'dialog', True) ),
                    'icon'  : get_local_icon('page'),
                    'page'  : pages['current'],
                    'search': True
                })
            
            
            for item in data['movies']:
                try:
                    try:    genres = '&emsp;[' + ', '.join(item['genres'][:3]) + ']'
                    except: genres = ''
                    
                    imdb      = {'rating':'0', 'votes':'0'}
                    kinopoisk = {'rating':'0', 'votes':'0'}
                    if('rating_imdb_value' in item):
                        imdb = {'rating':item['rating_imdb_value'], 'votes':item['rating_imdb_count']}
                    if('rating_kinopoisk_value' in item):
                        kinopoisk = {'rating':item['rating_kinopoisk_value'], 'votes':item['rating_kinopoisk_count']}
                    
                    rating = ''
                    if(imdb['rating'] != '0' and kinopoisk['rating'] != '0'):
                        rating = '&emsp;' + imdb['rating'] + ' (' + imdb['votes'] + ') / ' + kinopoisk['rating'] + ' (' + kinopoisk['votes'] + ')'
                    
                    country = ''
                    if('countries' in item):
                        country = item['countries'][0]
                    
                    properties = {
                        'Country'     : country,
                        'PlotOutline' : item['description'],
                        'Plot'        : item['long_description'],
                        'Year'        : item['year'],
                        'Rating'      : imdb['rating'],
                        'Votes'       : imdb['votes']
                    }
                    
                    country = '&emsp;(' + country + ')' if(country) else ''
                    
                    label       = common.replaceHTMLCodes( '[B]' + item['name'] + '[/B]' + country + genres + rating )
                    icon        = BASE_URL + item['cover']
                    video_id    = item['movie_id']

                    items.append({
                        'label'      : label,
                        'icon'       : icon,
                        'properties' : properties,
                        'id'         : video_id
                    })
                except:pass
    except:pass
    return {'items':items,'sys_items':sys_items}


#method
def get_search_results(search_value = ''):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'suggestion.php?q=' + search_value, 'cookie':COOKIE['set']})
        if result['status'] == 200:
            data = json.loads(result['content'])
            data = data['json'][0]['response']
            for item in data['movies']:
                try:
                    label    = item['name'] + '&emsp;(' + item['year'] + ')'
                    icon     = BASE_URL + item['cover']
                    video_id = item['movie_id']
                        
                    items.append({
                        'label': common.replaceHTMLCodes( label ),
                        'icon' : icon,
                        'id'   : video_id
                    })
                except:pass
    except:pass
    return items
        
        
#method
def get_movie(id):
    items = []
    try:
        result = common.fetchPage({'link': BASE_API_URL, 'cookie':COOKIE['set'], 'post_data':{'action[0]':'Video.getMovie','movie_id[0]':id}})
        
        if result['status'] == 200:
            data  = json.loads(result['content'])
            item  = data['js'][0]['response']['movie']
            
            is_playlist = False
            icon   = BASE_URL + item['covers'][0]['original']
            
            if(len(item['files']) == 1):
                label       = item['name']
                url         = get_playable_url(item['files'][0]['path'])
                properties  = {
                    'duration'     : item['files'][0]['metainfo']['playtime'],
                    'fanart_image' : '' if(len(item['files'][0]['frames']) == 0) else BASE_URL + item['files'][0]['frames'][0],
                }
                
                items.append({
                    'label'      : '[B]ПРОСМОТР[/B]: '.decode('utf-8') + label,
                    'icon'       : icon,
                    'properties' : properties,
                    'url'        : url
                })
                
                try:
                    trailer = item['trailer']
                    
                    try:   name = trailer['name']
                    except:name = 'Трейлер'
                    
                    items.append({
                        'label'      : name,
                        'icon'       : get_local_icon('kinopoisk'),
                        'properties' : {'fanart_image':trailer['preview']},
                        'url'        : trailer['video']
                    })
                except:pass
            elif(len(item['files']) > 1):
                is_playlist = True
                item['files'].pop(0)
                for video in item['files']:
                    label       = item['name'] + ': ' + video['name']
                    url         = get_playable_url(video['path'])
                    properties  = {
                        'duration'     : video['metainfo']['playtime'],
                        'fanart_image' : '' if(len(video['frames']) == 0) else BASE_URL + video['frames'][0],
                    }
                    
                    items.append({
                        'title'      : label,
                        'label'      : label,
                        'icon'       : icon,
                        'properties' : properties,
                        'url'        : url
                    })
    except:pass
    return {'items':items,'playlist':is_playlist}


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
                _key = to_utf8(key)
            
                if(_key.lower().find(search_value.lower()) > -1):
                    route       = get_url_route(val)
                    label       = _key
                    a           = _key.find(' (')
                    label2      = _key if(a < 0) else _key[:a]
                    
                    items.append({'title':label, 'icon':'', 'url':val, 'name':route[2], 'category':route[1], 'label':label2})
    except:
        pass
    return items

def get_playable_url(url):
    return str(url).replace('/home/video/', 'http://cinemaonline.kg:8080/') + UserAgent

