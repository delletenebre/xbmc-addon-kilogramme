# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
import re


@P.cached(30)
@P.action()
def wc_index(params):
    items = []
    URL = 'http://smotri.kg'
    content = App.http_request(URL)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        div = html.find(class_='view-content')
        for camera in div.find_all('a'):
            try:
                label = App.bs_get_text(camera)
                href = camera.get('href')

                content = App.http_request(URL + href)
                if content:
                    play_url = re.compile('\"rtmp://(.+?)\"').findall(content)[0]
                    if play_url:
                        items.append(
                            {
                                'label': label,
                                'url': 'rtmp://' + play_url,
                                'is_playable': True
                            }
                        )
            except IOError:
                pass

    URL = 'http://live.saimanet.kg'
    content = App.http_request(URL)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for camera in html.find_all(class_='onemaincam'):
            try:
                camera = camera.find(class_='title').find('a')
                label = App.bs_get_text(camera)
                href = camera.get('href')

                content = App.http_request(URL + href)
                if content:
                    html1 = BeautifulSoup(content, 'html.parser')
                    source = html1.find('source')
                    items.append(
                        {
                            'label': label,
                            'url': source.get('src'),
                            'is_playable': True
                        }
                    )
            except:
                pass
    return items
