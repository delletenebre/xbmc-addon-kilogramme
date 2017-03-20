# -*- coding: utf-8 -*-
import App
from App import P
import traceback
import simplejson as json
import urllib
import xbmc


URL = 'http://www.onair.kg'
API = URL + '/api/'


@P.action()
def oa_index(params):
    return [{
        'label': '[ Поиск ]',
        'icon': App.get_media('find'),
        'url': P.get_url(action='oa_search')
    }, {
        'label': App.format_bold('Популярное'),
        'url': P.get_url(action='oa_popular')
    }, {
        'label': 'Все фильмы',
        'url': P.get_url(action='oa_items', type='movies')
    }, {
        'label': 'Фильмы по жанрам',
        'url': P.get_url(action='oa_items', type='movies', condition='genres')
    }, {
        'label': 'Фильмы по стране',
        'url': P.get_url(action='oa_items', type='movies', condition='countries')
    }, {
        'label': 'Все сериалы',
        'url': P.get_url(action='oa_items', type='serials')
    }, {
        'label': 'Сериалы по жанрам',
        'url': P.get_url(action='oa_items', type='serials', condition='genres')
    }, {
        'label': 'Сериалы по стране',
        'url': P.get_url(action='oa_items', type='serials', condition='countries')
    }]


@P.action()
def oa_search(params):
    items = []

    query = App.keyboard(heading='Поиск')
    if query is not None and query != '':
        content = App.http_request(API + '/films/search?' + urllib.urlencode({'title': query}))
        if content:
            data = json.loads(content)
            for item in data:
                plot = App.format_description(
                    item['Countries'].encode('utf-8'),
                    item['Genres'].encode('utf-8'),
                    item['Description'].encode('utf-8')
                )

                label = App.format_bold(item['Title'])

                url = ''
                if item['Type'] == 'Movie':
                    content = App.http_request('%s/movies/%s' % (API, item['Id']))
                    if content:
                        movie = json.loads(content)
                        url = movie['VideoFile']
                    else:
                        continue
                else:
                    url = P.get_url(action='oa_seasons', id=item['Id'], title=item['Title'].encode('utf-8'))
                    label = App.replace_html_codes('%s&emsp;сериал'.decode('utf-8') % label)

                items.append({
                    'label': label,
                    'thumb': item['PosterFile'],
                    'art': {
                        'poster': item['PosterFile']
                    },
                    'info': {
                        'video': {
                            'plot': plot,
                            'year': item['ReleaseYear'],
                        }
                    },
                    'url': url,
                    'is_playable': item['Type'] == 'Movie'
                })
            if len(items) == 0:
                App.noty('no_search_results')
    else:
        App.noty('no_search_results')

    return App.create_listing(items)


@P.action()
@P.cached(360)
def oa_popular(params):
    items = []

    content = App.http_request('%s/films/popular' % API)
    if content:
        data = json.loads(content)
        for item in data:
            plot = App.format_description(
                item['Countries'].encode('utf-8'),
                item['Genres'].encode('utf-8'),
                item['Description'].encode('utf-8')
            )

            label = App.format_bold(item['Title'])

            url = ''
            if item['Type'] == 'Movie':
                content = App.http_request('%s/movies/%s' % (API, item['Id']))
                if content:
                    movie = json.loads(content)
                    url = movie['VideoFile']
                else:
                    continue
            else:
                url = P.get_url(action='oa_seasons', id=item['Id'], title=item['Title'].encode('utf-8'))
                label = App.replace_html_codes('%s&emsp;сериал'.decode('utf-8') % label)

            items.append({
                'label': label,
                'thumb': item['PosterFile'],
                'art': {
                    'poster': item['PosterFile']
                },
                'info': {
                    'video': {
                        'plot': plot,
                        'year': item['ReleaseYear'],
                    }
                },
                'url': url,
                'is_playable': item['Type'] == 'Movie'
            })

    return App.create_listing(items)


@P.action()
@P.cached(360)
def oa_items(params):
    items = []

    url = '%s/%s' % (API, params.type)

    if 'condition' in params and params.condition != '':
        url = '%s/%s' % (url, params.condition)
    else:
        params.condition = ''

    if 'id' in params and params.id != '':
        url = '%s/%s' % (url, params.id)
    else:
        params.id = ''

    content = App.http_request(url)
    if content:
        data = json.loads(content)
        for item in data:
            if 'Name' in item:
                label = item['Name'] if item['Name'] != '-' else 'Без категории'
                url = P.get_url(action='oa_items', type=params.type, condition=params.condition, id=item['Id'])

                if params.id != '' and params.type == 'serials':
                    # Скорее всего список сериалов
                    url = P.get_url(action='oa_seasons', id=item['Id'], title=label.encode('utf-8'))

                items.append({
                    'label': App.replace_html_codes(label),
                    'url': url
                })
            else:
                # Скорее всего это фильм
                label = item['Title']
                plot = App.format_description(
                    item['Countries'].encode('utf-8'),
                    item['Genres'].encode('utf-8'),
                    item['Description'].encode('utf-8')
                )
                items.append({
                    'label': item['Title'],
                    'thumb': item['PosterFile'],
                    'art': {
                        'poster': item['PosterFile']
                    },
                    'info': {
                        'video': {
                            'plot': plot,
                            'year': item['ReleaseYear'],
                        }
                    },
                    'url': item['VideoFile'],
                    'is_playable': True
                })

    return App.create_listing(items)


@P.action()
@P.cached(360)
def oa_seasons(params):
    items = []

    content = App.http_request('%s/serials/%s/seasons' % (API, params.id))
    if content:
        data = json.loads(content)
        seasons_ids = []
        for item in data:
            seasons_ids.append(str(item['Id']))
            items.append({
                'label': item['Name'],
                'url': P.get_url(action='oa_episodes', id=item['Id'], title=params.title, season=item['Name'][6:]),
                'is_folder': False
            })
        if len(items) > 0:
            items.insert(0, {
                'label': App.replace_html_codes('[B]%s[/B]&emsp;Все сезоны'.decode('utf-8') % params.title.decode('utf-8')),
                'url': P.get_url(action='oa_episodes', id=','.join(seasons_ids), title=params.title),
                'is_folder': False
            })

    return App.create_listing(items)


@P.action()
def oa_episodes(params):
    items = []

    xbmc.executebuiltin('ActivateWindow(busydialog)')

    try:
        i = 0
        for id in params.id.split(','):
            i += 1
            content = App.http_request('%s/seasons/%s/episodes' % (API, id))
            if content:
                data = json.loads(content)
                season = params.season if 'season' in params else str(i)

                for episode in data:
                    items.append(
                        {
                            'label': App.replace_html_codes('%s&emsp;s%se%s&emsp;[B]%s[/B]' % (params.title.decode('utf-8'), season, episode['Number'], episode['Title'])),
                            'info': {
                                'video': {
                                    'plot': episode['Description'],
                                    'duration': str2sec(episode['Duration'])
                                }
                            },
                            'url': episode['VideoFile'],
                            'is_playable': True
                        }
                    )
    except:
        P.log_error(traceback.format_exc())
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    if len(items) > 0:
        App.create_playlist(items)
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')
    else:
        App.noty('playlist_empty')


def str2sec(t):
    time = t.split(':')
    return int(time[2]) + (int(time[1]) * 60) + (int(time[0]) * 60 * 60)
