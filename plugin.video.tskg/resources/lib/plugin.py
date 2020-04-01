# -*- coding: utf-8 -*-
#Script.log(tag, lvl=Script.ERROR)
from __future__ import unicode_literals

# noinspection PyUnresolvedReferences
from codequick import Route, Resolver, Listitem, run
from codequick.utils import urljoin_partial, bold, color
from codequick.script import Script
import HTMLParser
import random
import re
import urlquick
import xbmcgui

BASE_URL = "https://www.ts.kg"
url_constructor = urljoin_partial(BASE_URL)
urlquick.MAX_AGE = 1


@Route.register
def root(plugin, content_type="video"):
    yield Listitem.search(search)
    yield Listitem.from_dict(
        last_added,
        bold('Последние поступления')
    )
    categories = __get_categories()
    for category in categories:
        yield category


@Route.register
def tvshow_category(plugin, category_id):
    items = []
    page = 1
    while True:
        tvshows = __get_tvshows_by_category(category_id, page)
        if not tvshows:
            break
        else:
            items.extend(tvshows)
            page += 1
    return items


@Route.register
def search(plugin, search_query):
    response = urlquick.get(url_constructor('/show/search/{}'.format(search_query))).json()
    for tvshow in response:
        item = Listitem()
        show_id = tvshow['url'].split('/')[2]
        item.label = tvshow['name']
        item.art['thumb'] = __get_poster_url(show_id)
        item.set_callback(show_page, show_id=show_id)
        yield item


@Route.register
def last_added(plugin):
    """:param Route plugin: The plugin parent object."""
    html = urlquick.get(url_constructor('/news'))
    document = html.parse('div', attrs={'class': 'app-news'})
    for block in document.iterfind('.//div[@class="row app-news-block"]'):
        date = block.find('.//div[@class="app-news-date"]/strong').text
        for element in block.iterfind('.//div[@class="app-news-list-item"]'):
            item = Listitem()

            link = element.find('.//a')
            if link is None:
                continue

            title = link.text
            subtitle = element.find('.//span/small')
            subtitle = subtitle.text if subtitle is not None else ''
            genres = link.get('title')
            badges = map(__parse_badges, element.findall('.//span'))
            badges = ' '.join(filter(None, badges))
            href = link.get('href')
            if (href.startswith('/show')):
                show_id = href.split('/')[2]
                item.art['thumb'] = __get_poster_url(show_id)
                item.set_callback(show_page, show_id=show_id)
            elif (href.startswith('/selection')):
                item.set_callback(tvshow_selection, href)
            else:
                continue

            label = filter(None, [date[:2], bold(title), badges, subtitle])
            plot = filter(None, ['[CR]'.join(filter(None, [bold(title), badges])), genres, subtitle])
            item.label = __replace_html_codes('&emsp;'.join(label))
            item.info['plot'] = '[CR][CR]'.join(plot)
            # # Date
            # date = elem.find(".//time")
            # if date is not None:
            #     date = date.get("datetime").split("T", 1)[0]
            #     item.info.date(date, "%Y-%m-%d")  # 2018-10-19

            # # Video url
            # url_tag = elem.find(".//a[@class='ellipsis']")
            # url = url_tag.get("href")

            # item.context.related(video_list, url='url', filter_mode=1)
            yield item


@Route.register
def show_page(plugin, show_id):
    html = urlquick.get(url_constructor('/show/{}'.format(show_id)))
    document = html.parse('div', attrs={'class': 'container main-container'})
    title = document.find('.//div[@id="h-show-title"]')
    if title is not None:
        all_seasons_item = Listitem()
        all_seasons_item.art['thumb'] = __get_poster_url(show_id)

        title = bold(title.text)
        title_original = document.find('.//div[@class="app-show-header-title-original"]').text
        all_seasons_item.label = __replace_html_codes('&emsp;'.join([title, 'Все сезоны']))
        years = ''.join(document.find('.//div[@class="app-show-header-years"]').itertext())
        genres = filter(None, map(__clear_tvshow_tags, document.findall('.//ul[@class="app-show-tags"]/li/a')))
        country = document.find('.//ul[@class="app-show-tags"]/li/a[@class="app-show-tags-flag"]')
        country = country.text if country is not None else 'un'
        description = __replace_html_codes(document.find('.//p[@class="app-show-description"]').text)

        seasons = []
        for season_block in document.iterfind('.//section[@class="app-show-seasons-section-light hidden"]'):
            season = {
                'title': '',
                'episodes': []
            }
            season['title'] = season_block.find('.//h3').text
            
            for link in season_block.iterfind('.//div/ul/li/a'):
                episode_id = link.get('id')[31:]
                season['episodes'].append(episode_id)
            seasons.append(season)
            # Script.log(season_number, lvl=Script.ERROR)
            # Script.log(episode_number, lvl=Script.ERROR)

        plot = [__format_join('[CR]', [title, title_original]), description]
        all_seasons_item.info['plot'] = '[CR][CR]'.join(plot)
        

        episodes_ids = []
        seasons_items = []
        for season in seasons:
            item = Listitem()
            episodes_count = len(season['episodes'])
            item.label = __replace_html_codes('&emsp;'.join([bold(season['title']), '({})'.format(episodes_count)]))
            item.art['thumb'] = __get_poster_url(show_id)
            plot = [title, season['title'], 'Эпизодов: {}'.format(episodes_count)]
            item.info['plot'] = '[CR][CR]'.join(plot)
            item.set_callback(tvshow_episodes, episodes_ids=season['episodes'], show_id=show_id)
            episodes_ids.extend(season['episodes'])
            seasons_items.append(item)
        

        all_seasons_item.set_callback(tvshow_episodes, episodes_ids=episodes_ids, show_id=show_id)
        yield all_seasons_item

        mix_playlist = episodes_ids[:]
        random.shuffle(mix_playlist)
        yield Listitem.from_dict(play_episodes_mix, 'Микс',
            art={'thumb': __get_poster_url(show_id)},
            info={'plot': 'Воспроизвести в случайном порядке'},
            params={'episodes_ids':mix_playlist}
        )

        for item in seasons_items:
            yield item


@Route.register
def tvshow_episodes(plugin, episodes_ids, show_id):
    items = []
    playlist = []
    episodes_ids.reverse()
    for episode_id in episodes_ids:
        (label, url, quality, subtitles, duration, plot) = __get_episode_info(episode_id)

        item = Listitem()
        item.label = label
        item.subtitles = subtitles
        item.info['duration'] = duration
        item.info['plot'] = plot
        item.art['thumb'] = __get_poster_url(show_id)
        item.url = url
        item.stream.hd(quality)
        # item.context.related(funct, url=url) # вызывает функцию в контекстном меню
        
        playlist.append((label, url))
        playlist_copy = playlist[:]
        playlist_copy.reverse()
        
        item.set_callback(play_episodes, playlist=playlist_copy)
        items.append(item)
    items.reverse()
    for item in items:
        yield item


@Route.register
def tvshow_selection(plugin, url):
    html = urlquick.get(url_constructor(url))
    document = html.parse('div', attrs={'class': 'container main-container'})
    for tvshow in document.iterfind('.//div[@class="row selection-show"]'):
        link = tvshow.find('a')
        href = link.get('href')
        show_id = href.split('/')[2]
        title = tvshow.find('div//a').text
        title_original = tvshow.find('div//small')
        if title_original is not None:
            title_original = title_original.text
        description = tvshow.find('div/p').text.strip()

        item = Listitem()
        item.label = title
        item.art['thumb'] = __get_poster_url(show_id)
        item.info['plot'] = __format_join('[CR][CR]', [__format_join('[CR]', [bold(title), title_original]), description])
        item.set_callback(show_page, show_id=show_id)
        yield item


@Resolver.register
def play_episodes(plugin, playlist):
    return playlist
    # Script.log('play_episode ' + str(items), lvl=Script.ERROR)


@Resolver.register
def play_episodes_mix(plugin, episodes_ids):
    playlist = []
    for episode_id in episodes_ids:
        (label, url, quality, subtitles, duration, plot) = __get_episode_info(episode_id)
        playlist.append((label, url))
    return playlist


def __get_episode_info(episode_id):
    response = urlquick.get(url_constructor('/show/episode/episode.json?episode={}'.format(episode_id)), headers={
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0'
    }).json()
    label = response['fullname']
    title = label
    voice = response['voice']
    if response['name'] is not None:
        label += __replace_html_codes('&emsp;' + bold(response['name']))

    duration = response['duration']
    subtitles = url_constructor(response['subtitles']) if response['subtitles'] else None

    hd = response['video']['files']['HD']['url']
    sd = response['video']['files']['SD']['url']
    url = hd if hd is not None else sd
    quality = hd is not None # 0 - sd, 1 - hd

    return (label, url, quality, filter(None, [subtitles]), duration, __format_join('[CR][CR]', [title, response['name'], voice]))


def __get_categories():
    items = []
    html = urlquick.get(url_constructor('/show'))
    document = html.parse('select', attrs={'id': 'filter-category'})
    for option in document.iterfind('optgroup/option'):
        category_id = option.get('value')
        if category_id == '0':
            continue
        items.append(Listitem.from_dict(tvshow_category, option.text, params={'category_id':category_id}))
    return items


def __get_tvshows_by_category(category_id, page):
    items = []
    html = urlquick.get(url_constructor('/show?category={}&sortby=a&page={}'.format(category_id, page)))
    document = None
    try:
        document = html.parse('div', attrs={'id': 'shows'})
    except Exception as e:
        pass
    if document is not None:
        for show in document.iterfind('.//div[@class="show"]'):
            title = ''.join(show.find('.//p[@class="show-title"]').itertext()).strip()
            link = show.find('.//a')
            href = link.get('href')
            show_id = href.split('/')[2]
            img = show.find('.//img[@class="poster poster-lazy"]')
            genres = img.get('title')
            item = Listitem()
            item.label = title
            item.info['plot'] = '[CR][CR]'.join(filter(None, [bold(title), genres]))
            item.art['thumb'] = __get_poster_url(show_id)
            item.set_callback(show_page, show_id=show_id)

            items.append(item)
    return items


def __clear_tvshow_tags(element):
    # нужно удалить элементы с аттрибутом class
    return None if element.get('class') is not None else ''.join(element.itertext())


def __get_poster_url(show_id):
    return '{0}/posters/{1}.png'.format(BASE_URL, show_id)


def __replace_html_codes(text):
    text = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', text)
    text = HTMLParser.HTMLParser().unescape(text)
    text = text.replace('&amp;', '&')
    return text


def __parse_badges(element):
    element_class = element.get('class')
    result = None
    if 'label' in element_class:
        result = element.text
        if not result:
            span = element.find('.//span')
            if span is not None:
                result = span.get('title')
    color_code = 'FFee98fb' # light purple
    if result in ['Топ', 'Важно']:
        color_code = 'FFe53935' # red
    elif result == 'Подборка':
        color_code = 'FFff9800' # orange
    elif result == 'Новое':
        color_code = 'FF5cb85c' # green
    elif result in ['Обновлено', 'Финал']:
        color_code = 'FF5bc0de' # blue
    return None if result is None else bold(color(result, color_code))

def __format_join(separator, items):
    return separator.join(filter(None, items))