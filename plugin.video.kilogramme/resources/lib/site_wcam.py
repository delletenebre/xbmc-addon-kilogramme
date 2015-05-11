#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2, re, json, traceback
from _header import *

BASE_NAME_SAIMA  = common.replaceHTMLCodes('&emsp;SAIMA TELECOM&emsp;live.saimanet.kg')
BASE_URL_SAIMA   = 'http://live.saimanet.kg/sys/api/get_cams'

BASE_NAME_SMOTRI = common.replaceHTMLCodes('&emsp;SMOTRI.KG')
BASE_URL_SMOTRI  = 'http://www.smotri.kg/'

BASE_NAME_KT     = common.replaceHTMLCodes('&emsp;КыргызТелеком'.decode('utf-8'))
BASE_URL_KT      = 'http://kt.kg'

BASE_NAME  = 'Веб-камеры'
BASE_LABEL = 'wc'

@plugin.route('/site/' + BASE_LABEL)
def wc_index():
    item_list = get_cameras()

    items     = [{
        'label'       : item['name'],
        'path'        : item['url'],
        'thumbnail'   : item['icon'],
        'is_playable' : True
    } for item in item_list]

    return items





def get_cameras():
    items = []
    try:
        result = common.fetchPage({'link': BASE_URL_SAIMA})
        if result['status'] == 200:
            data = json.loads(result['content'])
            #xbmc.log('Json list : ' + str(data))
            for item in data:
                try:
                    #xbmc.log('Json item : ' + str(item['title']))
                    items.append({'name': item['title'], 'url':item['url'], 'icon':item['image']})
                except:
                    xbmc.log('json exception '+ str(sys.exc_info()[0]))
                    traceback.print_exc()
                    pass
    except: pass

    try:
        icon  = 'http://kt.kg/bitrix/templates/ktnet_copy/images/logo.gif'
        name = set_color('Чуй - фонтан', 'bold') + BASE_NAME_KT
        items.append({'name':common.replaceHTMLCodes( name ), 'url':'rtmp://213.145.131.243:5010/live', 'icon':icon})
    except: pass

    try:
        result = common.fetchPage({'link': BASE_URL_SMOTRI})
        if result['status'] == 200:
            cams = re.compile('>([^<]{6,})<\/a><\/span><\/span>[^:]*(rtmp[^"]+)[^\/]*\/([^"]+)').findall(result['content'])
            for cam in cams:
                try:
                    xbmc.log('Json item : ' + str(item['title']))
                    items.append({'name': cam[0], 'url':cam[1], 'icon':BASE_URL_SMOTRI + cam[2]})
                except:
                    xbmc.log('json exception '+ str(sys.exc_info()[0]))
                    traceback.print_exc()
                    pass
    except:
        xbmc.log('json exception '+ str(sys.exc_info()[0]))
        traceback.print_exc()
        pass


    #xbmc.log('Exit list : ' + str(items))
    return items
