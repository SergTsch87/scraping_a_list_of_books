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
    

def op_json_file_write(file_path, json_content):
    import json
    with open(file_path , 'a', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)

    
# Читаємо файл замість запиту до сервера
def op_file_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    # ------------  Init block  ----------------------
    file_path = Path('irbis_page.html')
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
    
    # ------------  Write + Read block to/from Template file  ----------------------
    if not file_path.exists(): # Якщо ф-л не існує , виконуємо запит до сервера і зберігаємо результат до файлу
        response = requests.get(irbis_dict['url_irbis_with_params'])
        op_file_write(file_path, response.text)

    html_content = op_file_read(file_path)

    # ------------  Parsing block  ----------------------
    
    tree = html.fromstring(html_content)
    xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[@width="100%"]'  # отримання рядків з інформацією про книги  
    books_info = tree.xpath(xpath_query)  # Отримуємо елемент (xpath повертає список)
    
    # ------------  Write block to parsed data file  ----------------------
    file_path_2 = 'irbis_data.html'
    file_path_3 = 'irbis_data.json'
    
    books_dict = {
        'num_book': None,
        'lib_code_book': None,
        'author': None,
        'title_and_detail_description': None,
        'check_ab': None
    }

    for book in books_info:
        # print(f'book: {html.tostring(book, encoding='unicode')}') # Виводимо HTML-код кожного елемента (рядка з інформацією про книгу)
        num_book = './td[1]/b/text()'  # отримання номера книги
        lib_code_book = './td[2]/b/text()'  # отримання коду бібліотеки книги
        
        # Напиши код, як у 2-му td слід перерахувати усі вкладені <dd>,
        # які містять інформацію про книгу (назва, автор, рік видання і т.д.)
        # і зберегти їх у змінну (наприклад, book_info)
        # book_info = './td[2]/dd/text()'  # отримання інформації про книгу (назва, автор, рік видання і т.д.) з усіх вкладених <dd> у 2-му td    
        dds = book.xpath('./td[2]/dd')  # отримання усіх вкладених <dd> у 2-му td
        book_info = [dd.text_content().strip() for dd in dds if dd.text_content().strip()]  # отримання текстового вмісту кожного <dd> і збереження його у список (видаляємо порожні рядки)
        
        author = book_info[0] if len(book_info) > 0 else 'Unknown Author'  # отримання автора (перший елемент списку book_info)
        title_and_detail_description = book_info[1] if len(book_info) > 1 else 'Unknown Title and Description'  # отримання назви (другий елемент списку book_info)
        check_ab = book_info[2] if (len(book_info) > 2 and 'аб' in book_info[2]) else 'Not on the Subscription department'  # перевірка наявности книги в абонементі (третій елемент списку book_info) 

        # як краще зберегти до books_dict отримані дані про книгу?
        # Чи зберігати їх у вигляді словника, де ключами будуть назви полів
        # (num_book, lib_code_book, author, title_and_detail_description, check_ab),
        # а значеннями - відповідні дані про книгу?
        # Чи краще зберігати їх у вигляді об'єкта класу Book (dataclass), який містить ці поля як атрибути?
        # - Зберігати дані про книгу краще у вигляді об'єкта класу Book (dataclass),
        # оскільки це дозволяє краще структурувати дані і забезпечує зручний доступ до них через атрибути.
        # Використання dataclass також полегшує створення, оновлення і читання об'єктів,
        # а також покращує читабельність коду.
        # Словник може бути менш зручним для роботи з даними про книгу,
        # оскільки він не забезпечує такої ж структури і може бути менш інтуїтивно зрозумілим для розробників,
        # які звикли працювати з об'єктами.
        books_dict['num_book'] = book.xpath(num_book)[0] if len(book.xpath(num_book)) > 0 else 'Unknown Number'  # отримання номера книги   
        books_dict['lib_code_book'] = book.xpath(lib_code_book)[0] if len(book.xpath(lib_code_book)) > 0 else 'Unknown Library Code'  # отримання коду бібліотеки книги
        books_dict['author'] = author
        books_dict['title_and_detail_description'] = title_and_detail_description
        books_dict['check_ab'] = check_ab

        # print(f'book: {book.text_content()}')  # Виводимо текстовий вміст кожного елемента (рядка з інформацією про книгу)
        # op_file_write(file_path_2, html.tostring(book, encoding='unicode'))  # Зберігаємо отриманий блок з інформацією про книги у файл    
        # op_file_write(file_path_2, books_dict)  # Зберігаємо отриманий блок з інформацією про книги у файл    
        op_json_file_write(file_path_3, books_dict)  # Зберігаємо отриманий блок з інформацією про книги у файл у форматі JSON

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