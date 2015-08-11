#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmcplugin
from _header import *
import site_tskg, site_ockg, site_onair, site_wcam, site_ontvkg, site_nbmv, site_nbts
from xbmcswift2 import actions

@plugin.route('/')
def index():
    items = [
        {'label': site_tskg.BASE_NAME, 'icon' : get_local_icon(site_tskg.BASE_LABEL), 'path': plugin.url_for(site_tskg.BASE_LABEL + '_index')},
        {'label': site_ockg.BASE_NAME, 'icon' : get_local_icon(site_ockg.BASE_LABEL), 'path': plugin.url_for(site_ockg.BASE_LABEL + '_index')},
        {'label': site_onair.BASE_NAME, 'icon' : get_local_icon(site_onair.BASE_LABEL), 'path': plugin.url_for(site_onair.BASE_LABEL + '_index')},
        {'label': site_ontvkg.BASE_NAME, 'icon' : get_local_icon(site_ontvkg.BASE_LABEL), 'path': plugin.url_for(site_ontvkg.BASE_LABEL + '_index')},
        {'label': site_nbmv.BASE_NAME, 'icon' : get_local_icon(site_nbmv.BASE_LABEL), 'path': plugin.url_for(site_nbmv.BASE_LABEL + '_index')},
        {'label': site_nbts.BASE_NAME, 'icon' : get_local_icon(site_nbts.BASE_LABEL), 'path': plugin.url_for(site_nbts.BASE_LABEL + '_index')},
        {'label': site_wcam.BASE_NAME, 'icon' : get_local_icon(site_wcam.BASE_LABEL), 'path': plugin.url_for(site_wcam.BASE_LABEL + '_index')},
        {'label': set_color('Настройки плагина'.decode('utf-8'), 'dialog'), 'icon': get_local_icon('sett'), 'path': plugin.url_for('run_settings'), 'is_not_folder':True},
        {'label': set_color('Очистить кэш'.decode('utf-8'), 'dialog'), 'icon': get_local_icon('sett'), 'path': plugin.url_for('run_clear_cache'), 'is_not_folder':True},
    ]
    return items
    
@plugin.route('/settings')
def run_settings():
    plugin.open_settings()
    
@plugin.route('/clear_cache')
def run_clear_cache():
    storages = plugin.list_storages()
    storages.append('.functions')
    for name in storages:
        storage = plugin.get_storage(name)
        storage.clear()
        storage.sync()
    
    plugin.notify('Кэш успешно очищен', 'KiloGramme', image=get_local_icon('noty_icon'))