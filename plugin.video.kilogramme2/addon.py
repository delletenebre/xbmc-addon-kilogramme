# -*- coding: utf-8 -*-
import resources.lib.App as App
from resources.lib.App import P
import shutil
import os
import resources.lib.ts
import resources.lib.on_air
import resources.lib.cinema_online
import resources.lib.namba_movies
import resources.lib.namba_serials
import resources.lib.webcameras


@P.action()
def root(params):
    P.log_error(str(P.get_setting('string_formatting')))
    return [
        {
            'label': 'TS.KG',
            'icon': App.get_media('ts'),
            'url': P.get_url(action='ts_index')
        },
        {
            'label': 'Cinema Online',
            'icon': App.get_media('cinema_online'),
            'url': P.get_url(action='co_index')
        },
        {
            'label': 'Namba.Кинозал',
            'icon': App.get_media('namba_movies'),
            'url': P.get_url(action='nm_index')
        },
        {
            'label': 'Namba.Сериалы',
            'icon': App.get_media('namba_serials'),
            'url': P.get_url(action='ns_index')
        },
        {
            'label': 'Веб-камеры',
            'icon': App.get_media('webcamera'),
            'url': P.get_url(action='wc_index')
        },
        {
            'label': 'Очистить кэш',
            'icon': App.get_media('sett'),
            'url': P.get_url(action='clear_cache'),
            'is_folder': False
        }
    ]


@P.action()
def clear_cache(params):
    plugin_cache_file = App.ADDON_FOLDER + '__cache__.pcl'
    if os.path.exists(plugin_cache_file):
        os.remove(plugin_cache_file)
    shutil.rmtree(App.ADDON_FOLDER + '/.cache')
    # storage = P.get_storage('__cache__.pcl')
    # storage.clear()
    # storage.flush()
    App.notification('Кэш успешно очищен', '', 'info')

if __name__ == '__main__':
    P.run()
