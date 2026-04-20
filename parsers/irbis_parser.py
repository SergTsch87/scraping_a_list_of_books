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
import requests
#impirt socket, time
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

URL_IRBIS_BASE = 'https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe'


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


# Чи є блок записів певного року?
# Get html-код сторінки з книгами певного року (якщо є) / повідомлення про відсутність записів / повідомлення про помилку
def has_year(url_with_params: str) -> tuple[int, list | None]:
    # otput year status:
    #    -1  ->  невідома помилка
    #     0  ->  нема записів за цей рік
    #     1  ->  є записи за цей рік
    xpath_query_books = '/html/body/table/tr[4]/td[2]/table[3]/tr[1]/td'
    xpath_query_empty = '/html/body/table/tr[4]/td[2]/table[2]/tr/td/big'
    response = requests.get(url_with_params)
    tree = html.fromstring(response.text)
    has_books = tree.xpath(xpath_query_books)
    has_empty = tree.xpath(xpath_query_empty)

    if has_books: # є записи певного року
        return 1, has_books
    
    if has_empty: # немає записів певного року
        return 0, has_empty
    
    if not has_books and not has_empty: # невідома помилка
        return -1, None


# Вилучаємо зі сторінки усі:
    # - тег з атр-том і пар-ром
    # - тег з атр-том і без пар-ра
    # - тег без атр-та
def del_attr_wth_params(html_code_page, tag, attr=None, param=None):
    tree_xpath = html_code_page[0].getroottree() if html_code_page else None  # отримуємо дерево з html-коду сторінки
    
    if attr is None and param is None:
        str_xpath = f'//{tag}'
    elif param is None:
        str_xpath = f'//{tag}[@{attr}]'
    else:
        str_xpath = f'//{tag}[@{attr}="{param}"]'

    for el in tree_xpath.xpath(str_xpath):
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)


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
    count_pages, remaind = divmod(count_docs, S21CNR)
    if remaind != 0:
        count_pages += 1
    return count_pages


# Загальна кількість знайдених книг (за певний рік)
def gener_count_find_books_of_year(html_code_page):
    count_docs = int(html_code_page[0].text_content().strip()) if html_code_page else 0
    return count_docs


def get_url_with_params(year):
    return f'{URL_IRBIS_BASE}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'


def main():
    list_of_empty_years = []
    list_of_error_years = []

    for year in range(1800, 2027):
        url = get_url_with_params(year)
        year_status, html_code_page = has_year(url) # html_code_page - html-код сторінки з книгами певного року

        if year_status == 0: # нема записів за цей рік
             list_of_empty_years.append(year) # для статистики, які роки були оброблені
        if year_status == -1: # невідома помилка
            #  log_error(year, html_code_page) # для статистики, які роки були оброблені з помилкою
             list_of_error_years.append(year) # для статистики, які роки були оброблені з помилкою

        if year_status == 1: # є записи за цей рік
            # html_code_page = has_year(url)[1] # отримуємо html-код сторінки з книгами певного року
            # Обходимо усі записи на сторінці, вилучаємо зайве, формуємо Book і зберігаємо його до html-файлу
            count_docs = gener_count_find_books_of_year(html_code_page)
            print(f'\nЗагальна кількість знайдених документів: {count_docs}')
            count_pages = count_pages_of_year(count_docs, S21CNR)
            print(f'\nКількість сторінок: {count_pages}')

            for iter_page in range(1, count_pages + 1):
        # ------------  Parsing block  ----------------------

                if iter_page == 1: # для першої сторінки - ті ж URL та html_code_page
                    print(f'Ітерація {iter_page}/{count_pages}, S21STN={S21STN}') # for test

                    # Видаляємо всі елементи:
                        # <style>
                        # <form>
                        # <hr noshade>
                    del_attr_wth_params(html_code_page, 'style', attr=None, param=None)
                    del_attr_wth_params(html_code_page, 'form', attr=None, param=None)
                    del_attr_wth_params(html_code_page, 'hr', attr='noshade', param=None)

                else: # для наступних сторінок - формуємо новий URL та отримуємо новий html_code_page
                    S21STN = 1 + S21CNR * iter_page  # Формула для номера сторінки
                    # Пізніше оптимізуй код до "S21STN += 20" (щоб менше множити)

                    # Оновлюємо URL з новим S21STN
                    url_with_params = f'{URL_IRBIS_BASE}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'
                    print(f'Ітерація {iter_page}/{count_pages}, S21STN={S21STN}') # for test

                    response = requests.get(url_with_params)
                    tree = html.fromstring(response.text)

                    # Видаляємо всі елементи:
                        # <style>
                        # <form>
                        # <hr noshade>
                    del_attr_wth_params(html_code_page, 'style', attr=None, param=None)
                    del_attr_wth_params(html_code_page, 'form', attr=None, param=None)
                    del_attr_wth_params(html_code_page, 'hr', attr='noshade', param=None)


if __name__ == '__main__':
    main()