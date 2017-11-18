# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
import urllib
import simplejson as json
import re


URL = 'http://namba.kg'
API = URL + '/api'


@P.action()
def nm_index(params):
    return [{
        'label': '[ Поиск ]',
        'icon': App.get_media('find'),
        'url': P.get_url(action='nm_search')
    }, {
        'label': 'Популярные',
        'url': P.get_url(action='nm_top')
    }, {
        'label': 'По жанрам',
        'url': P.get_url(action='nm_genres')
    }]


@P.action()
def nm_search(params):
    items = []
    query = App.keyboard(heading='Поиск')
    if query is None:
        pass
    elif query != '':
        content = App.http_request(API + '/?%s' % urllib.urlencode({
            'service': 'home',
            'action': 'search',
            'type': 'movie',
            'query': query,
            'sort': 'desc'
        }))
        if content:
            movies = json.loads(content)['movies']
            for movie in movies:
                cover = movie['preview']

                items.append({
                    'label': movie['title'],
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'url': P.get_url(action='nm_movie', id=movie['id'])
                })
            if len(items) == 0:
                App.noty('no_search_results')
    else:
        App.noty('no_search_results')

    return App.create_listing(items, content='movies')


@P.cached(720)
@P.action()
def nm_top(params):
    items = []

    content = App.http_request(URL + '/movie/')
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_='charts-block')
        if block is not None:
            for movie in block.find_all(class_='changed'):
                link = movie.find('a')
                img = link.find('img')

                id = link.get('href').split('=')[1]
                cover = img.get('src')
                label = img.get('title')

                items.append({
                    'label': label,
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'url': P.get_url(action='nm_movie', id=id)
                })
    return App.create_listing(items, content='movies')


@P.cached(1440)
@P.action()
def nm_genres(params):
    items = []

    content = App.http_request(URL + '/movie/')
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_='categories-menu')
        if block is not None:
            for genre in block.find_all('a'):
                label = App.bs_get_text(genre)
                id = genre.get('href').split('=')[1]

                items.append({
                    'label': label,
                    'url': P.get_url(action='nm_movies_by_genre', id=id)
                })
    return App.create_listing(items)


@P.cached(720)
@P.action()
def nm_movies_by_genre(params):
    params.refresh = 'page' in params

    items = []
    try:
        if params.page == 'search':
            page = int(App.keyboard(heading='Перейти на страницу', numeric=True))
            if page > params.total_pages:
                page = params.total_pages
            if page < 1:
                page = 1
            params.page = str(page)
        else:
            page = int(params.page)
    except:
        page = 1

    content = App.http_request('%s/movie/category.php?%s' % (URL, urllib.urlencode({
        'id': params.id,
        'p': page
    })))
    if content:
        html = BeautifulSoup(content, 'html.parser')
        block = html.find(class_='result-block')
        for movie in block.find_all(class_='thumb'):
            link = movie.find('a')
            img = link.find('img')

            id = link.get('href').split('=')[1]
            cover = img.get('src')
            label = img.get('title')

            items.append({
                'label': label,
                'thumb': cover,
                'art': {
                    'poster': cover
                },
                'url': P.get_url(action='nm_movie', id=id)
            })

        total_pages = int(re.compile('"paginator_container",\n      (\d+?),').findall(str(html))[0])
        add_pagination(items, get_pagination(page, total_pages, 'nm_movies_by_genre', params))

        if total_pages > 1:
            items.insert(0, {
                'label': App.replace_html_codes('%s&emsp;%d / %d' % ('[ Перейти на страницу ]'.decode('utf-8'), page, total_pages)),
                'url': P.get_url(action='nm_movies_by_genre', id=params.id, page='search', total_pages=total_pages)
            })

    return App.create_listing(items, content='movies', update_listing=params.refresh)


@P.action()
def nm_movie(params):
    items = []

    content = App.http_request('%s/movie/watch.php?%s' % (URL, urllib.urlencode({'id': params.id})))
    if content:
        html = BeautifulSoup(content, 'html.parser')
        cover = html.find(class_='movie-cover')
        if cover is not None:
            cover = cover.find('img').get('src')

        description = App.bs_get_text_with_newlines(html.find(class_='description-text'))

        flashvars = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(content)
        if flashvars:
            video_id = flashvars[0]
            items.append(create_movie_item(video_id, cover))
        else:
            video = html.find('source', {'type': 'video/mp4'})
            if video is not None:
                title = html.find(class_='panel-title')
                if title is not None:
                    title = title.get_text().split('/', 1)
                    P.log_error(title)
                    if len(title) == 2:
                        title = title[1]
                    else:
                        title = title[0]
                else:
                    title = 'Просмотр'

                items.append({
                    'label': App.remove_double_spaces(title),
                    'thumb': cover,
                    'art': {
                        'poster': cover
                    },
                    'info': {
                        'video': {
                            'plot': '' if App.get_skin_name() == 'skin.confluence' else description,
                        }
                    },
                    'url': video.get('src'),
                    'is_playable': True,
                })
            else:
                App.notification('Ошибка', 'Фильм не найден', 'info')

        
    return App.create_listing(items, content='movies')


def create_movie_item(id, cover):
    item = {}

    content = App.http_request('%s/?%s' % (API, urllib.urlencode({
        'service': 'video',
        'action': 'video',
        'id': id
    })))
    if content:
        movie = json.loads(content)['video']

        label = movie['title']

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
                    'plot': '' if App.get_skin_name() == 'skin.confluence' else movie['raw_description'],
                }
            },
            'url': movie['download']['flv'],
            'is_playable': True,
        }
    return item


def get_pagination(current_page, total_pages, action, params):
    items = []

    current_page = int(current_page)
    total_pages = int(total_pages)

    if total_pages < current_page:
        current_page = total_pages

    if current_page > 1:
        items.append({
            'label': App.replace_html_codes('%s&emsp;Предыдущая страница'.decode('utf-8') % App.format_bold('<')),
            'icon': App.get_media('prev'),
            'url': P.get_url(
                action=action,
                id=params.id,
                page=current_page - 1
            )
        })
    if current_page < total_pages:
        items.append({
            'label': App.replace_html_codes('%s&emsp;Следующая страница'.decode('utf-8') % App.format_bold('>')),
            'icon': App.get_media('next'),
            'url': P.get_url(
                action=action,
                id=params.id,
                page=current_page + 1
            )
        })

    return items


def add_pagination(items, pagination):
    for p in pagination:
        items.insert(0, p)
        items.append(p)
    return items
