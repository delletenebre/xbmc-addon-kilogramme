# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
import urllib
import simplejson as json
import re
import xbmc
import traceback


URL = 'http://namba.kg/serials/'
API = 'http://namba.kg/api'


@P.cached(1440)
@P.action()
def ns_index(params):
    items = [{
        'label': '[ Поиск ]',
        'icon': App.get_media('find'),
        'url': P.get_url(action='ns_search')
    }, {
        'label': App.format_bold('Популярные'),
        'url': P.get_url(action='ns_top')
    }, {
        'label': App.format_bold('Новые серии'),
        'url': P.get_url(action='ns_new_episodes')
    }, {
        'label': App.format_bold('Новые сериалы'),
        'url': P.get_url(action='ns_new_serials')
    }]

    content = App.http_request(URL)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_='categories-menu')
        if block is not None:
            for genre in block.find_all('a'):
                label = App.bs_get_text(genre)
                url = genre.get('href').split('=')
                url[1] = urllib.quote(url[1].encode('utf-8'))
                url = '='.join(url)

                items.append({
                    'label': label,
                    'url': P.get_url(action='ns_serials_by_genre', url=url)
                })
    return items


@P.action()
def ns_search(params):
    items = []
    query = App.keyboard(heading='Поиск')
    if query is None:
        pass
    elif query != '':
        query = query.decode('utf-8').lower()
        serials = get_serials_list()
        for serial in serials:
            if serial['title'].lower().find(query) > -1:
                cover = serial['cover']

                items.append({
                    'label': serial['title'],
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'url': P.get_url(action='ns_serial_seasons', url=serial['url'])
                })
        if len(items) == 0:
            App.noty('no_search_results')
    else:
        App.noty('no_search_results')

    return App.create_listing(items, content='tvshows')


@P.cached(720)
@P.action()
def ns_top(params):
    return get_serials_from_index_page('charts-result-block')


@P.cached(120)
@P.action()
def ns_new_episodes(params):
    return get_serials_from_index_page('new-episode-serials')


@P.cached(720)
@P.action()
def ns_new_serials(params):
    return get_serials_from_index_page('last-serials')


@P.cached(1440)
@P.action()
def ns_serials_by_genre(params):
    items = []
    P.log_error(params.url)
    content = App.http_request(URL + params.url)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_='serials-list')
        for serial in block.find_all('li'):
            link = serial.find('a')
            img = link.find('img')

            url = link.get('href')
            cover = img.get('src')
            label = img.get('title').strip()

            items.append({
                'label': label,
                'thumb': cover,
                'art': {
                    'poster': cover
                },
                'url': P.get_url(action='ns_serial_seasons', url=url)
            })

    return App.create_listing(items, content='tvshows')


@P.cached(1440)
@P.action()
def ns_serial_seasons(params):
    items = []

    content = App.http_request(URL + params.url)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        name = App.bs_get_text(html.find('h1')).strip()
        description = html.find(class_='serial-description')
        year = ''
        plot = App.STR_NO_DATA
        cover = ''
        if description is not None:
            cover = description.find('img').get('src')
            description_text = App.bs_get_text(description.find(class_='text')).encode('utf-8')

            year = re_compile_or_no_data('Год(.+?)\n', description_text)
            country = re_compile_or_no_data('Страна(.+?)\n', description_text)
            if country == App.STR_NO_DATA:
                country = re_compile_or_no_data('Производство(.+?)\n', description_text)
            genre = re_compile_or_no_data('Жанр(.+?)\n', description_text)
            director = re_compile_or_no_data('Режиссер(.+?)\n', description_text)
            plot = re_compile_or_no_data('\n(.+?)\n      \n', description_text)
            plot = App.format_description(description=plot, country=country, genre=genre, director=director)

        season_headers = html.find_all(class_='panel-title')

        items.append({
            'label': App.replace_html_codes('%s&emsp;Все сезоны'.decode('utf-8') % App.format_bold(name)),
            'thumb': cover,
            'art': {
                'poster': cover
            },
            'info': {
                'video': {
                    'plot': plot,
                    'year': year
                }
            },
            'url': P.get_url(action='ns_serial_season_episodes', url=params.url, season_number='-1')
        })

        for season_header in season_headers:
            label = App.bs_get_text(season_header.find('h2'))
            season_number = label.split(' ')[1]

            items.append({
                'label': label,
                'thumb': cover,
                'art': {
                    'poster': cover
                },
                'url': P.get_url(action='ns_serial_season_episodes', url=params.url, season_number=season_number)
            })

    return App.create_listing(items, content='tvshows')


@P.action()
def ns_serial_season_episodes(params):
    items = []

    xbmc.executebuiltin('ActivateWindow(busydialog)')

    content = App.http_request(URL + params.url)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        serial_name = App.bs_get_text(html.find('h1')).strip()
        season_headers = html.find_all(class_='panel-title')

        for season_header in season_headers:
            try:
                season_name = App.bs_get_text(season_header.find('h2'))
                season_number = season_name.split(' ')[1]
                if params.season_number == '-1' or params.season_number == season_number:
                    episodes_block = season_header.parent.find(class_='videos-pane')
                    for episode in episodes_block.find_all('li'):
                        try:
                            link = episode.find('a').get('href')
                            cover = episode.find('img').get('src')
                            episode_number = App.bs_get_text(episode.find(class_='grey')).split(' ')[0]
                            label = App.replace_html_codes('%s&emsp;%sx%s' % (serial_name, season_number, episode_number))

                            items.append(create_movie_item(link, label, cover))
                        except:
                            P.log_error(traceback.format_exc())
            except:
                P.log_error(traceback.format_exc())

    xbmc.executebuiltin('Dialog.Close(busydialog)')

    if len(items) > 0:
        App.create_playlist(items)
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')
    else:
        App.noty('playlist_empty')


def create_movie_item(episode_url, label, cover):
    item = {}

    content = App.http_request(URL + episode_url)
    if content:
        video_id = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(content)[0]
        content = App.http_request('%s/?%s' % (API, urllib.urlencode({
            'service': 'video',
            'action': 'video',
            'id': video_id
        })))
        if content:
            movie = json.loads(content)['video']

            item = {
                'label': label,
                'thumb': cover,
                'art': {
                    'poster': cover
                },
                'stream_info': {
                    'video': {
                        'duration': App.timestring2seconds(movie['duration'])
                    }
                },
                'info': {
                    'video': {
                        'plot': '' if App.get_skin_name() == 'skin.confluence' else movie['raw_description']
                    }
                },
                'url': movie['download']['flv'],
                'is_playable': True,
            }
    return item


def get_serials_from_index_page(block_class):
    items = []

    content = App.http_request(URL)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_=block_class)
        if block is not None:
            for serial in block.find_all('li'):
                link = serial.find('a')
                img = link.find('img')

                url = link.get('href')
                cover = img.get('src')
                label = img.get('title')

                items.append({
                    'label': label,
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'url': P.get_url(action='ns_serial_seasons', url=url)
                })
    return App.create_listing(items, content='tvshows')


def re_compile_or_no_data(regular_expression, text):
    result = re.compile(regular_expression).findall(text)
    if len(result) > 0:
        result = result[0].replace(':', '')
        if result.find('выпуска') == 0:
            result.replace('выпуска', '')
        if result.find('ы') == 0:
            result = result[2:]
        result = result.strip()
    else:
        result = App.STR_NO_DATA
    return result


@P.cached(1440)
def get_serials_list():
    content = App.http_request(URL)
    if content:
        result = re.compile('var list_all_serial = (.+?)}];').findall(content)
        if len(result) > 0:
            return json.loads(result[0] + '}]')
