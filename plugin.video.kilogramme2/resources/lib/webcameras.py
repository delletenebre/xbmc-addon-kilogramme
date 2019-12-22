# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
from urlparse import urlparse, parse_qs


@P.cached(30)
@P.action()
def wc_index(params):
    items = []

    url = 'http://live.saimanet.kg'
    content = App.http_request(url)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for camera in html.find_all(class_='onemaincam'):
            try:
                camera = camera.find(class_='title').find('a')
                label = App.bs_get_text(camera)
                href = camera.get('href')

                content = App.http_request(url + href)
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

    url = 'https://elcat.kg/translation/'
    content = App.http_request(url)
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for div in html.find_all(class_='tranlation__item'):
            try:
                title = div.find('h2').text
                camera_number = div.get('id').split('_')[1]
                camera_div = html.find(id='start_stream' + camera_number)
                camera_src = camera_div.find('iframe').get('src')
                camera_name = camera_src.split('?')[1].split('&')[0].split('=')[1]
                
                items.append(
                    {
                        'label': title,
                        'url': 'https://webcam.elcat.kg:5443/LiveApp/streams/' + camera_name +'.m3u8?token=null ',
                        'is_playable': True
                    }
                )
            except:
                pass

    return items
