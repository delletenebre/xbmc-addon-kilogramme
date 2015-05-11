#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json, time, xbmc, traceback
from _header import *

BASE_URL = 'http://cinemaonline.kg/'
BASE_NAME = 'Cinema Online'
BASE_LABEL = 'oc'
GA_CODE = 'UA-34889597-1'
NK_CODE = '1744'


def default_oc_noty():
    plugin.notify('Сервер недоступен', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))


def get_oc_cookie():
    result = {'phpsessid': '', 'utmp': '', 'set': ''}
    cookie = plugin.get_storage(BASE_LABEL, TTL=1440)

    try:
        result['phpsessid'] = cookie['phpsessid']
        result['utmp'] = cookie['utmp']
        result['set'] = cookie['set']
    except:
        try:
            a = common.fetchPage({'link': BASE_URL})
            b = common.fetchPage({'link': BASE_URL + 'cinema.png?' + str(int(time.time()))})

            cookie['set'] = a['header']['Set-Cookie'] + '; ' + b['header']['Set-Cookie']
            result['set'] = cookie['set']

            cookies = common.getCookieInfoAsHTML()
            cookie['phpsessid'] = common.parseDOM(cookies, 'cookie', attrs={'name': 'PHPSESSID'}, ret='value')[0]
            try:
                cookie['utmp'] = common.parseDOM(cookies, 'cookie', attrs={'name': '_utmp'}, ret='value')[0]
            except:
                cookie['utmp'] = common.parseDOM(cookies, 'cookie', attrs={'name': '__utmp'}, ret='value')[0]
            result['phpsessid'] = cookie['phpsessid']
            result['utmp'] = cookie['utmp']
        except:
            pass

    return result


COOKIE = ''  # get_oc_cookie()
BASE_API_URL = BASE_URL + 'api.php?format=json'  # &' + COOKIE['phpsessid'] + '&JsHttpRequest='+str(int(time.time()))+'-xml'


@plugin.route('/site/' + BASE_LABEL)
def oc_index():
    items = [{
                 'label': set_color('[ Поиск ]', 'dialog', True),
                 'path': plugin.url_for('oc_search'),
                 'icon': get_local_icon('find')
             }, {
                 'label': set_color('Новинки на CinemaOnline', 'light'),
                 'path': plugin.url_for('oc_category', id=0)
             }, {
                 'label': set_color('По жанрам', 'bold'),
                 'path': plugin.url_for('oc_genres')
             }, {
                 'label': 'Бестселлеры',
                 'path': plugin.url_for('oc_bestsellers')
             }, {
                 'label': 'Лучшие по версии IMDB',
                 'path': plugin.url_for('oc_category', id=2)
             }, {
                 'label': 'Лучшие по версии КиноПоиск',
                 'path': plugin.url_for('oc_category', id=9)
             }]

    return items


@plugin.route('/site/' + BASE_LABEL + '/genre')
def oc_genres():
    item_list = get_genres()

    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_genre', id=item['id'])
             } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/bestsellers')
def oc_bestsellers():
    item_list = get_bestsellers()

    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_movie', id=item['id']),
                 'icon': item['icon'],
             } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/genre/<id>')
def oc_genre(id):
    item_list = get_genre_movie_list(id)

    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_movie', id=item['id']),
                 'properties': item['properties'],
                 'icon': item['icon'],
             } for item in item_list['items']]

    if (item_list['sys_items']):
        items = add_pagination(items, item_list['sys_items'], 'oc_genre_pagination', id)

    return items


@plugin.route('/site/' + BASE_LABEL + '/genre/<id>/<page>')
def oc_genre_pagination(id, page='1'):
    page = int(page)
    item_list = get_genre_movie_list(id, page)
    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_movie', id=item['id']),
                 'properties': item['properties'],
                 'icon': item['icon'],
             } for item in item_list['items']]

    if (item_list['sys_items']):
        items = add_pagination(items, item_list['sys_items'], 'oc_genre_pagination', id)

    return plugin.finish(items, update_listing=True)


@plugin.route('/site/' + BASE_LABEL + '/category/<id>')
def oc_category(id):
    item_list = get_movie_list(id)

    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_movie', id=item['id']),
                 'properties': item['properties'],
                 'icon': item['icon'],
             } for item in item_list['items']]

    if (item_list['sys_items']):
        items = add_pagination(items, item_list['sys_items'], 'oc_category_pagination', id)

    return items


@plugin.route('/site/' + BASE_LABEL + '/category/<id>/<page>')
def oc_category_pagination(id, page='1'):
    page = int(page)
    item_list = get_movie_list(id, page)
    items = [{
                 'label': item['label'],
                 'path': plugin.url_for('oc_movie', id=item['id']),
                 'properties': item['properties'],
                 'icon': item['icon'],
             } for item in item_list['items']]

    if (item_list['sys_items']):
        items = add_pagination(items, item_list['sys_items'], 'oc_category_pagination', id)

    return plugin.finish(items, update_listing=True)


@plugin.route('/site/' + BASE_LABEL + '/to_page/category/<id>/<page>')
def oc_go_to_page(id, page=1):
    search_page = common.getUserInputNumbers('Укажите страницу')
    if (search_page):
        search_page = int(search_page) - 1 if (int(search_page) > 0) else 1
        item_list = get_movie_list(id, search_page)

        items = [{
                     'label': item['label'],
                     'path': plugin.url_for('oc_movie', id=item['id']),
                     'properties': item['properties'],
                     'icon': item['icon'],
                 } for item in item_list['items']]

        if (item_list['sys_items']):
            for item in item_list['sys_items']:
                items.insert(0, {
                    'label': item['label'],
                    'path': plugin.url_for('oc_go_to_page', id=id, page=item['page']) if (
                        item['search'] == True ) else plugin.url_for('oc_category_pagination', id=id,
                                                                     page=item['page']),
                    'icon': item['icon']
                })

        return plugin.finish(items, update_listing=True)
    else:
        plugin.redirect('plugin://' + plugin.id + '/site/' + BASE_LABEL + '/category/' + id + '/' + str(int(page) - 1))


@plugin.route('/site/' + BASE_LABEL + '/movie/<id>')
def oc_movie(id):
    item_list = get_movie(id)
    # xbmc.log('Item list: ' + str(item_list))
    items = [{
                 # 'title'       : item['label'],
                 'label': item['label'],
                 'path': item['url'],
                 'thumbnail': item['icon'],
                 'properties': item['properties'],
                 'is_playable': True
             } for item in item_list['items']]

    if (item_list['playlist']):
        # xbmc.log('Item list play: ' + str(item_list['items']))
        kgontv_playlist(item_list['items'])
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')
    else:
        # xbmc.log('Item play: ' + str(items))
        return items


@plugin.route('/site/' + BASE_LABEL + '/search')
def oc_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if (search_val):
        item_list = get_search_results(str(search_val))

        items = [{
                     'label': item['label'],
                     'path': plugin.url_for('oc_movie', id=item['id']),
                     'icon': item['icon'],
                 } for item in item_list]

        return items
    else:
        plugin.redirect('plugin://' + plugin.id + '/site/' + BASE_LABEL)


# method
def get_bestsellers():
    items = []
    try:
        result = common.fetchPage({'link': BASE_API_URL, 'post_data': {'action[0]': 'Video.getBestsellers'}})
        kg_stats(BASE_URL, GA_CODE, NK_CODE)

        if result['status'] == 200:
            html = result['content']
            data = json.loads(html)
            for item in data['json'][0]['response']['bestsellers']:
                for video in item['movies']:
                    label = video['name'] + ' [' + item['name'] + ']'
                    icon = BASE_URL + video['cover']
                    video_id = video['movie_id']

                    items.append({
                        'label': label,
                        'icon': icon,
                        'id': video_id
                    })
    except:
        default_oc_noty()
    return items


# method
def get_genres():
    items = []
    try:
        result = common.fetchPage({'link': BASE_API_URL, 'post_data': {'action[0]': 'Video.getGenres'}})
        kg_stats(BASE_URL, GA_CODE, NK_CODE)

        if result['status'] == 200:
            html = result['content']
            data = json.loads(html)
            for item in data['json'][0]['response']['genres']:
                items.append({
                    'label': item['name'],
                    'id': item['id']
                })
    except:
        default_oc_noty()
    return items


# method
def get_movie_list(order_id, page='0'):
    sys_items = []
    items = []
    size = 40
    try:
        offset = int(page) * size
        result = common.fetchPage({'link': BASE_API_URL,
                                   'post_data': {'action[0]': 'Video.getCatalog', 'offset[0]': str(offset),
                                                 'size[0]': str(size), 'order[0]': order_id}})

        kg_stats(BASE_URL, GA_CODE, NK_CODE)

        if result['status'] == 200:
            data = json.loads(result['content'])
            data = data['json'][0]['response']

            # ======== pagination ========#
            sys_items = KG_get_pagination((offset / size + 1), total=data['total'], size=size, offset=1)
            # ======== END pagination ========#

            megogo = False
            for item in data['movies']:
                try:
                    try:
                        genres = '&emsp;[' + ', '.join(item['genres'][:3]) + ']'
                    except:
                        genres = ''
                    if 'Megogo' not in item['genres']:
                        imdb = {'rating': '0', 'votes': '0'}
                        kinopoisk = {'rating': '0', 'votes': '0'}
                        if ('rating_imdb_value' in item):
                            imdb = {'rating': item['rating_imdb_value'], 'votes': item['rating_imdb_count']}
                        if ('rating_kinopoisk_value' in item):
                            kinopoisk = {'rating': item['rating_kinopoisk_value'],
                                         'votes': item['rating_kinopoisk_count']}

                        rating = ''
                        if (imdb['rating'] != '0' and kinopoisk['rating'] != '0'):
                            rating = '&emsp;' + imdb['rating'] + ' (' + imdb['votes'] + ') / ' + kinopoisk[
                                'rating'] + ' (' + kinopoisk['votes'] + ')'

                        country = ''
                        if ('countries' in item):
                            country = item['countries'][0]

                        properties = {
                            'Country': country,
                            'PlotOutline': item['description'],
                            'Plot': item['long_description'],
                            'Year': item['year'],
                            'Rating': imdb['rating'],
                            'Votes': imdb['votes']
                        }

                        country = '&emsp;(' + country + ')' if (country) else ''

                        label = common.replaceHTMLCodes('[B]' + item['name'] + '[/B]' + country + genres + rating)
                        icon = BASE_URL + item['cover']
                        video_id = item['movie_id']

                        items.append({
                            'label': label,
                            'icon': icon,
                            'properties': properties,
                            'id': video_id
                        })
                    else:
                        megogo = True
                except:
                    pass
                    # if megogo: plugin.notify('Megogo пропущен', BASE_NAME, 1000, get_local_icon('noty_' + BASE_LABEL))
    except:
        default_oc_noty()
    return {'items': items, 'sys_items': sys_items}


# method
def get_genre_movie_list(genre, page='0'):
    sys_items = []
    items = []
    size = 40
    order_id = 0
    try:
        offset = int(page) * size
        result = common.fetchPage({'link': BASE_API_URL,
                                   'post_data': {'action[0]': 'Video.getCatalog', 'offset[0]': str(offset),
                                                 'size[0]': str(size), 'order[0]': order_id, 'genre[0]': genre}})

        kg_stats(BASE_URL, GA_CODE, NK_CODE)

        if result['status'] == 200:
            data = json.loads(result['content'])
            data = data['json'][0]['response']

            # ======== pagination ========#
            sys_items = KG_get_pagination((offset / size + 1), total=data['total'], size=size, offset=1)
            # ======== END pagination ========#

            megogo = False
            for item in data['movies']:
                try:
                    try:
                        genres = '&emsp;[' + ', '.join(item['genres'][:3]) + ']'
                    except:
                        genres = ''
                    if 'Megogo' not in item['genres']:
                        imdb = {'rating': '0', 'votes': '0'}
                        kinopoisk = {'rating': '0', 'votes': '0'}
                        if ('rating_imdb_value' in item):
                            imdb = {'rating': item['rating_imdb_value'], 'votes': item['rating_imdb_count']}
                        if ('rating_kinopoisk_value' in item):
                            kinopoisk = {'rating': item['rating_kinopoisk_value'],
                                         'votes': item['rating_kinopoisk_count']}

                        rating = ''
                        if (imdb['rating'] != '0' and kinopoisk['rating'] != '0'):
                            rating = '&emsp;' + imdb['rating'] + ' (' + imdb['votes'] + ') / ' + kinopoisk[
                                'rating'] + ' (' + kinopoisk['votes'] + ')'

                        country = ''
                        if ('countries' in item):
                            country = item['countries'][0]

                        properties = {
                            'Country': country,
                            'PlotOutline': item['description'],
                            'Plot': item['long_description'],
                            'Year': item['year'],
                            'Rating': imdb['rating'],
                            'Votes': imdb['votes']
                        }

                        country = '&emsp;(' + country + ')' if (country) else ''

                        label = common.replaceHTMLCodes('[B]' + item['name'] + '[/B]' + country + genres + rating)
                        icon = BASE_URL + item['cover']
                        video_id = item['movie_id']

                        items.append({
                            'label': label,
                            'icon': icon,
                            'properties': properties,
                            'id': video_id
                        })
                    else:
                        megogo = True
                except:
                    pass
                    # if megogo: plugin.notify('Megogo пропущен', BASE_NAME, 1000, get_local_icon('noty_' + BASE_LABEL))
    except:
        default_oc_noty()
    return {'items': items, 'sys_items': sys_items}


# method
def get_search_results(search_value=''):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'suggestion.php?q=' + urllib2.quote(search_value)})

        kg_stats(BASE_URL, GA_CODE, NK_CODE)
        if result['status'] == 200:
            data = json.loads(result['content'])
            data = data['json'][0]['response']
            for item in data['movies']:
                try:
                    label = item['name'] + '&emsp;|&emsp;' + item['international_name'] + '&emsp;(' + item['year'] + ')'
                    icon = BASE_URL + item['cover']
                    video_id = item['movie_id']

                    items.append({
                        'label': common.replaceHTMLCodes(label),
                        'icon': icon,
                        'id': video_id
                    })
                except:
                    pass
    except:
        default_oc_noty()
    return items


# method
def get_movie(id):
    items = []
    try:
        result = common.fetchPage(
            {'link': BASE_API_URL, 'post_data': {'action[0]': 'Video.getMovie', 'movie_id[0]': id}})
        kg_stats(BASE_URL, GA_CODE, NK_CODE)

        if result['status'] == 200:
            data = json.loads(result['content'])
            item = data['json'][0]['response']['movie']

            icon = BASE_URL + item['covers'][0]['original']

            try:
                trailer = item['trailer']

                try:
                    name = trailer['name']
                except:
                    name = 'Трейлер'

                items.append({
                    'title': name,
                    'label': name,
                    'icon': get_local_icon('kinopoisk'),
                    'properties': {'fanart_image': trailer['preview']},
                    'url': trailer['video']
                })
            except:
                pass

            for video in item['files']:
                try:
                    label = item['name'] + ': ' + video['name']
                    url = get_playable_url(video['path']) + UserAgent

                    try:
                        fan = video['frames'][0]
                    except:
                        fan = ''

                    properties = {
                        'duration': video['metainfo']['playtime'],
                        'fanart_image': fan,
                    }
                    items.append({
                        'title': label,
                        'label': set_color('ПРОСМОТР: ', 'bold').decode('utf-8') + label,
                        'icon': icon,
                        'properties': properties,
                        'url': url
                    })
                except:
                    # xbmc.log('Exception : ' + str(traceback.format_exc()))
                    continue

            try:
                for other in item['other_movies']:
                    try:
                        try:
                            fan = BASE_URL + other['cover']
                        except:
                            fan = ''

                        properties = {
                            'fanart_image': fan,
                        }
                        items.append({
                            'title': other['name'],
                            'label': set_color('ЕЩЕ: ', 'bold').decode('utf-8') + other['name'],
                            'icon': fan,
                            'properties': properties,
                            'url': plugin.url_for('oc_movie', id=other['movie_id'])
                        })
                    except:
                        # xbmc.log('Exception : ' + str(traceback.format_exc()))
                        continue
            except:
                # xbmc.log('Exception : ' + str(traceback.format_exc()))
                pass

    except:
        default_oc_noty()

    # xbmc.log('Exit list : ' + str(items))
    return {'items': items, 'playlist': True if (len(items) > 1) else False}


def get_playable_url(url):
    return str(url).replace('/home/video/', 'http://p0.oc.kg:8080/')

