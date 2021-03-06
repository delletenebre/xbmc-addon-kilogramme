# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
from App import H
import xbmc
import simplejson as json
import urllib
import re
import traceback
from operator import itemgetter


URL = 'http://www.ts.kg'



@P.cached(1440)
@P.action()
def ts_index(params):
    items = []
    content = App.http_request(URL + '/show')
    if content:
        items.append(
            {
                'label': '[ Поиск ]',
                'url': P.get_url(action='ts_search'),
                'icon': App.get_media('find')
            }
        )
        items.append(
            {
                'label': App.format_bold('Последние поступления'),
                'url': P.get_url(action='ts_last_added'),
            }
        )

        html = BeautifulSoup(content, 'html.parser')
        categories = html.find(id='filter-category')

        for option in categories.find_all('option'):
            id = option.get('value')
            if id == '0':
                continue

            label = option.get_text()
            items.append(
                {
                    'label': label,
                    'url': P.get_url(action='ts_category', id=id)
                }
            )
    return App.create_listing(items)


@P.action()
def ts_search(params):
    items = []
    query = App.keyboard(heading='Поиск')
    if query is None:
        pass
    elif query != '':
        query = query.decode('utf-8').lower()
        tvshows = App.http_request('%s/show/search/%s' % (URL, query))
        if tvshows is not None:
            tvshows = sorted(json.loads(tvshows), key=itemgetter('name'))
            for tvshow in tvshows:
                try:
                    name = tvshow['name'].encode('utf-8')
                    url = tvshow['url']

                    items.append(
                        {
                            'label': name,
                            'url': P.get_url(action='ts_tvshow_seasons', href=url)
                        }
                    )
                except:
                    P.log_error(traceback.format_exc())
        if len(items) == 0:
            App.noty('no_search_results')
    else:
        App.noty('no_search_results')

    return App.create_listing(items, content='tvshows')


@P.cached(120)
@P.action()
def ts_last_added(params):
    items = []

    content = App.http_request(URL + '/news')
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for block in html.find_all(class_='app-news-block'):
            date = App.bs_get_text(block.find(class_='app-news-date'))

            for list_item in block.find_all(class_='app-news-list-item'):
                badge = get_news_item_badge(list_item)

                link = list_item.find(class_='app-news-link')

                if not link:
                    continue

                label = App.bs_get_text(link)
                sub_label = App.bs_get_text(list_item.find('small'))

                genres = link.get('title').replace(', ', App.STR_LIST_DELIMITER).encode('utf-8')

                label = [date[:2], App.format_bold(label), sub_label, App.format_bold(badge)]
                label = filter(None, label)
                label = App.replace_html_codes('&emsp;'.join(label))

                item_url = P.get_url(action='add_favorite')

                href = link.get('href')
                hrefs = href.split('/')
                href1 = hrefs[1]
                if href1 == 'selection':
                    item_url = P.get_url(action='ts_selection', href=href)
                elif href1 == 'show':
                    if len(hrefs) == 3:
                        item_url = P.get_url(action='ts_tvshow_seasons', href=href)
                    else:
                        item_url = P.get_url(action='ts_tvshow_seasons',
                                             href='/'.join(hrefs[:3]))

                description = App.format_description(genre=genres)

                items.append(
                    {
                        'label': label,
                        'info': {
                            'video': {
                                'plot': '' if App.get_skin_name() == 'skin.confluence' else description,
                                'genre': App.clear_xbmc_tags(genres)
                            }
                        },
                        'url': item_url,
                    }
                )
    return App.create_listing(items, content='tvshows')


#@P.cached(1440)
@P.action()
def ts_category(params):
    items = []

    def get_shows_by_page(page):
        content = App.http_request(URL + '/show?' + urllib.urlencode({'category': params.id, 'sortby': 'a', 'page': page}))
        if content:
            html = BeautifulSoup(content, 'html.parser')
            shows = html.find(id='shows')
            if shows is not None:
                for show in shows.find_all(class_='show'):
                    tag_a = show.find('a')
                    tag_img = tag_a.find('img')
                    tag_p = tag_a.find('p')

                    episodes = show.find(class_='ec').get_text()
                    href = tag_a.get('href')
                    poster = URL + tag_img.get('src')
                    genres = tag_img.get('title')
                    if genres is not None:
                        genres = genres.split(', ')
                        if (len(genres) > 1):
                            del genres[0]
                        genres = App.explode_info_string(genres)
                    else:
                        genres = App.STR_NO_DATA

                    country = tag_p.find('img')
                    if country is not None:
                        country = App.get_country(country.get('alt'))
                    else:
                        country = ''

                    label = tag_p.get_text()
                    description = App.format_description(episodes=episodes,
                                                         country=country,
                                                         genre='' if App.get_skin_name() == 'skin.confluence' else genres)
                    items.append(
                        {
                            'label': label,
                            'icon': poster,
                            'fanart': poster,
                            'art': {
                                'poster': poster
                            },
                            'info': {
                                'video': {
                                    'mediatype': 'tvshow',
                                    'title': label,
                                    'genre': App.clear_xbmc_tags(genres),
                                    'episode': episodes,
                                    'plot': description
                                }
                            },
                            'properties': {
                                'TotalEpisodes': episodes
                            },
                            'url': P.get_url(action='ts_tvshow_seasons', href=href)
                        }
                    )

                get_shows_by_page(page + 1)

    get_shows_by_page(1)

    return App.create_listing(items, content='tvshows')


#@P.cached(1440)
@P.action()
def ts_tvshow_seasons(params):
    items = []
    content = App.http_request(URL + params.href)
    content = content.replace('</span></strong></span></a>', '</span></strong></a></span>') # fix closing tags
    if content:
        html = BeautifulSoup(content, 'html.parser')
        title = html.find('meta', {'property': 'og:title'}).get('content')
        description = html.find('meta', {'property': 'og:description'}).get('content').encode('utf-8')
        poster = html.find('meta', {'property': 'og:image'}).get('content')
        country = App.STR_NO_DATA
        genres = []
        tvshow_tags = html.find(class_='app-show-tags')
        if tvshow_tags is not None:
            country = tvshow_tags.find(class_='app-show-tags-flag')
            if country:
                country = country.get('data-original-title')
            else:
                country = App.STR_NO_DATA

            for a in tvshow_tags.find_all('a'):
                href = a.get('href').split('/')
                if href[1] == 'genre':
                    genres.append(a.get_text())
        genres = App.explode_info_string(genres)
        description = App.format_description(description=description,
                                            country=country,
                                            genre='' if App.get_skin_name() == 'skin.confluence' else genres)
        meta_premiered = ''
        year = html.find('h3')
        if year:
            year = App.bs_get_text(year.find('a'))
            if year:
                meta_premiered = '%s-01-01' % year
        else:
            year = ''
        meta_genres = App.clear_xbmc_tags(genres)
        
        episodes_ids_all_seasons = ''
        episodes_all_seasons = 0
        seasons = html.find_all('div', {'data-season': True})
        for season in seasons:
            season_number = season.get('data-season')

            episodes_ids = []
            episodes = season.find_all(class_="text-primary")
            for episode in episodes:
                episode_id = episode.get('id')[23:]
                episodes_ids.append(episode_id)

            episodes_ids = ','.join(episodes_ids)
            episodes_ids_all_seasons += episodes_ids
            episodes_all_seasons += len(episodes)

            items.append(
                {
                    'label': 'Сезон {0}'.format(season_number),
                    'icon': poster,
                    'fanart': poster,
                    'art': {
                        'poster': poster
                    },
                    'info': {
                        'video': {
                            'plot': description,
                            'year': year,
                            'genre': meta_genres,
                            'episode': str(len(episodes))
                        }
                    },
                    'url': P.get_url(action='ts_tvshow_season_episodes',
                                     season=season_number,
                                     episodes_ids=episodes_ids),
                    'is_folder': False
                }
            )    

        items.insert(0, {
            'label': App.replace_html_codes('%s&emsp;Все сезоны'.decode('utf-8') % App.format_bold(title)),
            'thumb': poster,
            'art': {
                'poster': poster
            },
            'info': {
                'video': {
                    'mediatype': 'tvshow',
                    'plot': description,
                    'premiered': meta_premiered,
                    'genre': meta_genres,
                    'episode': '10'
                }
            },
            'properties': {
                'TotalSeasons': str(len(seasons)),
                'TotalEpisodes': str(episodes_all_seasons)
            },
            'url': P.get_url(action='ts_tvshow_season_episodes',
                             season='all',
                             episodes_ids=episodes_ids_all_seasons),
            'is_folder': False
        })

    return App.create_listing(items, content='tvshows')


@P.action()
def ts_tvshow_season_episodes(params):
    items = []

    xbmc.executebuiltin('ActivateWindow(busydialog)')

    for id in params.episodes_ids.split(','):
        try:
            (resp_headers, content) = H.request('{0}/show/episode/episode.json?episode={1}'.format(URL, id), 'GET', headers={'X-Requested-With': 'XMLHttpRequest', 'User-Agent': App.USER_AGENT})
            if resp_headers.status == 200:
                episode = json.loads(content)

                label = episode['fullname']
                if episode['name'] is not None:
                    label += App.replace_html_codes('&emsp;' + App.format_bold(episode['name']))

                duration = episode['duration']

                hd = episode['video']['files']['HD']['url']
                sd = episode['video']['files']['SD']['url']

                subtitles = episode['subtitles']

                items.append(
                    {
                        'label': label,
                        'stream_info': {
                            'video': {
                                'duration': duration
                            }
                        },
                        'subtitles': [URL + subtitles if subtitles is not False else ''],
                        'mime': episode['video']['mimetype'],
                        'url': hd if hd is not None else sd,
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


@P.action()
def ts_selection(params):
    items = []

    content = App.http_request(URL + params.href)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for show in html.find_all(class_='selection-show'):
            href = show.find('a').get('href')
            img = show.find('img')
            poster = URL + img.get('src')
            title = show.find('h4').find('a').get_text()
            title_original = App.bs_get_text(show.find('small'))
            description = App.bs_get_text(show.find(class_='selection-show-description'))
            # genres = App.STR_NO_DATA
            # country = App.STR_NO_DATA
            plot = ' '.join(description.split())
            if title_original != '':
                plot = '%s\n\n%s' % (App.format_bold(title_original), plot)

            items.append(
                {
                    'label': title,
                    'thumb': poster,
                    'art': {
                        'poster': poster
                    },
                    'info': {
                        'video': {
                            'mediatype': 'tvshow',
                            'plot': plot
                        }
                    },
                    'url': P.get_url(action='ts_tvshow_seasons', href=href)
                }
            )

    return App.create_listing(items, content='tvshows')


@P.action()
def add_favorite(params):
    xbmc.executebuiltin('ActivateWindow()')
    # xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Favourites.AddFavourite", "params": {"title":"%s", "type":"window", "path":"%s", "thumbnail":"%s"}, "id": 1}' % (name, cmd, thumb))


def get_news_item_badge(item):
    result = ''
    badge = item.find(class_='label')
    if badge is not None:
        try:
            text = badge.get_text()
            color = App.get_color(badge.get('class')[1])
            result = App.format_color(text, color)
        except:
            P.log_error(traceback.format_exc())

    return result
