# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
from App import H
import traceback
import urllib
import simplejson as json
import math
import xbmc
import xbmcplugin
import sys


URL = 'http://cinemaonline.kg'
API = URL + '/api.php?format=json'
stars_condition = {
    'count': 1000,
    'ratings': {
        '​‌*': 6.5,
        '​‌**': 7.25,
        '​‌***': 8.25
    }
}


@P.action()
def co_index(params):
    return [{
        'label': '[ Поиск ]',
        'icon': App.get_media('find'),
        'url': P.get_url(action='co_search')
    }, {
        'label': App.format_bold('Новинки'),
        'url': P.get_url(action='co_movies', order_id='0')
    }, {
        'label': 'Популярное',
        'url': P.get_url(action='co_bestsellers')
    }, {
        'label': 'По жанрам',
        'url': P.get_url(action='co_genres')
    }, {
        'label': 'Лучшие по версии IMDB',
        'url': P.get_url(action='co_movies', order_id='2')
    }, {
        'label': 'Лучшие по версии КиноПоиск',
        'url': P.get_url(action='co_movies', order_id='9')
    }]


@P.action()
def co_search(params):
    items = []
    query = App.keyboard(heading='Поиск')
    if query is not None and query != '':
        content = App.http_request(URL + '/suggestion.php?' + urllib.urlencode({'q': query}))
        if content:
            movies = json.loads(content)['json'][0]['response']['movies']
            for movie in movies:
                cover = get_bigger_cover(movie['cover'])

                items.append({
                    'label': movie['name'],
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'info': {
                        'video': {
                            'year': movie['year'],
                        }
                    },
                    'url': P.get_url(action='co_movie', id=movie['movie_id'])
                })
            if len(items) == 0:
                App.noty('no_search_results')
    else:
        App.noty('no_search_results')

    return App.create_listing(items, content='movies')


@P.action()
def co_bestsellers(params):
    items = []

    content = App.http_request(API, 'POST', {'action[0]': 'Video.getBestsellers'})
    if content:
        data = json.loads(content)['json'][0]['response']
        for category in data['bestsellers']:
            for movie in category['movies']:
                cover = get_bigger_cover(movie['cover'])

                items.append({
                    'label': App.replace_html_codes('[B]%s[/B]&emsp;%s' % (movie['name'], category['name'])),
                    'thumb': cover,
                    'fanart': cover,
                    'art': {
                        'poster': cover
                    },
                    'info': {
                        'video': {
                            'year': movie['year'],
                        }
                    },
                    'url': P.get_url(action='co_movie', id=movie['movie_id'])
                })

    return App.create_listing(items, content='movies')


@P.action()
def co_movies(params):
    if 'genre_id' not in params:
        params.genre_id = ''
    params.refresh = 'page' in params

    items = []
    size = 40
    try:
        if params.page == 'search':
            last_page = int(params.last_page) - 1
            page = int(App.keyboard(heading='Перейти на страницу', numeric=True)) - 1
            if page > last_page:
                page = last_page
            if page < 0:
                page = 0
            params.page = str(page)
        else:
            page = int(params.page)
    except:
        page = 0

    offset = page * size

    request_data = sorted([
        ('action[0]', 'Video.getCatalog'),
        ('offset[0]', offset),
        ('size[0]', size),
        ('order[0]', params.order_id),
        ('genre[0]', params.genre_id)
    ])
    content = App.http_request(API, 'POST', request_data)
    if content:
        data = json.loads(content)['json'][0]['response']

        for movie in data['movies']:
            description = get_description(movie)
            id = movie['movie_id']

            cover = get_bigger_cover(movie['cover'])

            label = App.format_bold(movie['name'])
            plot = description

            items.append(
                {
                    'label': label,
                    'thumb': cover,
                    'fanart': cover,
                    'art': {
                        'poster': cover,
                    },
                    'info': {
                        'video': {
                            'plot': plot,
                            'year': movie['year'],
                            'genre': ' / '.join(movie['genres'][:2]) if 'genres' in movie else ''
                        }
                    },
                    'url': P.get_url(action='co_movie', id=id)
                }
            )

        movies_count = int(data['total'])
        add_pagination(
            items,
            get_pagination((offset / size + 1), movies_count, size, 1, params)
        )

        if movies_count > size:
            total_pages = int(math.ceil(movies_count / size + 1))
            items.insert(0, {
                'label': App.replace_html_codes('%s&emsp;%d / %d' % ('[ Перейти на страницу ]'.decode('utf-8'), page + 1, total_pages)),
                'url': P.get_url(action='co_movies', order_id=params.order_id, genre_id=params.genre_id, page='search', last_page=total_pages)
            })

    return App.create_listing(items, content='movies', update_listing=params.refresh)


@P.action()
def co_genres(params):
    items = []

    content = App.http_request(API, 'POST', {'action[0]': 'Video.getGenres'})
    if content:
        data = json.loads(content)['json'][0]['response']['genres']
        for genre in data:
            label = App.replace_html_codes(
                '[B]%s[/B]&emsp;%s' % (genre['name'], genre['count'])
            )
            items.append(
                {
                    'label': label,
                    'url': P.get_url(action='co_movies', order_id='0', genre_id=genre['id'])
                }
            )
    return App.create_listing(items)


@P.action()
def co_movie(params):
    items = []

    request_data = sorted([
        ('action[0]', 'Video.getMovie'),
        ('movie_id[0]', params.id)
    ])
    content = App.http_request(API, 'POST', request_data)
    if content:
        movie = json.loads(content)['json'][0]['response']['movie']

        cover = '{0}/{1}'.format(URL, movie['covers'][0]['thumbnail'])

        for file in movie['files']:
            duration = ''
            url = P.get_url(action='co_movie_playlist', id=movie['movie_id'])

            if file['is_dir']:
                label = App.replace_html_codes(movie['name'] + '&emsp;Плейлист'.decode('utf-8'))
            else:
                label = file['name'] if len(movie['files']) > 1 else movie['name']
                url = file['path'].replace('/home/video/', 'http://p0.oc.kg:8080/')
                duration = file['metainfo']['playtime_seconds']

            items.append(
                {
                    'label': label,
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'stream_info': {
                        'video': {
                            'duration': duration
                        }
                    },
                    'info': {
                        'video': {
                            'plot': get_description(movie),
                            'year': movie['year'],
                            'mpaa': movie['mpaa'],
                            'title': movie['name'],
                            'originaltitle': movie['international_name'],
                        }
                    },
                    'url': url,
                    'is_playable': not(file['is_dir']),
                    'is_folder': not(file['is_dir']),
                }
            )

            if file['is_dir']:
                break

    return App.create_listing(items, content='movies')


@P.action()
def co_movie_playlist(params):
    items = []
    xbmc.executebuiltin('ActivateWindow(busydialog)')

    request_data = sorted([
        ('action[0]', 'Video.getMovie'),
        ('movie_id[0]', params.id)
    ])
    content = App.http_request(API, 'POST', request_data)
    if content:
        movie = json.loads(content)['json'][0]['response']['movie']
        cover = '{0}/{1}'.format(URL, movie['covers'][0]['thumbnail'])
        for file in movie['files']:
            if file['is_dir']:
                continue

            url = file['path'].replace('/home/video/', 'http://p0.oc.kg:8080/')

            items.append(
                {
                    'label': file['name'],
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'stream_info': {
                        'video': {
                            'duration': file['metainfo']['playtime_seconds']
                        }
                    },
                    'info': {
                        'video': {
                            'plot': get_description(movie),
                            'year': movie['year'],
                            'mpaa': movie['mpaa'],
                            'title': '%s: %s' % (movie['name'], file['name']),
                            'originaltitle': movie['international_name'],
                        }
                    },
                    'url': url,
                    'is_playable': True
                }
            )

    xbmc.executebuiltin('Dialog.Close(busydialog)')

    if len(items) > 0:
        App.create_playlist(items)
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')
    else:
        App.noty('playlist_empty')


def get_bigger_cover(path):
    url = ''
    if path != '':
        try:
            paths = path.split('_')
            nums = paths[1][:-4]
            nums = map(int, nums.split('x'))
            y = 200 * nums[1] / nums[0]

            url = get_cover_by_size(paths[0], 200, y)

            if url == '':
                url = get_cover_by_size(paths[0], 200, y - 1)
                if url == '':
                    url = get_cover_by_size(paths[0], 200, y + 1)
                    if url == '':
                        url = '{0}/{1}/image.jpg'.format(URL, paths[0]).replace('thumbnails', 'images')
                        (resp_headers, resp_content) = H.request(url, 'GET')
                        if resp_headers.status != 200:
                            url = ''
        except:
            P.log_error(traceback.format_exc)
    return url if url != '' else '{0}/{1}'.format(URL, path)


def get_cover_by_size(path, x, y):
    url = '{0}/{1}_{2}x{3}.jpg'.format(URL, path, x, y)
    (resp_headers, resp_content) = H.request(url, 'GET')
    return url if resp_headers.status == 200 else ''


def get_description(info):
    description = ''
    if 'description' in info:
        description = info['description']
    if 'long_description' in info:
        description = info['long_description']

    director = App.STR_NO_DATA
    if 'directors' in info:
        director = App.explode_info_string(info['directors'])

    # name_original = info['international_name']

    rating = get_movie_rating_value(info, 'rating_imdb_count', 'rating_imdb_value')
    if rating == '':
        rating = get_movie_rating_value(info, 'rating_kinopoisk_count', 'rating_kinopoisk_value')

    return App.format_description(
        country=App.explode_info_string(info['countries']) if 'countries' in info else '',
        genre='' if App.get_skin() == 'skin.confluence' else App.explode_info_string(info['genres']) if 'genres' in info else '',
        description=description.replace('<br>', '\n').encode('utf-8'),
        director=director,
        rating=rating
    )


def get_movie_rating(movie):
    stars = check_movie_rating(movie, 'rating_imdb_count', 'rating_imdb_value')
    if stars == '':
        stars = check_movie_rating(movie, 'rating_kinopoisk_count', 'rating_kinopoisk_value')

    return stars


def check_movie_rating(movie, count_name, value_name):
    stars = ''
    try:
        count = int(movie[count_name])
        rating = float(movie[value_name])
        if count >= stars_condition['count']:
            for key in sorted(stars_condition['ratings']):

                if rating >= stars_condition['ratings'][key]:
                    stars = key
    except:
        pass
    return stars


def get_movie_rating_value(movie, count_name, value_name):
    try:
        count = int(movie[count_name])
        rating = float(movie[value_name])
        if count >= stars_condition['count']:
            return str(rating)
    except:
        return ''


def get_pagination(current, total, size, offset, params):
    items = []

    current = int(current)
    total = int(total)
    size = int(size)
    offset = int(offset)

    pages = {
        'total': total if (size == 0 and offset == 0) else int(math.ceil(total / size + 1)),
        'current': current if (current > 0) else 1
    }
    if pages['total'] < pages['current']:
        pages['current'] = pages['total']

    if pages['current'] > 1:
        items.append({
            'label': App.replace_html_codes('[B]<[/B]&emsp;Предыдущая страница'.decode('utf-8')),
            'icon': App.get_media('prev'),
            'url': P.get_url(
                action='co_movies',
                order_id=params.order_id,
                genre_id=params.genre_id,
                page=pages['current'] - 1 - offset
            )
        })
    if pages['current'] < pages['total']:
        items.append({
            'label': App.replace_html_codes('[B]>[/B]&emsp;Следующая страница'.decode('utf-8')),
            'icon': App.get_media('next'),
            'url': P.get_url(
                action='co_movies',
                order_id=params.order_id,
                genre_id=params.genre_id,
                page=pages['current'] + 1 - offset
            )
        })

    pages = {
        'total': int(math.ceil(total / size + 1)),
        'current': offset / size + 1
    }

    return items


def add_pagination(items, pagination):
    for p in pagination:
        items.insert(0, p)
        items.append(p)
    return items
