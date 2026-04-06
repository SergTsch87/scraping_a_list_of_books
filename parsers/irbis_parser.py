# для MVP

# Витягує:
# title
# description
# availability (аб/чз)

# Перетворює -> Book (dataclass)

# Роль:
# Знає, де і як отримати сторінки з інформацією про книги

# Знає, де знаходиться потрібна інформація в html-сторінці
# # Відповідає за:
# # - парсинг html-сторінки
# # - формування Book



#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gettext import find

import requests, socket, time
from bs4 import BeautifulSoup
from lxml import html

# ---------- Utility functions --------------------
def is_connected():    # Для перевірки доступности інтернету перед надсиланням запиту
    try:
        socket.create_connection(('www.google.com', 80), timeout=5)
        return True
    except OSError:
        return False


# ------------- Parsing logic ---------------------------------

# !!!
# Потім об'єднай ці ф-ції в одну,
# яка буде приймати url і повертати soup-об'єкт або html-код
# залежно від параметра return_soup     
# ! І не заплутайся в цих двох ф-ціях, які по суті роблять одне і те саме,
# але з різними параметрами return_soup (true/false) - це може призвести до плутанини,
# якщо не бути обережним. Краще об'єднати їх в одну ф-цію,
# яка буде приймати параметр return_soup і повертати відповідний результат.
# Це зробить код більш чистим і зрозумілим.

# Повертає весь html-код сторінки / soup-об'єкт (залежно від параметра return_soup)
def fetch_content(url, timeout=20, return_soup=True):
    response = requests.get(url, timeout=20)
    response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
    html = response.text
    return BeautifulSoup(html, 'html.parser') if return_soup else html


def fetch(url, timeout=10):
    if not is_connected():  # Якщо нема інтернет-зв'язку
        return 'Error: No internet connection'

    print(f'Fetching URL: {url}')  # !!! переконайтеся, що ви дійсно отримуєте нову сторінку
    html = fetch_content(url, timeout=10, return_soup=False)
            
    if html is None or len(html.strip()) == 0:
        return []
            
    return html  # Успішний запит, - Повертаємо контент


def get_dict_all_categories(url):
    soup = fetch_content(url, timeout=20, return_soup=True)
    # # print(f'soup.prettify == {soup.find('ul', class_='menu-categories ng-star-inserted')}')

    # dict_all_categories = {}
    # list_tags_a = soup.find_all('a', class_='ssr-menu-categories__link')


def main():
    # "https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=F&I21DBN=ELIB&P21DBN=ELIB&S21FMT=&S21ALL=&Z21ID="
    year = 2025
    S21STN = 141 # Сторінка, з якої починаємо збір даних (1 - перша сторінка)
    S21REF = 10 # Кількість результатів на сторінці (10 - за замовчуванням)
    S21CNR = 20 # Кількість результатів на сторінці (20 - за замовчуванням)
    # яка різниця між S21REF і S21CNR? - це може бути важливо для правильного формування URL-адреси
    # та отримання потрібної кількості результатів на сторінці.
    # Якщо вони обидва відповідають за кількість результатів,
    # то потрібно визначити, який з них є правильним параметром для цього завдання,
    # щоб уникнути плутанини і забезпечити правильну роботу парсера.
    P21DBN = 'KNIGI' # База даних, яку ми хочемо парсити (KNIGI - книги)
    C21COM = 'S' # Команда для пошуку (S - пошук) /
    # / C21COM=S - це параметр, який вказує на те, що ми хочемо виконати пошук (Search) в базі даних.
    # Це важливо для формування правильного URL-адреси і отримання потрібних результатів при парсингу.    
    url_irbis = 'https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe'
    url_irbis_with_params = f'{url_irbis}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'
    
    # https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=S&I21DBN=KNIGI&P21DBN=KNIGI&S21FMT=fullw&S21ALL=(%3C.%3EG%3D2025$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN=141&S21REF=10&S21CNR=20

    # body > table > tbody > tr:nth-child(4) > td.main_content > table:nth-child(5) > tbody

    # !!! Наче як унікальний way!)
    # /html/body/table/tbody/tr[4]/td[2]/table[4]/tbody

    # body > table > tbody > tr:nth-child(4) > td.main_content > table:nth-child(5) > tbody > tr:nth-child(4)

    # якими засобами з html/soup obj дістати блок за його xpath? 
    # як це робити find(), find_all() або CSS-селекторами?
    # import lxml.html
    # import gettext

    # - це може бути важливо для правильного отримання потрібного блоку з інформацією про книги,
    # особливо якщо структура сторінки складна і містить багато елементів.
    # Використання XPath може допомогти точно вказати шлях до потрібного елемента
    # і уникнути плутанини при парсингу.
    # !!! Але BeautifulSoup не підтримує XPath, тому потрібно використовувати інші методи
    #  для отримання потрібного блоку, такі як find(), find_all() або CSS-селектори.
    # Це може бути важливо для правильного отримання інформації про книги 
    # і забезпечення ефективної роботи парсера.   

    response = requests.get(url_irbis_with_params)
    tree = html.fromstring(response.content)
    # print(f'HTML: {response.text}')
    print(f'Tree: {tree}')
    # Використовуємо XPath для отримання потрібного блоку з інформацією про книги
    # xpath_query = '/html/body/table/tbody/tr[4]/td[2]/table[4]/tbody/tr'  # Приклад XPath для отримання рядків з інформацією про книги  
    xpath_query = f'//table[contains(., "{S21STN}.")]'  # Приклад XPath для отримання рядків з інформацією про книги  
    
    # Отримуємо елемент (xpath повертає список)
    books_info = tree.xpath(xpath_query)
    print(books_info)  # Виводимо отриману інформацію про книги
    if books_info:
        tbody = books_info[0]  # Отримуємо перший елемент tbody
        # Приклад отримання тексту всіх комірок всередині цього tbody
        data = [td.text_content().strip() for td in tbody.xpath('.//td')]
        print(data)


# для дем-ції прикладу викор-ня ф-цій цього ф-лу
if __name__ == '__main__':
    main()