# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P


@P.cached(30)
@P.action()
def wc_index(params):
    items = []
    url_format = 'http://212.42.105.251:8080/%s/tracks-v1/index.m3u8'
    cameras = {
        'Площадь Победы': 'pobeda',
        'Кумысолечебница "Байтур"': 'baytur',
        'Южная магистраль': 'asanbai1',
        'Ибраимова/Кулатова': 'record',
        '6 м-н': '6mk',
        'ГБ "Тоо-Ашуу" - 2': 'gbashuu2',
        'ГБ "Тоо-Ашуу" - 1': 'gbashuu1',
        'Проект ВОЛС Тоо Ашуу 2': 'tooashuu2',
        'Проект ВОЛС Тоо Ашуу 1': 'tooashuu1',
        'Советская - Боконбаева - 2': 'sov2',
        'Советская - Боконбаева - 1': 'sov1',
        'Алма-Атинская/Ахунбаева': 'ahunbaeva',
        'Чуй/Советская (ОАО Кыргызтелеком)': 'chui',
        'Нарын': 'naryn',
        'Бостери (ОАО Кыргызтелеком)': 'bosteri',
        'Кара-Балта площадь им. Ленина': 'kb',
        'Ибраимова - Боконбаева': 'ibraimova',
        'Сулайман Тоо - город Ош': 'osh'
    }

    for name in sorted(cameras):
        items.append({
            'label': name,
            'url': url_format % cameras[name],
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
