# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import App
from App import P
from App import H
import re


URL = 'http://www.ts.kg'


@P.action()
def wc_index(params):
    items = []
    content = App.http_request('http://smotri.kg')
    if content:
        html = BeautifulSoup(content, 'html.parser')
        for td in html.find_all('td'):
            label = App.bs_get_text(td.find('a'))

            for script in td.find_all('script'):
                cams = re.search('swf\.flashVar\(\"vid\",\"(.+?)\"\);', script.get_text())
                if cams:
                    items.append(
                        {
                            'label': label,
                            'url': cams.group(1) + ' timeout=1', # cams.group(1) + ' timeout=3',
                            'is_playable': True
                        }
                    )
    return items
