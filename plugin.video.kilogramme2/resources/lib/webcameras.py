# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
from urlparse import urlparse, parse_qs


URL = 'http://smotri.kg%s'

@P.cached(30)
@P.action()
def wc_index(params):
    items = []
    
    url_format = 'rtmp://212.42.105.251:1935/%s/?token=%s'
    # url_format = 'http://212.42.105.251:8080/record/mpegts?token=%s'
    # url_format = 'http://212.42.105.251:8080/record/tracks-v1/mono.m3u8?token=%s'

    content = App.http_request(URL % '/')
    if content:
        html = BeautifulSoup(content, 'html.parser')
        container = html.find(class_='view-cameras')
        for link in container.find_all('a'):
            if link is not None:
                url = link.get('href')
                content = App.http_request(URL % url)
                if content:
                    html = BeautifulSoup(content, 'html.parser')
                    iframe = html.find('iframe')
                    if iframe is not None:
                        url = iframe.get('src')
                        parsed_url = urlparse(url)
                        url_splitted = url.split('/')
                        params = parse_qs(parsed_url.query)
                        if 'token' in params:
                            token = params['token'][0].strip()
                            items.append({
                                'label': link.get_text(),
                                'url': url_format % (url_splitted[3], token),
                                'is_playable': True
                            })

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
    return items
