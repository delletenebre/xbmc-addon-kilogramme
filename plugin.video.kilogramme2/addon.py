# -*- coding: utf-8 -*-
import resources.lib.App as App
from resources.lib.App import P
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
        }
    ]


if __name__ == '__main__':
    P.run()
