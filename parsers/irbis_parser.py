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

from pathlib import Path

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
    
    
# Читаємо файл замість запиту до сервера
def op_file_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    file_path = Path('irbis_page.html')

    # "https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=F&I21DBN=ELIB&P21DBN=ELIB&S21FMT=&S21ALL=&Z21ID="
    url_irbis = 'https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe'
    
    year = 2025
    S21STN = 141 # Сторінка, з якої починаємо збір даних (1 - перша сторінка)
    S21REF = 10 # Кількість результатів на сторінці (10 - за замовчуванням)
    S21CNR = 20 # Кількість результатів на сторінці (20 - за замовчуванням)
    P21DBN = 'KNIGI' # База даних, яку ми хочемо парсити (KNIGI - книги)
    C21COM = 'S' # Команда для пошуку в БД (S - пошук) /
    
    irbis_dict = {
        'year': year,
        'S21STN': S21STN,
        'S21REF': S21REF,
        'S21CNR': S21CNR,
        'P21DBN': P21DBN,
        'C21COM': C21COM,
        'url_irbis_with_params': f'{url_irbis}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'
    }                
    # https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=S&I21DBN=KNIGI&P21DBN=KNIGI&S21FMT=fullw&S21ALL=(%3C.%3EG%3D2025$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN=141&S21REF=10&S21CNR=20


    if not file_path.exists(): # Якщо ф-л не існує , виконуємо запит до сервера і зберігаємо результат до файлу
        response = requests.get(irbis_dict['url_irbis_with_params'])
        op_file_write(file_path, response.text)

    html_content = op_file_read(file_path)

    # ------------  Parsing block  ----------------------
    
    tree = html.fromstring(html_content)
    # print(f'HTML: {response.text}')
    print(f'Tree: {tree}')

    xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[@width="100%"]'  # отримання рядків з інформацією про книги  
    
    # Отримуємо елемент (xpath повертає список)
    books_info = tree.xpath(xpath_query)
    # print(f'books_info: {books_info}')  # Виводимо отриману інформацію про книги
    
    file_path_2 = 'irbis_data.html'
    for book in books_info:
        # print(html.tostring(book, encoding='unicode'))  # Виводимо HTML-код кожного елемента з інформацією про книги
        op_file_write(file_path_2, html.tostring(book, encoding='unicode'))  # Зберігаємо отриманий блок з інформацією про книги у файл    

    # # Нащо тоді мені цей код, якщо я вже зберіг потрбні дані кодом вище?
    # # - Ти правий, цей код може бути зайвим, якщо ти вже зберіг потрібні дані у файл.
    # # Його можна видалити або закоментувати, якщо він не потрібен для подальшої обробки даних.     
    # if books_info:
    #     tbody = books_info[0]  # Отримуємо перший елемент tbody
    #     # Приклад отримання тексту всіх комірок всередині цього tbody
    #     data = [td.text_content().strip() for td in tbody.xpath('.//td')]
    #     print(data)
    #     # op_file_write(file_path_2, data)


if __name__ == '__main__':
    main()