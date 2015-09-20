#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json, traceback

from _header import *

BASE_URL = 'http://www.ts.kg/'
BASE_NAME = 'TS.KG'
BASE_LABEL = 'ts'
SETT_DAYS = plugin.get_setting('tskg_news_count', int)
GA_CODE = 'UA-337170-16'
NK_CODE = '991'


@plugin.cached(TTL=60 * 24)
def get_search_shows_list():
    search_data = common.fetchPage({
        'link': BASE_URL + 'show/search/data.json'
    })
    try:
        if search_data['status'] == 200:
            return json.loads(search_data['content'])
    except:
        return json.loads('{}')


@plugin.route('/site/' + BASE_LABEL)
def ts_index():
    item_list = get_categories(BASE_URL + 'show')
    items = []

    if item_list:
        items = [{
                     'label': item['title'],
                     'path': plugin.url_for('ts_tvshows', category_id=item['category']),
                     'icon': item['icon'],
                     'properties': {'fanart_image': item['fanart']},
                 } for item in item_list]

        items = [{
                     'label': set_color('[ Поиск ]', 'dialog', True),
                     'path': plugin.url_for('ts_search'),
                     'icon': get_local_icon('find'),
                     'properties': {'fanart_image': item_list[0]['fanart']},
                 }, {
                     'label': set_color('Последние поступления', 'light', True),
                     'path': plugin.url_for('ts_lastadded', category='last'),
                     'properties': {'fanart_image': item_list[0]['fanart']},
                 }] + items
    else:
        plugin.notify('Сервер недоступен', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))

    return items


@plugin.route('/site/' + BASE_LABEL + '/search')
def ts_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if (search_val):
        item_list = get_search(search_val)

        items = [{
                     'label': item['title'],
                     'path': plugin.url_for('ts_seasons', category_id=item['category_id'], name=item['name'],
                                            title=item['label']),
                     'icon': BASE_URL + 'posters/' + item['name'] + '.jpg',
                 } for item in item_list]

        return items
    else:
        plugin.redirect('plugin://' + plugin.id + '/site/' + BASE_LABEL)


@plugin.route('/site/' + BASE_LABEL + '/last')
def ts_lastadded():
    item_list = get_lastadded(BASE_URL)

    items = [{
                 'label': item['title'],
                 'path': plugin.url_for('ts_seasons', category_id=item['category_id'], name=item['name'],
                                        title=to_utf8(item['label'])) if (not item['is_playable']) else item['url'],
                 'icon': BASE_URL + 'posters/' + item['name'] + '.jpg',
                 'info': item['info'],
                 'is_playable': item['is_playable']
             } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/<category_id>')
def ts_tvshows(category_id):
    item_list = get_tvshows(BASE_URL + 'show?category=' + category_id + '&genre=0&star=0&sort=a')

    items = [{
                 'label': item['title'],
                 'path': plugin.url_for('ts_seasons', category_id=category_id, name=item['name'],
                                        title=to_utf8(item['title'])),
                 'icon': item['icon'],
                 'properties': item['properties'],
             } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/<category_id>/<name>')
def ts_seasons(category_id, name):
    title = plugin.request.args['title'][0]
    item_list = get_seasons(BASE_URL + 'show/' + name, title)
    items = [{
                 'label': item['title'],
                 'path': plugin.url_for('ts_season', category_id=category_id, name=name, season=item['season'],
                                        title=title),
                 'icon': BASE_URL + 'posters/' + name + '.jpg',
                 'is_not_folder': True,
             } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/<category_id>/<name>/<season>')
def ts_season(category_id, name, season):
    plugin.notify('Пожалуйста, подождите', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))
    item_list = get_videos_by_season(BASE_URL + 'show/' + name, plugin.request.args['title'][0], season)
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')


# method
def get_lastadded(url):
    items = []
    try:
        result = common.fetchPage({'link': url})
        kg_stats(url, GA_CODE, NK_CODE)

        if result['status'] == 200:
            html = result['content']

            news_table = common.parseDOM(html, 'div', attrs={'class': 'col-xs-4'})
            days = 0
            day_title = common.parseDOM(news_table, 'h3')

            for i in range(0, SETT_DAYS + 1):
                links_by_day = re.compile('<h3>' + day_title[i] + '(.+?)<h3>\d').findall(str(news_table))
                div_news = common.parseDOM(links_by_day[0], 'div', attrs={'class': 'clearfix news'})

                for item in div_news:
                    try:
                        title = common.parseDOM(item, 'a')
                        href = common.parseDOM(item, 'a', ret='href')

                        badge = common.parseDOM(item, 'span', attrs={'class': 'label label-success'})
                        if badge:
                            badge = '&emsp;[B][COLOR green]' + badge[0].decode('unicode-escape') + '[/COLOR][/B]'
                        else:
                            badge = ''

                        route = get_url_route(href[0])

                        try:
                            if ( href[0].split('.')[0].find('news') > -1 ):
                                continue;
                        except:
                            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

                        play_url = ''
                        info = {}
                        is_playable = len(route[-1].split('-')) > 2

                        if is_playable:
                            try:
                                episode_html = common.fetchPage({'link': BASE_URL[:-1] + href[0]})
                            except:
                                episode_html = common.fetchPage({'link': href[0]})
                            if episode_html['status'] == 200:
                                ep_html = episode_html['content']
                                ep_id = common.parseDOM(ep_html, 'input', attrs={'id': 'episode_id_input'}, ret='value')
                                ep_json = getEpisode(ep_id[0])

                                temp = ep_json['file']['url']# if ep_json['file']['is_hls'] else ep_json['file']['mp4']
                                play_url = temp + UserAgent
                                info = {
                                    'duration': ep_json['duration'] / 60  # seconds to minutes
                                }

                        label = common.replaceHTMLCodes(
                            day_title[i][0:5] + '&emsp;' + title[0].decode('unicode-escape') + badge)
                        label2 = common.replaceHTMLCodes(title[0].decode('unicode-escape'))

                        items.append({'title': label, 'icon': '', 'is_playable': is_playable,
                                      'url': play_url if (is_playable) else href[0], 'name': route[0],
                                      'category_id': '0', 'label': label2, 'info': info})

                    except:
                        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items


# method
def get_categories(url):
    items = []
    kg_stats(url, GA_CODE, NK_CODE)
    try:
        result = common.fetchPage({
            'link': url,
            'headers': [
                ('Content-Type', 'text/html; charset=UTF-8'),
                ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36')
            ],
        })

        branding = ''

        if result['status'] == 200:
            html = result['content']

            categories = common.parseDOM(html, 'select', attrs={'id': 'filter-category'})
            options = common.parseDOM(categories, 'option')
            options_id = common.parseDOM(categories, 'option', ret='value')
            for i in range(0, len(options)):
                if (options_id[i] != '0'):
                    title = options[i]
                    href = 'show/?category=' + options_id[i] + '&amp;sort=a'
                    icon = ''
                    category = ''

                    items.append({'title': title, 'category': options_id[i], 'icon': icon, 'fanart': branding})
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items


#method
def get_tvshows(url):
    items = []

    def get_shows_by_pagination(page):
        try:
            result = common.fetchPage({'link': url + '&page=' + str(page),
                                       'headers': [
                                           ('Content-Type', 'text/html; charset=UTF-8'),
                                           ('User-Agent',
                                            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'),
                                       ]})
            kg_stats(url, GA_CODE, NK_CODE)

            if result['status'] == 200:
                html = result['content']

                container = common.parseDOM(html, 'div', attrs={'id': 'shows'})
                shows = common.parseDOM(container, 'div', attrs={'class': 'show'})
                for item in shows:
                    title = common.parseDOM(item, 'p', attrs={'class': 'show-title'})
                    href = common.parseDOM(item, 'a', ret='href')
                    icon = common.parseDOM(item, 'img', ret='src')
                    name = get_url_route(href[0])[0]
                    properties = {
                        'PlotOutline': '',
                        'Plot': '',
                    }

                    items.append({
                        'title': title[0],
                        'name': name,
                        'icon': BASE_URL[:-1] + icon[0],
                        'properties': properties
                    })

                pagination = common.parseDOM(html, 'ul', attrs={'class': 'pagination hidden'})
                li = common.parseDOM(pagination, 'li', attrs={'class': 'next'})

                if (li):
                    get_shows_by_pagination(page + 1)
        except:
            xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    get_shows_by_pagination(1)

    return items


#method
def get_seasons(url, title):
    items = []
    url_prefix = ''
    try:
        result = common.fetchPage({'link': url})
        kg_stats(url, GA_CODE, NK_CODE)

        if result['status'] == 200:
            html = result['content']

            sections = common.parseDOM(html, 'section')
            for item in sections:
                season_number = common.parseDOM(item, 'h3')

                label = common.replaceHTMLCodes(title.decode('utf-8') + ' &emsp; ' + season_number[0])
                items.append({'title': label, 'url': url, 'icon': '', 'season': season_number[0][6:]})
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items


#method
def get_videos_by_season(url, title, season):
    items = []
    season = int(season)
    
    try:
        result = common.fetchPage({'link': url+'-'+str(season)+'-1',
                                   'headers': [
                                       ('Content-Type', 'text/html; charset=UTF-8'),
                                       ('User-Agent',
                                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36'),
                                   ]})
        kg_stats(url, GA_CODE, NK_CODE)

        if result['status'] == 200:
            html = result['content']
            down = common.parseDOM(html, 'a', {'id': 'download-button'}, ret='href')[0]
            down = down.split('/');
            down = down[len(down)-1];
            result = common.fetchPage({'link': BASE_URL + 'show/episode/nav.json?episode=' + down,
                                   'headers': [
                                       ('X-Requested-With', 'XMLHttpRequest'),
                                       ('Content-Type', 'text/html; charset=UTF-8'),
                                       ('User-Agent',
                                        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'),
                                   ]})
            data = json.loads(result['content'])

            for item in data:
                s_num_e_num = 's' + str(season) + 'e' + item['title']

                label = common.replaceHTMLCodes(title.decode('utf-8') + ' &emsp; ' + s_num_e_num )

                if 'fullname' in item:
                    label = label + common.replaceHTMLCodes('&emsp;' + item['fullname'].decode('utf-8'))
                elif 'name' in item and item['name']:
                    label = label + common.replaceHTMLCodes('&emsp;' + item['name'].decode('utf-8'))
                
                icon = ''
                ep_json = getEpisode(item['id'])
                temp = ep_json['file']['url']# if ep_json['file']['is_hls'] else ep_json['file']['mp4']
                href = temp
                items.append({'title': label, 'url': href, 'icon': icon})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_search(search_value):
    items = []
    try:
        search_data = get_search_shows_list()

        if search_data:
            for data in search_data:
                _key = data['title'].encode('utf-8')
                _url = data['url']
                search_value = search_value.decode('utf-8').lower().encode('utf-8')

                if (search_value in _key.decode('utf-8').lower().encode('utf-8')):
                    route = get_url_route(_url)
                    label = _key
                    a = _key.find(' (')
                    label2 = _key if (a < 0) else _key[:a]

                    items.append({'title': label, 'icon': '', 'url': _url, 'name': route[0], 'category_id': '0',
                                  'label': label2})
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items


def getEpisode(id):
    result = common.fetchPage({
        'link': BASE_URL + 'show/episode/episode.json?episode='+str(id),
        'headers': [
            ('X-Requested-With', 'XMLHttpRequest')
        ]
    })
    if result['status'] == 200:
        return json.loads(result['content'])
