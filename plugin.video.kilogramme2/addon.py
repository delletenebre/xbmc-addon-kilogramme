# -*- coding: utf-8 -*-
import resources.lib.App as App
from resources.lib.App import P
import resources.lib.ts
import resources.lib.on_air
import resources.lib.cinema_online
import resources.lib.namba_movies
import resources.lib.webcameras


@P.action()
def root(params):
    return [
        {
            'label': 'TS.KG',
            'icon': App.get_media('ts'),
            'url': P.get_url(action='ts_index')
        },
        {
            'label': 'OnAir',
            'icon': App.get_media('onair'),
            'url': P.get_url(action='oa_index')
        },
        {
            'label': 'Cinema Online',
            'icon': App.get_media('cinema_online'),
            'url': P.get_url(action='co_index')
        },
        {
            'label': 'Namba.Сериалы',
            'icon': App.get_media('namba_tvshows'),
            'url': P.get_url(action='subfolder')
        },
        {
            'label': 'Namba.Кинозал',
            'icon': App.get_media('namba_movies'),
            'url': P.get_url(action='nm_index')
        },
        {
            'label': 'Веб-камеры',
            'icon': App.get_media('webcamera'),
            'url': P.get_url(action='wc_index')
        }
    ]


if __name__ == '__main__':
    P.run()
