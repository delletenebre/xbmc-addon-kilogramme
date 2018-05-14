# -*- coding: utf-8 -*-

from resources.lib.simpleplugin import Plugin
import httplib2
import xbmc
import xbmcgui
import re
import HTMLParser
import urllib
import socket
import traceback
import types


P = Plugin()


PLUGIN_ID = P.addon.getAddonInfo('id')
MEDIA_URL = 'special://home/addons/{0}/resources/media/'.format(PLUGIN_ID)
ADDON_FOLDER = xbmc.translatePath('special://profile/addon_data/' + PLUGIN_ID)

STR_NO_DATA = 'n/d'
STR_LIST_DELIMITER = '[/B] / [B]'

VIEW_MODES = {
    'skin.estuary': {
        'files': {
            'type': 'files',
            'mode': 55,
        },
        'movies': {
            'type': 'files',
            'mode': 55,
        },
        'tvshows': {
            'type': 'tvshows',
            'mode': 55
        },
        'episodes': {
            'type': 'episodes',
            'mode': 50,
        }
    },
    'skin.confluence': {
        'files': {
            'type': 'files',
            'mode': 50
        },
        'movies': {
            'type': 'movies',
            'mode': 504
        },
        'tvshows': {
            'type': 'tvshows',
            'mode': 504
        },
        'episodes': {
            'type': 'episodes',
            'mode': 50
        }
    },
    'skin.unknown': {
        'files': {
            'type': 'files',
            'mode': 55,
        },
        'movies': {
            'type': 'files',
            'mode': 55,
        },
        'tvshows': {
            'type': 'files',
            'mode': 55
        },
        'episodes': {
            'type': 'files',
            'mode': 55,
        }
    },
}


H = httplib2.Http(ADDON_FOLDER + '/.cache', disable_ssl_certificate_validation=True)


def http_request(url, method='GET', data={}):
    try:
        (resp_headers, content) = H.request(
            url, method, urllib.urlencode(data),
            headers={
                'Content-type': 'application/x-www-form-urlencoded' if method.lower() == 'post' else 'application/octet-stream',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
            }
        )
        if resp_headers.status == 200:
            return content
        else:
            noty('server_error')
            P.log_error(traceback.format_exc)
    except httplib2.ServerNotFoundError:
        noty('internet_check')
        P.log_error(traceback.format_exc)
    except socket.timeout:
        noty('internet_timeout')
        P.log_error(traceback.format_exc)

    return None


def get_skin_name():
    return xbmc.getSkinDir()


def clear_xbmc_tags(string):
    return string.replace('[B]', '').replace('[/B]', '')


def create_listing(items, content='files', update_listing=False):
    skin_name = get_skin_name()
    if skin_name not in VIEW_MODES:
        skin_name = 'skin.unknown'
    view = VIEW_MODES[skin_name][content]
    return P.create_listing(items, succeeded=(len(items) > 0), content=view['type'], view_mode=view['mode'], update_listing=update_listing)


def keyboard(default=None, heading=None, hidden=False, numeric=False):
    '''Displays the keyboard input window to the user. If the user does not
    cancel the modal, the value entered by the user will be returned.

    :param default: The placeholder text used to prepopulate the input field.
    :param heading: The heading for the window. Defaults to the current
                    addon's name. If you require a blank heading, pass an
                    empty string.
    :param hidden: Whether or not the input field should be masked with
                   stars, e.g. a password field.
    '''
    if heading is None:
        heading = P.addon.getAddonInfo('name')
    if default is None:
        default = ''
    if numeric:
        keyboard = xbmcgui.Dialog()
        return keyboard.numeric(0, heading)
    else:
        keyboard = xbmc.Keyboard(default, heading, hidden)
    keyboard.doModal()
    if keyboard.isConfirmed():
        return keyboard.getText()


def notification(heading, message, icon='info', time=3000, sound=True):
    if icon == 'warning':
        icon = xbmcgui.NOTIFICATION_WARNING
    elif icon == 'error':
        icon = xbmcgui.NOTIFICATION_ERROR
    else:
        icon = xbmcgui.NOTIFICATION_INFO

    xbmcgui.Dialog().notification(heading, message, icon, time, sound)


def noty(type):
    if type == 'internet_check':
        notification('Отсутствует подключение', 'Проверьте подключение к сети Интернет', 'warning', 5000)
    elif type == 'internet_timeout':
        notification('Сервер не отвечает', 'Попробуйте ещё раз', 'warning', 5000)
    elif type == 'server_error':
        notification('Сервер недоступен', 'Проверьте сайт в браузере', 'warning', 5000)
    elif type == 'no_search_results':
        notification('Не найдено', 'Измените поисковой запрос', 'info')
    elif type == 'playlist_empty':
        notification('Плейлист не создан', 'Попробуйте ещё раз', 'warning', 5000)


def get_media(name, extension='png'):
    return '{0}.{1}'.format(MEDIA_URL + name, extension)


def get_color(color):
    colors = {
        'pagination': 'FF11b500',
        'dialog': 'FFe37101',
        'light': 'FF42aae0',
        'bright': 'F0FF00FF',
        'label-danger': 'FFd9534f',
        'label-success': 'FF5cb85c',
        'label-info': 'FF5bc0de',
    }

    return colors[color] if color in colors else color


def format_color(text, color):
    if P.get_setting('string_formatting'):
        text = '[COLOR %s]%s[/COLOR]' % (get_color(color), text)
    return text


def format_bold(text):
    if P.get_setting('string_formatting'):
        text = '[B]%s[/B]' % (text) if text != STR_NO_DATA else text
    return text


def format_description(country='', genre='', description='', director='', episodes='', rating=''):
    if country and len(country) == 2:
        country = get_country(country)
    if country and country != STR_NO_DATA:
        country = format_bold(country)
    if genre and genre != STR_NO_DATA:
        genre = format_bold(genre)
    if director and director != STR_NO_DATA:
        director = format_bold(director)

    result = ''
    if episodes:
        result += 'Эпизодов: {0}\n'.format(episodes)

    if country:
        result += 'Страна: {0}\n'.format(country)

    if genre:
        result += 'Жанр: {0}\n'.format(genre)

    if director:
        result += 'Режиссёр: {0}\n'.format(director)

    if rating:
        result += 'Рейтинг: {0}\n'.format(format_bold(rating))

    if description:
        if result:
            result += '\n'
        result += '{0}\n'.format(description)

    return replace_html_codes(result.decode('utf-8'))


def make_root(url, path):
    return '/%s/%s' % (url, path)


def replace_html_codes(text):
    if not P.get_setting('string_formatting'):
        text = text.replace('&emsp;', '   ')
    text = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', to_utf8(text))
    text = HTMLParser.HTMLParser().unescape(text)
    text = text.replace('&amp;', '&')
    return text


def to_utf8(data):
    return data
    try:
        return data.decode('utf8', 'xmlcharrefreplace')
    except:
        s = u''
        for i in data:
            try:
                i.decode('utf8', 'xmlcharrefreplace')
            except:
                continue
            else:
                s += i
        return s


def bs_get_text(element):
    if element is not None:
        return element.get_text()
    return ''


def bs_get_text_with_newlines(element):
    text = ''
    if element is not None:
        for elem in element.recursiveChildGenerator():
            if isinstance(elem, types.StringTypes):
                text += elem.strip()
            elif elem.name == 'br':
                text += '\n'
    return text


def create_playlist(items=[{}], type='video'):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for item in items:
        listitem = P.create_list_item(item)
        playlist.add(item['url'], listitem)


def explode_info_string(string):
    return STR_LIST_DELIMITER.join(string).encode('utf-8')


def timestring2seconds(timestring):
    ftr = [3600, 60, 1]
    return sum([a * b for a, b in zip(ftr, map(int, timestring.split(':')))])


def remove_double_spaces(str):
    return ' '.join(str.split())


def get_country(code):
    countries = {
        'AU': 'Австралия',
        'AT': 'Австрия',
        'AZ': 'Азербайджан',
        'AX': 'Аландские о-ва',
        'AL': 'Албания',
        'DZ': 'Алжир',
        'AS': 'Американское Самоа',
        'AI': 'Ангилья',
        'AO': 'Ангола',
        'AD': 'Андорра',
        'AQ': 'Антарктида',
        'AG': 'Антигуа и Барбуда',
        'AR': 'Аргентина',
        'AM': 'Армения',
        'AW': 'Аруба',
        'AF': 'Афганистан',
        'BS': 'Багамские о-ва',
        'BD': 'Бангладеш',
        'BB': 'Барбадос',
        'BH': 'Бахрейн',
        'BY': 'Беларусь',
        'BZ': 'Белиз',
        'BE': 'Бельгия',
        'BJ': 'Бенин',
        'BM': 'Бермудские о-ва',
        'BG': 'Болгария',
        'BO': 'Боливия',
        'BQ': 'Бонэйр, Синт-Эстатиус и Саба',
        'BA': 'Босния и Герцеговина',
        'BW': 'Ботсвана',
        'BR': 'Бразилия',
        'IO': 'Британская территория в Индийском океане',
        'BN': 'Бруней-Даруссалам',
        'BF': 'Буркина-Фасо',
        'BI': 'Бурунди',
        'BT': 'Бутан',
        'VU': 'Вануату',
        'VA': 'Ватикан',
        'GB': 'Великобритания',
        'UK': 'Великобритания',
        'HU': 'Венгрия',
        'VE': 'Венесуэла',
        'VG': 'Виргинские о-ва (Британские)',
        'VI': 'Виргинские о-ва (США)',
        'UM': 'Внешние малые о-ва (США)',
        'TL': 'Восточный Тимор',
        'VN': 'Вьетнам',
        'GA': 'Габон',
        'HT': 'Гаити',
        'GY': 'Гайана',
        'GM': 'Гамбия',
        'GH': 'Гана',
        'GP': 'Гваделупа',
        'GT': 'Гватемала',
        'GN': 'Гвинея',
        'GW': 'Гвинея-Бисау',
        'DE': 'Германия',
        'GG': 'Гернси',
        'GI': 'Гибралтар',
        'HN': 'Гондурас',
        'HK': 'Гонконг',
        'GD': 'Гренада',
        'GL': 'Гренландия',
        'GR': 'Греция',
        'GE': 'Грузия',
        'GU': 'Гуам',
        'DK': 'Дания',
        'JE': 'Джерси',
        'DJ': 'Джибути',
        'DG': 'Диего-Гарсия',
        'DM': 'Доминика',
        'DO': 'Доминиканская Республика',
        'EG': 'Египет',
        'ZM': 'Замбия',
        'EH': 'Западная Сахара',
        'ZW': 'Зимбабве',
        'IL': 'Израиль',
        'IN': 'Индия',
        'ID': 'Индонезия',
        'JO': 'Иордания',
        'IQ': 'Ирак',
        'IR': 'Иран',
        'IE': 'Ирландия',
        'IS': 'Исландия',
        'ES': 'Испания',
        'IT': 'Италия',
        'YE': 'Йемен',
        'CV': 'Кабо-Верде',
        'KZ': 'Казахстан',
        'KY': 'Каймановы о-ва',
        'KH': 'Камбоджа',
        'CM': 'Камерун',
        'CA': 'Канада',
        'IC': 'Канарские о-ва',
        'QA': 'Катар',
        'KE': 'Кения',
        'CY': 'Кипр',
        'KG': 'Кыргызстан',
        'KI': 'Кирибати',
        'CN': 'Китай',
        'KP': 'КНДР',
        'CC': 'Кокосовые о-ва',
        'CO': 'Колумбия',
        'KM': 'Коморские о-ва',
        'CG': 'Конго - Браззавиль',
        'CD': 'Конго - Киншаса',
        'XK': 'Косово',
        'CR': 'Коста-Рика',
        'CI': 'Кот-д’Ивуар',
        'CU': 'Куба',
        'KW': 'Кувейт',
        'CW': 'Кюрасао',
        'LA': 'Лаос',
        'LV': 'Латвия',
        'LS': 'Лесото',
        'LR': 'Либерия',
        'LB': 'Ливан',
        'LY': 'Ливия',
        'LT': 'Литва',
        'LI': 'Лихтенштейн',
        'LU': 'Люксембург',
        'MU': 'Маврикий',
        'MR': 'Мавритания',
        'MG': 'Мадагаскар',
        'YT': 'Майотта',
        'MO': 'Макао',
        'MK': 'Македония',
        'MW': 'Малави',
        'MY': 'Малайзия',
        'ML': 'Мали',
        'MV': 'Мальдивские о-ва',
        'MT': 'Мальта',
        'MA': 'Марокко',
        'MQ': 'Мартиника',
        'MH': 'Маршалловы о-ва',
        'MX': 'Мексика',
        'MZ': 'Мозамбик',
        'MD': 'Молдова',
        'MC': 'Монако',
        'MN': 'Монголия',
        'MS': 'Монтсеррат',
        'MM': 'Мьянма (Бирма)',
        'NA': 'Намибия',
        'NR': 'Науру',
        'NP': 'Непал',
        'NE': 'Нигер',
        'NG': 'Нигерия',
        'NL': 'Нидерланды',
        'NI': 'Никарагуа',
        'NU': 'Ниуэ',
        'NZ': 'Новая Зеландия',
        'NC': 'Новая Каледония',
        'NO': 'Норвегия',
        'AC': 'о-в Вознесения',
        'IM': 'О-в Мэн',
        'NF': 'о-в Норфолк',
        'CX': 'о-в Рождества',
        'SH': 'О-в Св. Елены',
        'CK': 'о-ва Кука',
        'TC': 'О-ва Тёркс и Кайкос',
        'AE': 'ОАЭ',
        'OM': 'Оман',
        'PK': 'Пакистан',
        'PW': 'Палау',
        'PS': 'Палестинские территории',
        'PA': 'Панама',
        'PG': 'Папуа – Новая Гвинея',
        'PY': 'Парагвай',
        'PE': 'Перу',
        'PN': 'Питкэрн',
        'PL': 'Польша',
        'PT': 'Португалия',
        'PR': 'Пуэрто-Рико',
        'KR': 'Южная Корея',
        'RE': 'Реюньон',
        'RU': 'Россия',
        'RW': 'Руанда',
        'RO': 'Румыния',
        'SV': 'Сальвадор',
        'WS': 'Самоа',
        'SM': 'Сан-Марино',
        'ST': 'Сан-Томе и Принсипи',
        'SA': 'Саудовская Аравия',
        'SZ': 'Свазиленд',
        'MP': 'Северные Марианские о-ва',
        'SC': 'Сейшельские о-ва',
        'BL': 'Сен-Бартельми',
        'MF': 'Сен-Мартен',
        'PM': 'Сен-Пьер и Микелон',
        'SN': 'Сенегал',
        'VC': 'Сент-Винсент и Гренадины',
        'KN': 'Сент-Китс и Невис',
        'LC': 'Сент-Люсия',
        'RS': 'Сербия',
        'EA': 'Сеута и Мелилья',
        'SG': 'Сингапур',
        'SX': 'Синт-Мартен',
        'SY': 'Сирия',
        'SK': 'Словакия',
        'SI': 'Словения',
        'US': 'США',
        'SB': 'Соломоновы о-ва',
        'SO': 'Сомали',
        'SD': 'Судан',
        'SR': 'Суринам',
        'SL': 'Сьерра-Леоне',
        'TJ': 'Таджикистан',
        'TH': 'Таиланд',
        'TW': 'Тайвань',
        'TZ': 'Танзания',
        'TG': 'Того',
        'TK': 'Токелау',
        'TO': 'Тонга',
        'TT': 'Тринидад и Тобаго',
        'TA': 'Тристан-да-Кунья',
        'TV': 'Тувалу',
        'TN': 'Тунис',
        'TM': 'Туркменистан',
        'TR': 'Турция',
        'UG': 'Уганда',
        'UZ': 'Узбекистан',
        'UA': 'Украина',
        'WF': 'Уоллис и Футуна',
        'UY': 'Уругвай',
        'FO': 'Фарерские о-ва',
        'FM': 'Федеративные Штаты Микронезии',
        'FJ': 'Фиджи',
        'PH': 'Филиппины',
        'FI': 'Финляндия',
        'FK': 'Фолклендские о-ва',
        'FR': 'Франция',
        'GF': 'Французская Гвиана',
        'PF': 'Французская Полинезия',
        'TF': 'Французские Южные Территории',
        'HR': 'Хорватия',
        'CF': 'ЦАР',
        'TD': 'Чад',
        'ME': 'Черногория',
        'CZ': 'Чехия',
        'CL': 'Чили',
        'CH': 'Швейцария',
        'SE': 'Швеция',
        'SJ': 'Шпицберген и Ян-Майен',
        'LK': 'Шри-Ланка',
        'EC': 'Эквадор',
        'GQ': 'Экваториальная Гвинея',
        'ER': 'Эритрея',
        'EE': 'Эстония',
        'ET': 'Эфиопия',
        'ZA': 'ЮАР',
        'GS': 'Южная Георгия и Южные Сандвичевы о-ва',
        'SS': 'Южный Судан',
        'JM': 'Ямайка',
        'JP': 'Япония'
    }

    return countries[code] if code in countries else code
