#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib, json, traceback
from _header import *

ontvkg_logn = plugin.get_setting('ontvkg_logn', str)
ontvkg_pass = plugin.get_setting('ontvkg_pass', str)
ontvkg_ppin = plugin.get_setting('ontvkg_ppin', str)
ontvkg_lang = plugin.get_setting('ontvkg_lang', str)

BASE_NAME     = 'Online TV'
BASE_LABEL    = 'ontvkg'

OTV_URL = 'http://www.onlinetv.kg/';
STB_API_URL = OTV_URL + 'STBService/';
XML_API_URL = OTV_URL + 'XMLService/';
COOKIES = False;

def get_ontvkg_cookie():
    result = False
    cookies = plugin.get_storage(BASE_LABEL, TTL = 360)

    try:
        result = cookies['auth']

    except:
        r = common.fetchPage({
            'link': XML_API_URL + 'Login/' + urllib.quote_plus(ontvkg_logn) + '/' + urllib.quote_plus(ontvkg_pass) + '/true',
        })

        if r['status'] == 200:
            for h in r['header']:
                if h.find('Set-Cookie') > -1:
                    result = h.replace('Set-Cookie: ', '').replace(' HttpOnly', '')
                    cookies['auth'] = result
                    cookies.sync()

    return result


@plugin.route('/site/' + BASE_LABEL)
def ontvkg_index():
    items = []
    COOKIES = get_ontvkg_cookie()
    if not COOKIES:
        plugin.notify('Ошибка авторизации', 'OnlineTV.kg', image=get_local_icon('noty_' + BASE_LABEL))
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
    COOKIES = get_ontvkg_cookie()
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 360)
        return cache['channels']
    except:
        plugin.notify('Пожалуйста, подождите...', 'OnlineTV.kg', 2000, get_local_icon('noty_' + BASE_LABEL))

    try:
        r = common.fetchPage({
            'link': XML_API_URL + 'Groups',
            'cookie': COOKIES
        })

        if r['status'] == 200:
            xml = r['content']
            tag = 'group'
            categories = {
                'id'  : common.parseDOM(xml, tag, ret = 'id'),
                'name': common.parseDOM(xml, tag, ret = 'name'),
            }

            for i in range(0, len(categories['id'])):
                r = common.fetchPage({
                    'link': XML_API_URL + 'GroupChannels/' + categories['id'][i],
                    'cookie': COOKIES
                })

                if r['status'] == 200:
                    xml = r['content']
                    tag = 'channel'
                    data = {
                        'id'           : common.parseDOM(xml, tag, ret = 'id'),
                        'channelNumber': common.parseDOM(xml, tag, ret = 'channelNumber'),
                        'name'         : common.parseDOM(xml, tag, ret = 'name'),
                        'tId'          : common.parseDOM(xml, tag, ret = 'tId'),
                        'tName'        : common.parseDOM(xml, tag, ret = 'tName'),
                        'tDescription' : common.parseDOM(xml, tag, ret = 'tDescription'),
                    }

                    for j in range(0, len(data['id'])):
                        title = common.replaceHTMLCodes( '[' + categories['name'][i] + ']&emsp;' + set_color(data['name'][j], 'bold') )


                        r = common.fetchPage({
                            'link': XML_API_URL + 'LanguagesByChannelId/' + data['id'][j],
                            'cookie':COOKIES
                        })

                        if r['status'] == 200:
                            xml = r['content']
                            tag = 'transmission'
                            transmissions = {
                                'name': common.parseDOM(xml, tag, ret = 'name'),
                                'url' : common.parseDOM(xml, tag, ret = 'url'),
                            }

                            url = transmissions['url'][0]
                            for l in range(0, len(transmissions['name'])):
                                if(transmissions['name'][l] == ontvkg_lang):
                                    url = transmissions['url'][l]

                        items.append({
                            'title': title,
                            'url': url,
                            'icon': get_local_icon('onlinetv/'+data['id'][j])
                        })

                        cache['channels'] = items
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_genres():
    items = []
    COOKIES = get_ontvkg_cookie()
    try:
        cache = plugin.get_storage(BASE_LABEL, TTL = 360)
        return cache['genres']

    except:
        try:
            r = common.fetchPage({
                'link': XML_API_URL + 'Genres',
                'cookie':COOKIES
            })

            if r['status'] == 200:
                xml = r['content']
                tag = 'genre'
                data = {
                    'id'                : common.parseDOM(xml, tag, ret = 'id'),
                    'name'              : common.parseDOM(xml, tag, ret = 'name'),
                    'IsParentControlled': common.parseDOM(xml, tag, ret = 'IsParentControlled'),
                }
                for i in range(0, len(data['id'])):
                    items.append({
                        'label': data['name'][i],
                        'id': data['id'][i],
                        'icon': ''
                    })

                cache['genres'] = items
        except:
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_shows_by_genre(id, page, type = 'genre'):
    items = []
    pagination_items = []
    COOKIES = get_ontvkg_cookie()

    try:
        if type == 'genre':
            link = 'TransmissionsByGenreId/' + str(int(id)) + '/' + str(int(page)) + '/24'
        else:
            link = 'TransmissionsSearch/' + urllib.quote(str(id)) + '/' + str(int(page)) + '/24'

        r = common.fetchPage({
            'link': XML_API_URL + link,
            'cookie': COOKIES
        })

        if r['status'] == 200:
            xml = r['content']

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
            except:
                xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
            #======== END pagination ========#

            tag = 'transmission'
            data = {
                'id'     : common.parseDOM(xml, tag, ret = 'id'),
                'name'   : common.parseDOM(xml, tag, ret = 'name'),
                'date'   : common.parseDOM(xml, tag, ret = 'date'),
                'time_h' : common.parseDOM(xml, tag, ret = 'hour'),
                'time_m' : common.parseDOM(xml, tag, ret = 'minute'),
                'trCount': common.parseDOM(xml, tag, ret = 'transmissionsCount'),
            }
            for i in range(0, len(data['id'])):
                try:
                    date  = data['date'][i] + ' ' + data['time_h'][i] + ':' + data['time_m'][i]
                    label = common.replaceHTMLCodes( date + '&emsp;' + data['name'][i] )
                except:
                    label = common.replaceHTMLCodes( data['name'][i] )

                items.append({
                    'label': label,
                    'id':    data['id'][i],
                    'icon':  '',
                    'is_playable': True if data['trCount'][i] == '1' else False
                })
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {
        'items': items,
        'pagination': pagination_items
    }


#method
def get_transmission_group(genre_id, id):
    print XML_API_URL + 'TransmissionsByGenreGroupedTransmissionId/' + str(int(genre_id)) + '/' + str(int(id)) + '/1/100'
    items = []
    COOKIES = get_ontvkg_cookie()

    try:
        r = common.fetchPage({
            'link': XML_API_URL + 'TransmissionsByGenreGroupedTransmissionId/' + str(int(genre_id)) + '/' + str(int(id)) + '/1/100',
            'cookie':COOKIES
        })

        if r['status'] == 200:
            xml = r['content']
            tag = 'transmission'
            data = {
                'id'    : common.parseDOM(xml, tag, ret = 'id'),
                'name'  : common.parseDOM(xml, tag, ret = 'name'),
                'desc'  : common.parseDOM(xml, tag, ret = 'description'),
                'date'  : common.parseDOM(xml, tag, ret = 'date'),
                'time_h': common.parseDOM(xml, tag, ret = 'hour'),
                'time_m': common.parseDOM(xml, tag, ret = 'minute'),
            }

            for i in range(0, len(data['id'])):
                date  = data['date'][i] + ' ' + data['time_h'][i] + ':' + data['time_m'][i]
                label = common.replaceHTMLCodes( date + '&emsp;' + data['name'][i].title() + ': ' + data['desc'][i].title() )
                id    = data['id'][i]

                items.append({
                    'title': label,
                    'url':   get_transmission_url(id),
                    'icon':  ''
                })
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_transmission_url(id):
    COOKIES = get_ontvkg_cookie()

    try:
        r = common.fetchPage({
            'link': XML_API_URL + 'LanguagesByTransmissionId/' + str(int(id)),
            'cookie': COOKIES
        })

        if r['status'] == 200:
            xml = r['content']

            controll = {
                'is_controlled': common.parseDOM(xml, 'languages', ret = 'IsParentControlled')[0],
                'is_password'  : common.parseDOM(xml, 'languages', ret = 'IsParentPasswordEntered')[0],
            }
            transmission = {
                'name': common.parseDOM(xml, 'transmission', ret = 'name'),
                'url' : common.parseDOM(xml, 'transmission', ret = 'url'),
            }

            url = transmission['url'][0]

            for i in range(0, len(transmission['name'])):
                if(transmission['name'][i] == ontvkg_lang):
                    url = transmission['url'][i]

            return url
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return ''