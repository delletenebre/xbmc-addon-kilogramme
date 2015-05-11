#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, json
from _header import *

ontvkg_logn = plugin.get_setting('ontvkg_logn', str)
ontvkg_pass = plugin.get_setting('ontvkg_pass', str)
ontvkg_ppin = plugin.get_setting('ontvkg_ppin', str)
ontvkg_lang = plugin.get_setting('ontvkg_lang', str)

BASE_URL      = 'http://77.235.18.146/'
BASE_NAME     = 'Online TV'
BASE_LABEL    = 'ontvkg'
BASE_AUTH_URL = 'http://77.235.18.146/Auth/Login'
COOKIE        = ''

def get_ontvkg_cookie():
    result = ''
    cookie = plugin.get_storage(BASE_LABEL, TTL = 360)
    
    try:
        result = cookie['auth']
    except:
        #try:
        #auth   = common.fetchPage({'link': BASE_AUTH_URL, 'post_data':{'UserName':ontvkg_logn, 'Password':ontvkg_pass, 'RememberMe':'true'}})
        auth   = common.fetchPage({
            'link': BASE_AUTH_URL,
            'post_data':json.dumps({'UserName':ontvkg_logn,'Password':ontvkg_pass,'RememberMe':'true'}),
            'headers' : [
                ('Content-Type','application/json; charset=utf-8'),
                ('User-Agent','Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36 OPR/23.0.1522.60'),
            ],
        })

        for h in auth['header']:
            if h.find('Set-Cookie') > -1:
                result = h.replace('Set-Cookie: ', '').replace(' HttpOnly,', '').replace(' HttpOnly', '')
        #except: pass
    
    return result


@plugin.route('/site/' + BASE_LABEL)
def ontvkg_index():
    items = []
    COOKIE = get_ontvkg_cookie()
    if not COOKIE:
        plugin.notify('Ошибочная авторизация', 'OnlineTV.kg', image=get_local_icon('noty_' + BASE_LABEL))
    else:
        items = [{
            'label': set_color('Просмотр ТВ', 'light'),
            'path' : plugin.url_for('ontvkg_tv'),
            'icon' : get_local_icon('tv'),
            'is_not_folder': True,
        },{
            'label': 'Поиск передачи',
            'path' : plugin.url_for('ontvkg_search'),
            'icon' : '',
        },{
            'label': 'Поиск по жанру',
            'path' : plugin.url_for('ontvkg_genres'),
            'icon' : '',
        }]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/tv')
def ontvkg_tv():
    item_list = get_channels()
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')


@plugin.route('/site/' + BASE_LABEL + '/genres')
def ontvkg_genres():
    items = []
    item_list = get_genres()

    items = [{
        'label'      : item['label'],
        'path'       : plugin.url_for('ontvkg_shows_by_genre', type = 'genre', id = item['id']),
        'thumbnail'  : item['icon'],
    } for item in item_list]

    return items

@plugin.route('/site/' + BASE_LABEL + '/type/<type>/<id>/page/<page>', name='ontvkg_shows_by_genre_pagination')
@plugin.route('/site/' + BASE_LABEL + '/type/<type>/<id>',             name='ontvkg_shows_by_genre', options={'page': '1'})
def ontvkg_shows_by_genre(type, id, page):
	#type = genre || search
    items = []
    item_list = get_shows_by_genre(id, page, type)

    items = [{
        'label'        : item['label'],
        'path'         : plugin.url_for('ontvkg_shows_by_group', type = type, group_id = id, id = item['id']) if not item['is_playable'] else get_transmission_url(item['id']),
        'thumbnail'    : item['icon'],
        'is_playable'  : item['is_playable'],
        'is_not_folder': not item['is_playable'],
    } for item in item_list['items']]

    if(item_list['pagination']):
        for item in item_list['pagination']:
            items.insert(0, {
                'label': item['label'],
                'path' : plugin.url_for('ontvkg_shows_by_genre_pagination', type = type, id = id, page = item['page']) if item['search'] == False else plugin.url_for('ontvkg_go_to_page', type = type, id = id, page = item['page']),
                'icon' : item['icon'],
            })
    
    if(page == '1'):
        return items
    else:
        return plugin.finish(items, update_listing=True)


@plugin.route('/site/' + BASE_LABEL + '/to_page/<type>/<id>/<page>')
def ontvkg_go_to_page(type = 'genre', id = '0', page = '1'):
    search_page = common.getUserInputNumbers('Укажите страницу')
    if(search_page):
        page = search_page if (int(search_page) > 0) else '1'

        items = ontvkg_shows_by_genre(type, id, page)

        return plugin.finish(items, update_listing=True)
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL + '/' + str(type) + '/' + str(id) + '/page/' + str(page))


@plugin.route('/site/' + BASE_LABEL + '/transmissions/<group_id>/<id>')
def ontvkg_shows_by_group(group_id, id):
    plugin.notify('Пожалуйста, подождите...', BASE_NAME, 3000, get_local_icon('noty_' + BASE_LABEL))
    items = []
    item_list = get_transmission_group(group_id, id)

    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')


@plugin.route('/site/' + BASE_LABEL + '/search')
def ontvkg_search():
    search_val = plugin.keyboard('', 'Название передачи')
    if(search_val):
        return ontvkg_shows_by_genre('search', search_val, '1')
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL)





#method
def get_channels():
    items = []
    COOKIE = get_ontvkg_cookie()
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 360)
        return cache['channels']
    except: plugin.notify('Пожалуйста, подождите...', 'OnlineTV.kg', 10000, get_local_icon('noty_' + BASE_LABEL))
    
    #try:
    result = common.fetchPage({'link': BASE_URL + 'XMLService/Groups', 'cookie':COOKIE})
    if result['status'] == 200:
        xml = result['content']
        channel_group = {
            'id'  : common.parseDOM(xml, 'group', ret = 'id'),
            'name': common.parseDOM(xml, 'group', ret = 'name'),
        }
        for i in range(0, len(channel_group['id'])):
            result = common.fetchPage({'link': BASE_URL + 'XMLService/GroupChannels/' + channel_group['id'][i], 'cookie':COOKIE})
            if result['status'] == 200:
                xml = result['content']
                channel = {
                    'id'           : common.parseDOM(xml, 'channel', ret = 'id'),
                    'channelNumber': common.parseDOM(xml, 'channel', ret = 'channelNumber'),
                    'name'         : common.parseDOM(xml, 'channel', ret = 'name'),
                    'tId'          : common.parseDOM(xml, 'channel', ret = 'tId'),
                    'tName'        : common.parseDOM(xml, 'channel', ret = 'tName'),
                    'tDescription' : common.parseDOM(xml, 'channel', ret = 'tDescription'),
                }
            
                for j in range(0, len(channel['id'])):
                    title = common.replaceHTMLCodes( '[' + channel_group['name'][i] + ']&emsp;' + set_color(channel['name'][j], 'bold') )

                    
                    result = common.fetchPage({'link': BASE_URL + 'XMLService/LanguagesByChannelId/' + channel['id'][j], 'cookie':COOKIE})
                    if result['status'] == 200:
                        xml = result['content']
                        transmission = {
                            'name': common.parseDOM(xml, 'transmission', ret = 'name'),
                            'url' : common.parseDOM(xml, 'transmission', ret = 'url'),
                        }
                        
                        url = transmission['url'][0]
                        for l in range(0, len(transmission['name'])):
                            if(transmission['name'][l] == ontvkg_lang):
                                url = transmission['url'][l]
                                xbmc.log(url + ' - ' + channel['id'][j])
                                    
                    
                    items.append({'title':title, 'url':url, 'icon':get_local_icon('onlinetv/'+channel['id'][j])})
                    cache['channels'] = items
    #except: pass
    return items


#method
def get_genres():
    items = []
    COOKIE = get_ontvkg_cookie()
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 360)
        return cache['genres']
    except:
        try:
            result = common.fetchPage({'link': BASE_URL + 'XMLService/Genres', 'cookie':COOKIE})
            if result['status'] == 200:
                xml = result['content']
                genres = {
                    'id'                : common.parseDOM(xml, 'genre', ret = 'id'),
                    'name'              : common.parseDOM(xml, 'genre', ret = 'name'),
                    'IsParentControlled': common.parseDOM(xml, 'genre', ret = 'IsParentControlled'),
                }
                for i in range(0, len(genres['id'])):
                    items.append({'label':genres['name'][i], 'id':genres['id'][i], 'icon':''})
                    
                cache['genres'] = items
        except: pass
    return items


#method
def get_shows_by_genre(id, page, type = 'genre'):
    items = []
    pagination_items = []
    COOKIE = get_ontvkg_cookie()
    
    try:
        if type == 'genre':
            link = BASE_URL + 'XMLService/TransmissionsByGenreId/' + str(int(id)) + '/' + str(int(page)) + '/24'
        else:
            link = BASE_URL + 'XMLService/TransmissionsSearch/' + urllib.quote(str(id)) + '/' + str(int(page)) + '/24'

        result = common.fetchPage({'link': link, 'cookie':COOKIE})
        if result['status'] == 200:
            xml = result['content']

            #======== pagination ========#
            try:
                pages = {
                    'total'  : int(common.parseDOM(xml, 'transmissions', ret = 'count')[0]),
                    'current': int(page) if int(page) > 0 else 1
                }
                if pages['total'] < pages['current']:
                    pages['current'] = pages['total']
                
                if pages['current'] > 1:
                    pagination_items.append({
                        'label' : set_color('[ Предыдущая страница ]'.decode('utf-8'), 'next', True),
                        'icon'  : get_local_icon('prev'),
                        'page'  : pages['current'] - 1,
                        'search': False
                    })
                if pages['current'] < pages['total']:
                    pagination_items.append({
                        'label' : set_color('[ Следующая страница ]'.decode('utf-8'), 'next', True),
                        'icon'  : get_local_icon('next'),
                        'page'  : pages['current'] + 1,
                        'search': False
                    })
                if pages['total'] > 2:
                    pagination_items.append({
                        'label' : common.replaceHTMLCodes( set_color(('[ Перейти на страницу ]' + '&emsp;' + str(pages['current']) + ' из ' + str(pages['total']) + ' страниц').decode('utf-8'), 'dialog', True) ),
                        'icon'  : get_local_icon('page'),
                        'page'  : pages['current'],
                        'search': True
                    })
            except: pass
            #======== END pagination ========#

            shows = {
                'id'     : common.parseDOM(xml, 'transmission', ret = 'id'),
                'name'   : common.parseDOM(xml, 'transmission', ret = 'name'),
                'date'   : common.parseDOM(xml, 'transmission', ret = 'date'),
                'time_h' : common.parseDOM(xml, 'transmission', ret = 'hour'),
                'time_m' : common.parseDOM(xml, 'transmission', ret = 'minute'),
                'trCount': common.parseDOM(xml, 'transmission', ret = 'transmissionsCount'),
            }
            for i in range(0, len(shows['id'])):
                try:
                    date  = shows['date'][i] + ' ' + shows['time_h'][i] + ':' + shows['time_m'][i]
                    label = common.replaceHTMLCodes( date + '&emsp;' + shows['name'][i] )
                except:
                    label = common.replaceHTMLCodes( shows['name'][i] )

                items.append({'label':label, 'id':shows['id'][i], 'icon':'', 'is_playable':True if shows['trCount'][i] == '1' else False})
    except: pass
    return {'items':items, 'pagination':pagination_items}


#method
def get_transmission_group(genre_id, id):
    items = []
    COOKIE = get_ontvkg_cookie()
    
    try:
        result = common.fetchPage({'link': BASE_URL + 'XMLService/TransmissionsByGenreGroupedTransmissionId/' + str(int(genre_id)) + '/' + str(int(id)) + '/1/100', 'cookie':COOKIE})
        if result['status'] == 200:
            xml = result['content']
            shows = {
                'id'    : common.parseDOM(xml, 'transmission', ret = 'id'),
                'name'  : common.parseDOM(xml, 'transmission', ret = 'name'),
                'desc'  : common.parseDOM(xml, 'transmission', ret = 'description'),
                'date'  : common.parseDOM(xml, 'transmission', ret = 'date'),
                'time_h': common.parseDOM(xml, 'transmission', ret = 'hour'),
                'time_m': common.parseDOM(xml, 'transmission', ret = 'minute'),
            }

            for i in range(0, len(shows['id'])):
                date  = shows['date'][i] + ' ' + shows['time_h'][i] + ':' + shows['time_m'][i]
                label = common.replaceHTMLCodes( date + '&emsp;' + shows['name'][i].title() + ': ' + shows['desc'][i].title() )
                id    = shows['id'][i]

                items.append({'title':label, 'url':get_transmission_url(id), 'icon':''})
    except: pass
    return items


#method
def get_transmission_url(id):
    COOKIE = get_ontvkg_cookie()
    
    try:
        result = common.fetchPage({'link': BASE_URL + 'XMLService/LanguagesByTransmissionId/' + str(int(id)), 'cookie':COOKIE})
        if result['status'] == 200:
            xml = result['content']

            controll = {
                'is_controlled': common.parseDOM(xml, 'languages', ret = 'IsParentControlled')[0],
                'is_password'  : common.parseDOM(xml, 'languages', ret = 'IsParentPasswordEntered')[0],
            }
            transmission = {
                'name': common.parseDOM(xml, 'transmission', ret = 'name'),
                'url' : common.parseDOM(xml, 'transmission', ret = 'url'),
            }
            
            url = transmission['url'][0]
            for l in range(0, len(transmission['name'])):
                if(transmission['name'][l] == ontvkg_lang):
                    url = transmission['url'][l]
            
            return url
    except: pass
    return ''