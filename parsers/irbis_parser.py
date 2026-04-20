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

    # Сайт бібліотеки:
    # url_irbis = 'https://library.kr.ua'



#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from gettext import find

import json
import requests, socket, time
from bs4 import BeautifulSoup
from lxml import html, etree

from pathlib import Path


# ------------  Init block  ----------------------    
year = 1200
# year = 2025
S21STN = 1 # Сторінка, з якої починаємо збір даних (1 - перша сторінка)
S21REF = 10 # Кількість результатів на сторінці (10 - за замовчуванням)
S21CNR = 20 # Кількість результатів на сторінці (20 - за замовчуванням)
P21DBN = 'KNIGI' # База даних, яку ми хочемо парсити (KNIGI - книги)
C21COM = 'S' # Команда для пошуку в БД (S - пошук) /

url_irbis = 'https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe'


irbis_dict = {
    'year': year,
    'S21STN': S21STN, # 1,
    'S21REF': S21REF,
    'S21CNR': S21CNR,
    'P21DBN': P21DBN,
    'C21COM': C21COM,
    'url_irbis_with_params': f'{url_irbis}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'
}

url_irbis_with_params = irbis_dict['url_irbis_with_params']


# ---------- Utility functions --------------------
def is_connected():    # Для перевірки доступности інтернету перед надсиланням запиту
    try:
        socket.create_connection(('www.google.com', 80), timeout=5)
        return True
    except OSError:
        return False


def normalize_element_text(node):
    """Return normalized text for an element, with all nested text joined cleanly."""
    if node is None:
        return ''
    return ' '.join(text.strip() for text in node.xpath('.//text()') if text.strip())


def contains_ab(text):
    return text is not None and 'аб' in text.lower()


# ------------- Parsing logic ---------------------------------

# !!!
# Потім об'єднай ці ф-ції в одну,

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


def op_file_write(file_path, content):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
        
    print(f'Content append to {file_path}')
    

def op_json_file_write(file_path, json_content):
    # import json
    with open(file_path , 'a', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)

    
# Читаємо файл замість запиту до сервера
def op_file_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


# Чи є сторінка (і книги) певного року?
def has_year():
    xpath_query = '/html/body/table/tr[4]/td[2]/table[3]'
    response = requests.get(url_irbis_with_params)
    tree = html.fromstring(response.text)
    has_books = tree.xpath(xpath_query)
    
    if has_books: # є сторінка певного року
        # /html/body/table/tr[4]/td[2]/table[3]/tr[1]/td
        return True
    else:
        # print('Нема книг за цей рік')
        # /html/body/table/tr[4]/td[2]/table[2]/tr/td/big
        return False


# Вилучаємо зі сторінки усі:
    # - тег з атр-том і пар-ром
    # - тег з атр-том і без пар-ра
    # - тег без атр-та
def del_attr_wth_params(tree_xpath, tag, attr=None, param=None):
    if attr is None and param is None:
        xpath = f'//{tag}'
    elif param is None:
        xpath = f'//{tag}[@{attr}]'
    else:
        xpath = f'//{tag}[@{attr}="{param}"]'

    for el in tree_xpath.xpath(xpath):
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)

    # for param_tag in tree_xpath.xpath(f'//{tag}[@{attr}="{param}"]'):
    #     param_tag.getparent().remove(param_tag)


def create_tbody_to_html(tag, tree_xpath):
    # Створіть wrapper-елемент <tbody>
    # tag == 'tbody'
    tbody = etree.Element(tag)

    # Додайте усі tr з books_info до tbody
    
    # tree_xpath == books_info
    for tr in tree_xpath:
        tbody.append(tr)
    
    # Конвертуйте в HTML-рядок
    html_string = etree.tostring(tbody, encoding='unicode', method='html')
    return html_string


# К-сть сторінок певного року
def count_pages_of_year(count_docs, S21CNR): # S21CNR == 20 (by def-t)
    count_iters, remaind = divmod(count_docs, S21CNR)
    if remaind != 0:
        count_iters += 1
    return count_iters


# Загальна кількість знайдених книг (за певний рік)
def gener_count_find_books_of_year(irbis_dict):
                    # html/body/table/tr[4]/td[2]/table[2
    xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[1]/td/b'
    response = requests.get(irbis_dict['url_irbis_with_params'])
    tree = html.fromstring(response.text)
    
    num_books = tree.xpath(xpath_query)
    count_docs = int(num_books[0].text_content().strip()) if num_books else 0
    print(f'\nЗагальна кількість знайдених документів: {count_docs}')

    # # # К-сть сторінок певного року
    # count_iters = count_pages_of_year(count_docs, S21CNR)
    # return count_iters # ???
    return count_docs


def main():
    for year in range(1800, 2027):
        html_code_page = get_html_code_of_page_by_its_url(year)
        if <є записи за цей рік> у html_code_page:
            Обходимо усі записи на сторінці, вилучаємо зайве, формуємо Book і зберігаємо його до html-файлу
        if <нема записів за цей рік> у html_code_page:
             ніц не робимо, переходимо до наступного року
             list_of_empty_years.append(year) # для статистики, які роки були оброблені
        if <unknown error> у html_code_page:
             log_error(year, html_code_page) # для статистики, які роки були оброблені з помилкою
             list_of_error_years.append(year) # для статистики, які роки були оброблені з помилкою


if __name__ == '__main__':
    main()