#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, re
from urllib import urlencode, quote_plus, unquote_plus
import xbmc, xbmcgui, xbmcaddon, xbmcplugin


class Plugin():
    def __init__(self, name=None):
        self._hos = int(sys.argv[1])
        
        self._addon     = xbmcaddon.Addon()
        self._addon_id  = self._addon.getAddonInfo('id')
        self._name      = name or self._addon.getAddonInfo('name')
        self._path      = self._addon.getAddonInfo('path')
        self._path_libs = os.path.join( self._path, 'resources', 'lib', 'libs')
        
    
    def get_addon_id(self):
        return self._addon_id
    
    
    def url_for(self, func=None, params = {}):
        if re.findall(r'https?://\S+', func):
            return func
        else:
            params['func'] = func
            return self._make_request(params)

    def add_items(self, items = [{}]):
        result_items = []
        
        for item in items:
            #try:
            result_items.append(xbmcplugin.addDirectoryItem(handle = self._hos, url = item['path'], listitem=self._create_item(item), isFolder=item['isFolder']))
            #except:
                #result_items.append(xbmcplugin.addDirectoryItem(handle=self._hos, url=item['url'], listitem=self._create_item(item), isFolder=item['isFolder']))
                
        return result_items
    
    def _create_item(self, info):
        default_item = {
            'label'         : '',
            'label2'        : '',
            'year'          : '',
            'icon'          : '',
            'country'       : '',
            'genre'         : '',
            'rating'        : None, #Shows the IMDB rating of the currently selected movie in a list or thumb control
            'votes'         : '', #Shows the IMDB votes of the currently selected movie in a list or thumb control (Future Gotham addition)
            'RatingAndVotes': '', #Shows the IMDB rating and votes of the currently selected movie in a list or thumb control
            #'duration'      : None, #Shows the song or movie duration of the currently selected movie in a list or thumb control
            'trailer'       : '', #Shows the full trailer path with filename of the currently selected movie in a list or thumb control
            'Tagline'       : '', #Small Summary of current Video in a list or thumb control
            'PlotOutline'   : '', #Small Summary of current Video in a list or thumb control
            'plot'          : '', #Complete Text Summary of Video in a list or thumb control
            
            #'size'          : '',
            'thumb'         : '',
            'fanart'        : ''
        }
        i = dict(default_item)
        i.update(info)
            
        item = xbmcgui.ListItem(i['label'], iconImage='DefaultVideo.png' if i['isFolder'] == False else 'DefaultFolder.png', thumbnailImage=i['thumb'] or i['icon'])
            
        if i['fanart'] != None:
            item.setProperty('fanart_image', i['fanart'])
        
        if i['isFolder'] == False:
            del i['isFolder']
            del i['path']
            item.setInfo('Video', i)

        return item
        
    def add_to_playlist(self, items = [{}], type='video'):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        for item in items:
            listitem = xbmcgui.ListItem(item['label'], iconImage="DefaultVideo.png", thumbnailImage=item['icon'])
            listitem.setInfo( type='Video', infoLabels=item )
            
            playlist.add(item['url'], listitem)
				
			
		

    def finish(self):
        return xbmcplugin.endOfDirectory(self._hos)
    
    
    def get_local_icon(self, name):
        return os.path.join(self._path, 'resources', 'media', str(name))
        
    def get_path_libs(self):
        return self._path_libs
    
    
    def _make_request(self, params):
        return '%s?%s' % (sys.argv[0], urlencode(params))
    
    def parse_params(self):
        paramstring = sys.argv[2]
        param=[]
        if len(paramstring)>=2:
            params=paramstring
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        if len(param) > 0:
            for cur in param:
                param[cur] = unquote_plus(param[cur])
        return param