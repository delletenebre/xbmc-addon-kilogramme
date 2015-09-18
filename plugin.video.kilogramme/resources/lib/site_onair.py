#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, json, urllib, traceback
from _header import *

BASE_URL   = 'http://www.onair.kg/api/'
BASE_NAME  = 'OnAir'
BASE_LABEL = 'onair'
#GA_CODE = 'UA-337170-16'
SETT_DAYS = plugin.get_setting('onair_news_count', int)
NK_CODE = '4094'

@plugin.route('/site/' + BASE_LABEL)
def onair_index():
    item_list = get_categories(BASE_URL)
    items     = []

    if item_list:
        items = [{
            'label'     : item['title'],
            'path'      : plugin.url_for('get_all_by_category', id = item['id']),
            'thumbnail' : item['icon'],
        } for item in item_list]

        items = [{
            'label': set_color('[ Поиск ]', 'dialog', True),
            'path': plugin.url_for('onair_search'),
            'icon': get_local_icon('find'),
        }, {
            'label': set_color('Последние поступления', 'light', True),
            'path': plugin.url_for('onair_lastadded'),
        }, {
            'label': set_color('Популярные - ТОП 10', 'bright', True),
            'path': plugin.url_for('onair_popular'),
        }] + items

    else:
        plugin.notify('Сервер недоступен', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))

    return items

@plugin.route('/site/' + BASE_LABEL + '/search')
def onair_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if (search_val):
        item_list = get_search(search_val)

        items = [{
            'label'     : item['label'],
            'path'      : plugin.url_for(item['function'], id = item['id'], title = to_utf8(item['title'])) if item['function'] else item['url'],
            'thumbnail'  : item['icon'],
            'info'       : item['info'] if item['function'] == False else None,
            'properties' : item['properties'] if item['function'] == False else None,
            'is_playable': True if item['function'] == False else False
         } for item in item_list]

        return items
    else:
        plugin.redirect('plugin://' + plugin.id + '/site/' + BASE_LABEL)


@plugin.route('/site/' + BASE_LABEL + '/last')
def onair_lastadded():
    item_list = get_lastadded()

    items = [{
        'label'     : item['label'],
        'path'      : plugin.url_for(item['function'], id = item['id'], title = to_utf8(item['title'])) if item['function'] else item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'] if item['function'] == False else None,
        'properties' : item['properties'] if item['function'] == False else None,
        'is_playable': True if item['function'] == False else False
     } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/popular')
def onair_popular():
    item_list = get_popular()

    items = [{
        'label'     : item['label'],
        'path'      : plugin.url_for(item['function'], id = item['id'], title = to_utf8(item['title'])) if item['function'] else item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'] if item['function'] == False else None,
        'properties' : item['properties'] if item['function'] == False else None,
        'is_playable': True if item['function'] == False else False
     } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/all/<id>')
def get_all_by_category(id):
    item_list = get_list(id)

    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for(item['function'], id = item['id'], title = to_utf8(item['title'])) if item['function'] else item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'] if item['function'] == False else None,
        'properties' : item['properties'] if item['function'] == False else None,
        'is_playable': True if item['function'] == False else False
    } for item in item_list['items']]

    return items





@plugin.route('/site/' + BASE_LABEL + '/movie/<id>')
def onair_movie(id):
    item_list = get_movies(id)
    items = [{
        'label'      : item['title'],
        'path'       : item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'],
        'properties' : item['properties'],
        'is_playable': True
    } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/movies/genre/<id>')
def onair_movies_by_genre(id):
    item_list = get_movies('movies/genres/' + str(id))
    items = [{
        'label'      : item['title'],
        'path'       : item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'],
        'properties' : item['properties'],
        'is_playable': True
    } for item in item_list]

    return items

@plugin.route('/site/' + BASE_LABEL + '/movies/country/<id>')
def onair_movies_by_country(id):
    item_list = get_movies('movies/countries/' + str(id))
    items = [{
        'label'      : item['title'],
        'path'       : item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'],
        'properties' : item['properties'],
        'is_playable': True
    } for item in item_list]

    return items


@plugin.route('/site/' + BASE_LABEL + '/tvshow/<id>')
def onair_serial(id):
    title = plugin.request.args['title'][0]
    item_list = get_tvshow_seasons(id, title)
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('onair_season', id = id, season_id = item['season_id'], season_num = item['season_num'], title = to_utf8(title)),
        'thumbnail' : item['icon'],
        'is_not_folder': True,
    } for item in item_list['items']]

    return items

@plugin.route('/site/' + BASE_LABEL + '/tvshows/genre/<id>')
def onair_serials_by_genre(id):
    item_list = get_tvshows_by_genre(id)
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('onair_serial', id = item['id'], title = to_utf8(item['title'])),
        'thumbnail' : item['icon'],
    } for item in item_list['items']]

    return items

@plugin.route('/site/' + BASE_LABEL + '/tvshows/country/<id>')
def onair_serials_by_country(id):
    item_list = get_tvshows_by_country(id)
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('onair_serial', id = item['id'], title = to_utf8(item['title'])),
        'thumbnail' : item['icon'],
    } for item in item_list['items']]

    return items

@plugin.route('/site/' + BASE_LABEL + '/tvshow/<id>/season/<season_id>/<season_num>')
def onair_season(id, season_id, season_num):
    title = plugin.request.args['title'][0]
    plugin.notify('Пожалуйста, подождите', BASE_NAME, 1000, get_local_icon('noty_' + BASE_LABEL))
    item_list = get_episodes(season_id, title, season_num)
    kgontv_playlist(item_list)
    xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')




# method
def get_lastadded():
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'films/novelties'})
        if result['status'] == 200:
            jsonrs = json.loads(result['content'])

            setting_days = -1

            for jsonr in reversed(jsonrs):
                if setting_days == SETT_DAYS:
                    break;
                setting_days = setting_days + 1

                date = jsonr['Date'] + '&emsp;'
                films = jsonr['Films']

                for item in films:
                    if 'Type' in item:
                        item_type = item['Type']

                        if item_type == 'Movie':
                            movie_jsonr = common.fetchPage({'link': BASE_URL + 'movies/' + str(item['Id'])})
                            if movie_jsonr['status'] == 200:
                                item = json.loads(movie_jsonr['content'])

                                cover = item['PosterFile']
                                href  = item['VideoFile']
                                info  = {
                                    'duration'     : str2minutes(item['Duration']) if item['Duration'] else 0,
                                    'plot'         : item['Description'],
                                }

                                imdb = str(item['ImdbRating'])
                                kinopoisk = str(item['KinopoiskRating'])
                                rating = '&emsp;' + imdb + ' / ' + kinopoisk

                                country = item['Countries']
                                genres = item['Genres']

                                properties = {
                                    #'Country': country,
                                    #'PlotOutline': item['description'],
                                    'Plot': item['Description'],
                                    'Year': str(item['ReleaseYear']),
                                    'Rating': imdb
                                }

                                country = '&emsp;(' + country + ')' if (country) else ''

                                label = common.replaceHTMLCodes( date + '[B]' + item['Title'] + '[/B]' + country + '&emsp;' + genres + rating )
                                title = common.replaceHTMLCodes( item['Title'] )

                                items.append({
                                    'label': label,
                                    'title': title,
                                    'icon': cover,
                                    'url': href,
                                    'info': info,
                                    'properties': properties,
                                    'function': False,
                                })

                        elif item_type == 'Serial':

                            id    = item['Id']
                            title = common.replaceHTMLCodes( item['Title'] )

                            label = item['Title']
                            if 'AdditionalInfo' in item:
                                label = item['AdditionalInfo'].replace(label, '[B]' + label + '[/B]')
                            
                            label = common.replaceHTMLCodes( date + label )
                            icon  = item['PosterFile']

                            items.append({
                                'label': label,
                                'title': title,
                                'icon': icon,
                                'id': id,
                                'function': 'onair_serial'
                            })

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


# method
def get_popular():
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'films/popular'})
        if result['status'] == 200:
            jsonrs = json.loads(result['content'])
            for item in jsonrs:
                if 'Type' in item:
                    item_type = item['Type']

                    if item_type == 'Movie':
                        movie_jsonr = common.fetchPage({'link': BASE_URL + 'movies/' + str(item['Id'])})
                        if movie_jsonr['status'] == 200:
                            item = json.loads(movie_jsonr['content'])

                            cover = item['PosterFile']
                            href  = item['VideoFile']
                            info  = {
                                'duration'     : str2minutes(item['Duration']) if item['Duration'] else 0,
                                'plot'         : item['Description'],
                            }

                            imdb = str(item['ImdbRating'])
                            kinopoisk = str(item['KinopoiskRating'])
                            rating = '&emsp;' + imdb + ' / ' + kinopoisk

                            country = item['Countries']
                            genres = item['Genres']

                            properties = {
                                #'Country': country,
                                #'PlotOutline': item['description'],
                                'Plot': item['Description'],
                                'Year': str(item['ReleaseYear']),
                                'Rating': imdb
                            }

                            country = '&emsp;(' + country + ')' if (country) else ''

                            label = common.replaceHTMLCodes( '[B]' + item['Title'] + '[/B]' + country + '&emsp;' + genres + rating )
                            title = common.replaceHTMLCodes( item['Title'] )

                            items.append({
                                'label': label,
                                'title': title,
                                'icon': cover,
                                'url': href,
                                'info': info,
                                'properties': properties,
                                'function': False,
                            })

                    elif item_type == 'Serial':

                        id    = item['Id']
                        title = common.replaceHTMLCodes( item['Title'] )
                        label = common.replaceHTMLCodes( '[B]' + item['Title'] + '[/B]' )
                        icon  = item['PosterFile']

                        items.append({
                            'label': label,
                            'title': title,
                            'icon': icon,
                            'id': id,
                            'function': 'onair_serial'
                        })

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_categories(url):
    items = []
    try:
        items.append({'title':'Фильмы', 'icon':'', 'id':10})
        items.append({'title':'Фильмы по жанрам', 'icon':'', 'id':11})
        items.append({'title':'Фильмы по стране', 'icon':'', 'id':12})
        items.append({'title':'Сериалы', 'icon':'', 'id':20})
        items.append({'title':'Сериалы по жанрам', 'icon':'', 'id':21})
        items.append({'title':'Сериалы по стране', 'icon':'', 'id':22})
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items

#method
def get_list(id):
    items = []
    if ( id == '10' ) :
        return {'items': get_movies('movies')}

    try:
        apiurl = {
            '11' : 'movies/genres',
            '12' : 'movies/countries',
            '20' : 'serials',
            '21' : 'serials/genres',
            '22' : 'serials/countries',
        }.get(id, 'movies')

        function = {
            '11' : 'onair_movies_by_genre',
            '12' : 'onair_movies_by_country',
            '20' : 'onair_serial',
            '21' : 'onair_serials_by_genre',
            '22' : 'onair_serials_by_country',
        }.get(id, 'movies')

        result = common.fetchPage({'link': BASE_URL + apiurl})
        if result['status'] == 200:
            jsonr = json.loads(result['content'])

            for item in jsonr:
                id    = item['Id']
                title = item['Name'] if item['Name'] != '-' else 'Без категории'
                icon  = ''

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'id':id, 'function':function})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {'items':items}


#method
def get_movies(url):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + url})
        if result['status'] == 200:
            jsonrs = json.loads(result['content'])
            for jsonr in jsonrs:
                cover = jsonr['PosterFile']
                href  = jsonr['VideoFile']
                info  = {
                    'duration'     : str2minutes(jsonr['Duration']) if jsonr['Duration'] else 0,
                    'plot'         : jsonr['Description'],
                }

                imdb = str(jsonr['ImdbRating'])
                kinopoisk = str(jsonr['KinopoiskRating'])
                rating = '&emsp;' + imdb + ' / ' + kinopoisk

                country = jsonr['Countries']
                genres = jsonr['Genres']

                properties = {
                    #'Country': country,
                    #'PlotOutline': jsonr['description'],
                    'Plot': jsonr['Description'],
                    'Year': str(jsonr['ReleaseYear']),
                    'Rating': imdb
                }

                country = '&emsp;(' + country + ')' if (country) else ''

                title = common.replaceHTMLCodes('[B]' + jsonr['Title'] + '[/B]' + country + '&emsp;' + genres + rating)

                items.append({'function':False, 'title':title, 'icon':cover, 'url':href, 'info':info, 'properties':properties})
    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)
    return items


#method
def get_tvshow_seasons(id, title):
    items = []
    tvshow_title = title.decode('utf-8')
    title = ''
    try:
        result = common.fetchPage({'link': BASE_URL + 'serials/' + str(id) + '/seasons'})
        if result['status'] == 200:
            jsonr = json.loads(result['content'])

            for item in jsonr:
                season_id = item['Id']
                title = tvshow_title + '&emsp;' + item['Name']
                icon  = ''

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'season_id':season_id, 'tvshow_title':tvshow_title, 'season_num':item['Name'][6:]})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {'items':items}


#method
def get_tvshow_season_episodes(id, title):
    items = []
    tvshow_title = title.decode('utf-8')
    title = ''
    try:
        result = common.fetchPage({'link': BASE_URL + 'seasons/' + str(id) + '/episodes'})
        if result['status'] == 200:
            jsonr = json.loads(result['content'])

            for item in jsonr:
                season_id = item['Id']
                title = tvshow_title + '&emsp;' + item['Name']
                icon  = ''

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'season_id':season_id, 'tvshow_title':tvshow_title})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {'items':items}



#method
def get_tvshows_by_genre(id):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'serials/genres/' + str(id)})
        if result['status'] == 200:
            jsonr = json.loads(result['content'])

            for item in jsonr:
                id    = item['Id']
                title = item['Name'] if item['Name'] != '-' else 'Без категории'
                icon  = ''

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'id':id})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {'items':items}

#method
def get_tvshows_by_country(id):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'serials/countries/' + str(id)})
        if result['status'] == 200:
            jsonr = json.loads(result['content'])

            for item in jsonr:
                id    = item['Id']
                title = item['Name'] if item['Name'] != '-' else 'Без категории'
                icon  = ''

                items.append({'title':common.replaceHTMLCodes( title ), 'icon':icon, 'id':id})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return {'items':items}


#method
def get_episodes(id, season_title, season_num):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'seasons/' + str(id) + '/episodes'})
        if result['status'] == 200:
            jsonrs = json.loads(result['content'])
            for jsonr in jsonrs:
                icon = ''
                href = jsonr['VideoFile']
                info = {
                    'duration' : str2minutes(jsonr['Duration']) if jsonr['Duration'] else 0,
                    'plot'     : jsonr['Description'],
                }

                title = common.replaceHTMLCodes(season_title.decode('utf-8') + '&emsp;' + 's' + season_num + 'e' + jsonr['Number'] + '&emsp;' + jsonr['Title'])

                items.append({'title': title, 'url': href, 'icon': icon, 'info':info})

    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items


#method
def get_search(val):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'films/search?title=' + str(val)})
        if result['status'] == 200:
            jsonrs = json.loads(result['content'])
            for item in jsonrs:
                item_type = item['Type']

                if item_type == 'Movie':

                    movie_jsonr = common.fetchPage({'link': BASE_URL + 'movies/' + str(item['Id'])})
                    if movie_jsonr['status'] == 200:
                        item = json.loads(movie_jsonr['content'])

                        cover = item['PosterFile']
                        href  = item['VideoFile']
                        info  = {
                            'duration'     : str2minutes(item['Duration']) if item['Duration'] else 0,
                            'plot'         : item['Description'],
                        }

                        imdb = str(item['ImdbRating'])
                        kinopoisk = str(item['KinopoiskRating'])
                        rating = '&emsp;' + imdb + ' / ' + kinopoisk

                        country = item['Countries']
                        genres = item['Genres']

                        properties = {
                            #'Country': country,
                            #'PlotOutline': item['description'],
                            'Plot': item['Description'],
                            'Year': str(item['ReleaseYear']),
                            'Rating': imdb
                        }

                        country = '&emsp;(' + country + ')' if (country) else ''

                        label = common.replaceHTMLCodes( '[B]' + item['Title'] + '[/B]' + country + '&emsp;' + genres + rating )
                        title = common.replaceHTMLCodes( item['Title'] )

                        items.append({
                            'label': label,
                            'title': title,
                            'icon': cover,
                            'url': href,
                            'info': info,
                            'properties': properties,
                            'function': False,
                        })
                elif item_type == 'Serial':

                    id    = item['Id']
                    title = common.replaceHTMLCodes( item['Title'] )
                    label = common.replaceHTMLCodes( '[B]' + item['Title'] + '[/B]' )
                    icon  = item['PosterFile']

                    items.append({
                        'label': label,
                        'title': title,
                        'icon': icon,
                        'id': id,
                        'function': 'onair_serial'
                    })


    except:
        xbmc.log(traceback.format_exc(), xbmc.LOGERROR)

    return items