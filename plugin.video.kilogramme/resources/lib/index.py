#!/usr/bin/python
# -*- coding: utf-8 -*-

from _header import *
import site_tskg, site_ockg

@plugin.route('/')
def index():
    items = [
        {'label': site_tskg.BASE_NAME, 'icon' : get_local_icon(site_tskg.BASE_LABEL), 'path': plugin.url_for('ts_index', label = site_tskg.BASE_LABEL)},
        {'label': site_ockg.BASE_NAME, 'icon' : get_local_icon(site_ockg.BASE_LABEL), 'path': plugin.url_for('oc_index', label = site_ockg.BASE_LABEL)},
    ]
    
    return items