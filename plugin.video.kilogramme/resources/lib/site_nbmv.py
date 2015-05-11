#!/usr/bin/python
# -*- coding: utf-8 -*-
import re, json, urllib
from _header import *

BASE_URL   = 'http://movie.namba.kg/'
BASE_NAME  = 'Namba.Кинозал'
BASE_LABEL = 'nbmv'

@plugin.route('/site/' + BASE_LABEL)
def nbmv_index():
    item_list = get_categories(BASE_URL)
    items     = []
    
    if item_list:
        items = [{
            'label'     : item['title'],
            'path'      : plugin.url_for('nbmv_videos_by_category', id = item['id']),
            'thumbnail' : item['icon'],
        } for item in item_list]

        items = [{
            'label': set_color('[ Поиск ]', 'dialog', True),
            'path' : plugin.url_for('nbmv_search'),
            'icon' : get_local_icon('find')
        },{
            'label': set_color('Последние поступления', 'bright', True),
            'path' : plugin.url_for('nbmv_top30', type = 'new')
        },{
            'label': set_color('Популярные - ТОП 10', 'bright', True),
            'path' : plugin.url_for('nbmv_top30', type = 'popular')
        }] + items
    else:
        plugin.notify('Сервер недоступен', BASE_NAME, image=get_local_icon('noty_' + BASE_LABEL))
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/top30/<type>')
def nbmv_top30(type):
    item_list = get_top30(type)
    items = [{
        'label'      : item['title'],
        'path'       : item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'],
        'properties' : item['properties'],
        'is_playable': True
    } for item in item_list]
    
    return items


@plugin.route('/site/' + BASE_LABEL + '/category/<id>/page/<page>', name='nbmv_videos_by_category_pagination')
@plugin.route('/site/' + BASE_LABEL + '/category/<id>',             name='nbmv_videos_by_category', options={'page': '1'})
def nbmv_videos_by_category(id, page = '1'):
    item_list = get_videos_by_category(id, page)
    
    items = [{
        'label'     : item['title'],
        'path'      : plugin.url_for('nbmv_movie', id = item['id']),
        'thumbnail' : item['icon'],
    } for item in item_list['items']]
    
    if(item_list['pagination']):
        for item in item_list['pagination']:
            items.insert(0, {
                'label': item['label'],
                'path' : plugin.url_for('nbmv_videos_by_category_pagination', id = id, page = item['page']) if item['search'] == False else plugin.url_for('nbmv_go_to_page', id = id, page = item['page']),
                'icon' : item['icon'],
            })
    
    if(page == '1'):
        return items
    else:
        return plugin.finish(items, update_listing=True)


@plugin.route('/site/' + BASE_LABEL + '/movie/<id>')
def nbmv_movie(id):
    item_list = get_movie(id)
    items = [{
        'label'      : item['title'],
        'path'       : item['url'],
        'thumbnail'  : item['icon'],
        'info'       : item['info'],
        'properties' : item['properties'],
        'is_playable': True
    } for item in item_list]
    
    return items

@plugin.route('/site/' + BASE_LABEL + '/to_page/<id>/<page>')
def nbmv_go_to_page(id, page = '1'):
    search_page = common.getUserInputNumbers('Укажите страницу')
    if(search_page):
        page = search_page if (int(search_page) > 0) else '1'

        items = nbmv_videos_by_category(id, page)

        return plugin.finish(items, update_listing=True)
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL + '/category/' + str(id) + '/page/' + str(page))


@plugin.route('/site/' + BASE_LABEL + '/search')
def nbmv_search():
    search_val = plugin.keyboard('', 'Что ищете?')
    if(search_val):
        item_list = get_search_results(str(search_val))
        
        items = [{
            'label'      : item['title'],
            'path'       : item['url'],
            'thumbnail'  : item['icon'],
            'info'       : item['info'],
            'properties' : item['properties'],
            'is_playable': True
        } for item in item_list]
        
        return items
    else:
        plugin.redirect('plugin://'+plugin.id+'/site/' + BASE_LABEL)




#method
def get_search_results(query):
    items = []
    try:
        result = common.fetchPage({'link': 'http://namba.kg/api/?service=home&action=search&type=movie&query=' + urllib.quote(str(query)) + '&page=1&sort=desc&country_id=0&city_id=0'})
        if result['status'] == 200:
            result_json = json.loads(result['content'])
            
            for item in result_json['movies']:
                id    = item['id']
                items = items + get_movie(id, False)
    except: pass
    return items

#method
def get_top30(type = 'new'):
    #type = popular || new
    items = []
    try:
        result = common.fetchPage({'link': 'http://namba.kg/api/?type=' + type + '&service=home&action=movies&limit=10'})
        if result['status'] == 200:
            result_json = json.loads(result['content'])
            
            for item in result_json:
                title = common.replaceHTMLCodes( item['title'] )
                id    = item['video_id']
                cover = item['cover_url'] if item['cover_url'] != '' else item['image']

                items.append(get_movie_item(id, cover))
    except: pass
    return items


#method
def get_categories(url):
    items = []
    try:
        result = common.fetchPage({'link': url})
        if result['status'] == 200:
            html = result['content']
            
            categories = common.parseDOM(html, 'ul', attrs={'class':'categories-menu'})
            categories_li = common.parseDOM(categories, 'li')

            for item in categories_li:
                title = common.parseDOM(item, 'a')
                href  = common.parseDOM(item, 'a', ret='href')
                id    = href[0][href[0].index('=')+1:]

                items.append({'title':title[0], 'icon':'', 'id':id})
    except: pass
    return items
    
#method
def get_videos_by_category(id, page = '1'):
    pagination_items = []
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'category.php?id=' + str(id) + '&p=' + str(page)})
        if result['status'] == 200:
            html = result['content']

            #======== pagination ========#
            pagination_items = KG_get_pagination(page, re.compile('var paginator_container = new Paginator\( "paginator_container", (.+?),').findall(re.sub('\s+', ' ', html))[0])
            #======== END pagination ========#

            
            movies = common.parseDOM(html, 'ul', attrs={'class':'result-block'})
            movies_li = common.parseDOM(movies, 'li')

            for item in movies_li:
                title = common.parseDOM(item, 'img', ret='title')
                href  = common.parseDOM(item, 'a', ret='href')
                icon  = common.parseDOM(item, 'img', ret='src')
                id    = href[0][href[0].index('=')+1:]

                items.append({'title':common.replaceHTMLCodes( title[0] ), 'icon':icon[0], 'id':id})
    except: pass
    return {'items':items, 'pagination':pagination_items}
    

#method
def get_movie(id, watch = True):
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL + 'watch.php?id=' + str(id)})
        if result['status'] == 200:
            html     = result['content']
            video_id = re.compile('<param value="config=.+?__(.+?)" name="flashvars">').findall(html)[0]
            
            div_cover = common.parseDOM(html, 'div', attrs={'class':'movie-cover'})
            try:
                icon  = common.parseDOM(div_cover, 'img', ret='src')[0]
            except:
                icon  = ''
            
            items.append(get_movie_item(video_id, icon, watch))
    except: pass
    return items


def get_movie_item(id, cover = '', watch = False):
    movie_item = {}
    try:
        result = common.fetchPage({'link': 'http://namba.kg/api/?service=video&action=video&id=' + id})
        if result['status'] == 200:
            result_json = json.loads(result['content'])

            title = result_json['video']['title']
            if watch == True:
                title = set_color('ПРОСМОТР: ', 'bold').decode('utf-8') + title

            href  = result_json['video']['download']['flv']
            info  = {
                'duration'     : str2minutes(result_json['video']['duration']),
                'plot'         : result_json['video']['description'],
            }
            properties = {
                'fanart_image' : result_json['video']['big_preview'],
            }
            

            movie_item = {'title':title, 'icon':cover, 'url':href, 'info':info, 'properties':properties}
    except: pass
    return movie_item