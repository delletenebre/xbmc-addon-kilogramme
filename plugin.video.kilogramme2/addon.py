# -*- coding: utf-8 -*-
import resources.lib.App as App
from resources.lib.App import P
import resources.lib.ts
import resources.lib.on_air
import resources.lib.cinema_online


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
            'url': P.get_url(action='subfolder')
        },
        {
            'label': 'Namba.Кинозал',
            'url': P.get_url(action='subfolder')
        }
    ]


if __name__ == '__main__':
    P.run()
