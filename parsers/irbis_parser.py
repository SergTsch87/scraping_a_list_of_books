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
def count_pages_of_year(count_docs, S21CNR):
    count_iters, remaind = divmod(count_docs, S21CNR)
    if remaind != 0:
        count_iters += 1
    return count_iters


# Загальна кількість знайдених книг (за певний рік)
def gener_count_find_books_of_year(irbis_dict, S21CNR):
    # xpath_query = '/html/body/table/tbody/tr[4]/td[2]/table[4]/tbody/tr[0]/td/b'
    xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[1]/td/b'
    response = requests.get(irbis_dict['url_irbis_with_params'])
    tree = html.fromstring(response.text)
    
    num_books = tree.xpath(xpath_query)  # Отримуємо елемент (xpath повертає список)
    # print(f'\nTree: {tree}')
    # print(f'\nnum_books: {num_books}')
    count_docs = int(num_books[0].text_content().strip()) if num_books else 0
    print(f'\nЗагальна кількість знайдених документів: {count_docs}')

    # # К-сть сторінок певного року
    count_iters = count_pages_of_year(count_docs, S21CNR)
    return count_iters


def main():
    # ------------  Init block  ----------------------    
    year = 2025
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

    # year = irbis_dict["year"] # Нащо цей повтор?!..
    # num = irbis_dict["S21STN"]  # Нащо цей повтор?!..

# ------------
    # Загальна кількість знайдених документів:
    count_iters = gener_count_find_books_of_year(irbis_dict, S21CNR)
    # # xpath_query = '/html/body/table/tbody/tr[4]/td[2]/table[4]/tbody/tr[0]/td/b'
    # xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[1]/td/b'
    # response = requests.get(irbis_dict['url_irbis_with_params'])
    # tree = html.fromstring(response.text)
    
    # num_books = tree.xpath(xpath_query)  # Отримуємо елемент (xpath повертає список)
    # # print(f'\nTree: {tree}')
    # # print(f'\nnum_books: {num_books}')
    # count_docs = int(num_books[0].text_content().strip()) if num_books else 0
    # print(f'\nЗагальна кількість знайдених документів: {count_docs}')

    # # # К-сть сторінок певного року
    # count_iters = count_pages_of_year(count_docs, S21CNR)
    # # count_iters, remaind = divmod(count_docs, S21CNR)
    # # if remaind != 0:
    # #     count_iters += 1
# -------------

    # ------------  Write + Read block to/from Template file  ----------------------
    # response = None  # Ініціалізуємо змінну response перед блоком if
    # if not file_path.exists(): # Якщо ф-л не існує , виконуємо запит до сервера і зберігаємо результат до файлу
    #     response = requests.get(irbis_dict['url_irbis_with_params'])
    #     op_file_write(file_path, response.text)

    # html_content = op_file_read(file_path)


    # === ЦИКЛ ПО СТОРІНКАХ ===

    for num_page in range(count_iters):
        S21STN = 1 + S21CNR * num_page  # Формула для номера сторінки
        # Пізніше оптимізуй код до "S21STN += 20" (щоб менше множити)

        # Оновлюємо URL з новим S21STN
        url_with_params = f'{url_irbis}?C21COM=S&I21DBN=KNIGI&P21DBN={P21DBN}&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{year}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN={S21STN}&S21REF={S21REF}&S21CNR={S21CNR}'
        # print(f'Ітерація {num_page+1}/{count_iters}, S21STN={S21STN}')

        response = requests.get(url_with_params)
        tree = html.fromstring(response.text)

        # ------------  Parsing block  ----------------------
        
        # Видаляємо всі елементи:
            # <style>
            # <form>
            # <hr noshade>
        del_attr_wth_params(tree, 'style', attr=None, param=None)
        del_attr_wth_params(tree, 'form', attr=None, param=None)
        del_attr_wth_params(tree, 'hr', attr='noshade', param=None)
        
        # # Видаляємо всі елементи `<style>`
        # for style in tree.xpath('//style'):
        #     style.getparent().remove(style)

        # # Вилучаємо усі <form> зі сторінки
        # for form_el in tree.xpath('//form'):
        #     form_el.getparent().remove(form_el)
        
        # # # Вилучаємо усі <input type="hidden"> зі сторінки
        # # for hidden_input in tree.xpath('//input[@type="hidden"]'):
        # #     hidden_input.getparent().remove(hidden_input)
        
        # # Вилучаємо усі <hr noshade> зі сторінки
        # for hr_noshade in tree.xpath('//hr[@noshade]'):
        #     hr_noshade.getparent().remove(hr_noshade)

        # Отримуємо книги з цієї сторінки
        xpath_query = '/html/body/table/tr[4]/td[2]/table[4]/tr[@width="100%"]'  # отримання рядків з інформацією про книги  
        books_info = tree.xpath(xpath_query)  # Отримуємо елемент (xpath повертає список)
        
    
    # ------------  Load web page content to file  ----------------------
    
# db -|
#     |- 2025 -|
#           |- 1.html
#           |- 2.html
#           ...
#     |- 2024 -|
#           ...


    # # Нащо тоді мені цей код, якщо я вже зберіг потрбні дані кодом вище?
    # # - Ти правий, цей код може бути зайвим, якщо ти вже зберіг потрібні дані у файл.
    # # Його можна видалити або закоментувати, якщо він не потрібен для подальшої обробки даних.     


        # ------------  Loop block ( to bypass pagination each year ) ----------------------
        # # /2025/1|2|3...|n.html etc for each year


        # Створюємо елемент-обгортку <tbody>, який збережемо разом усіма записами до файлу
        if books_info:
            html_string = create_tbody_to_html('tbody', books_info)
            file_path = Path(f'./db/{year}/{S21STN}.html')
            # file_path.parent.mkdir(parents=True, exist_ok=True) # мабуть, слід вилучити...


            # # Створіть wrapper-елемент <tbody>
            # tbody = etree.Element('tbody')
            # # Додайте усі tr з books_info до tbody
            # for tr in books_info:
            #     tbody.append(tr)
            # # Конвертуйте в HTML-рядок
            # html_string = etree.tostring(tbody, encoding='unicode', method='html')
            
            # Запишіть до файлу
            op_file_write(file_path, html_string)

            print(f'Збережено: {file_path}')
        
        else:
            print(f'Немає книг на сторінці {S21STN}')

        # # tbody = books_info[0]  # Отримуємо перший елемент tbody
        # # Приклад отримання тексту всіх комірок всередині цього tbody

        # # html_string = etree.tostring(tbody, encoding='unicode', method='html')
        # html_string = etree.tostring(books_info, encoding='unicode', method='html')
        # # op_file_write(file_path, tbody.text_content().strip())
        # op_file_write(file_path, html_string)
        # # op_json_file_write(file_path, html_string)
        
        
        # - Щоб записати до файлу саме HTML-код, а не текстовий вміст,
        # ти можеш використовувати метод .tostring() з бібліотеки lxml
        # для перетворення об'єкта HtmlElement у рядок, який містить HTML-код.
        # from lxml import etree
        # html_string = etree.tostring(tbody, encoding='unicode', method='html')
        # op_file_write(file_path, html_string)
        
        # що є data? - Це список текстового вмісту всіх комірок (td) всередині першого елемента tbody,
        # який містить інформацію про книги.
        # Кожен елемент цього списку є рядком, який представляє текстовий вміст відповідної комірки таблиці.  
        # data = [td.text_content().strip() for td in tbody.xpath('.//td')]
        # print(data)
        # op_json_file_write(file_path, data)

    
    # # ------------  Write block to parsed data file  ----------------------
    
    # file_path_3 = 'irbis_data.json'    
    # books = []

    # for book in books_info:
    #     num_book = book.xpath('string(.//td[1]/b)').strip()
    #     lib_code_book = book.xpath('string(.//td[2]/b)').strip()
        
    #     # Напиши код, як у 2-му td слід перерахувати усі вкладені <dd>,
    #     # які містять інформацію про книгу (назва, автор, рік видання і т.д.)
    #     # і зберегти їх у змінну (наприклад, book_info)
    #     # book_info = './td[2]/dd/text()'  # отримання інформації про книгу (назва, автор, рік видання і т.д.) з усіх вкладених <dd> у 2-му td    
        
    #     dds = book.xpath('./td[2]/dd')  # отримання усіх вкладених <dd> у 2-му td
    #     # file_path_4 = 'dds.json'
    #     # op_json_file_write(file_path_4,dds)
        
    #     # > TypeError: Object of type HtmlElement is not JSON serializable
    #     #  - Це означає, що об'єкт типу HtmlElement не може бути серіалізований у формат JSON.
    #     # Як же тоді зберегти цей список dds до файлу у форматі JSON, якщо він містить об'єкти типу HtmlElement,
    #     # які не можуть бути безпосередньо серіалізовані у формат JSON?
    #     # - Щоб зберегти список dds до файлу у форматі JSON, ти можеш
    #     # спочатку перетворити кожен об'єкт HtmlElement у рядок,
    #     # використовуючи метод .text_content() для отримання текстового вмісту кожного елемента <dd>.  

    #     # чи можна записати весь список dds до файлу, а потім прочитати його і отримати текстовий вміст кожного <dd>?
    #     # - Так, ти можеш записати весь список dds до файлу, а потім прочитати його і отримати текстовий вміст кожного <dd>.
    #     # Для цього ти можеш використовувати функцію op_file_write для запису списку dds до файлу,
    #     # а потім використовувати функцію op_file_read для читання цього файлу і отримання текстового вмісту кожного <dd>.
    #     # Ось як це можна зробити:   

    #     # як, та до якого формату ф-лу, записати список отриманих елементів <dd> до файлу,
    #     # щоб потім можна було його прочитати і отримати текстовий вміст кожного <dd>?
    #     # - Ти можеш записати список отриманих елементів <dd> до файлу у форматі JSON,
    #     # використовуючи функцію op_json_file_write.
    #     # Для цього тобі потрібно спочатку отримати текстовий вміст кожного <dd> і зберегти його у список,
    #     # а потім записати цей список до файлу у форматі JSON. Ось як це можна зробити:.. як же? покажи код, будь ласка.


    #     dd_texts = [normalize_element_text(dd) for dd in dds if normalize_element_text(dd)]
    #     # для <b> <a>text</a> </b> - не повертає текст,
    #     # а для <a> <b>text</b> </a> - повертає текст.
    #     # Як повернути текст для <b> <a>text</a> </b> ?
    #     # - Використовуй метод .text_content() для отримання текстового вмісту елемента, незалежно від його структури.        

    #     author = dd_texts[0] if len(dd_texts) > 0 else None
    #     detail_description = dd_texts[1] if len(dd_texts) > 1 else None
    #     metadata = dd_texts[2] if len(dd_texts) > 2 else None
    #     availability = next((text for text in dd_texts if contains_ab(text)), None)

    #     book_record = {
    #         'num_book': num_book or None,
    #         'lib_code_book': lib_code_book or None,
    #         'author': author,
    #         'detail_description': detail_description,
    #         'metadata': metadata,
    #         'availability': availability,
    #         'dd_texts': dd_texts
    #     }

    #     books.append(book_record)
    #     # - Тому що для отримання назви та детального опису книги ми використовуємо другий елемент списку book_info (індекс 1),
    #     # а не перший (індекс 0).
    #     # Якщо ми перевіряємо len(book_info) > 0, то це означає, що в списку book_info є хоча б один елемент,
    #     # але це не гарантує, що другий елемент (назва та детальний опис) існує.
    #     # Тому ми перевіряємо len(book_info) > 1, щоб переконатися, що в списку book_info є принаймні два елементи,
    #     # перш ніж намагатися отримати другий елемент (назву та детальний опис книги).

    #     # як краще зберегти до books_dict отримані дані про книгу?
    #     # Чи зберігати їх у вигляді словника, де ключами будуть назви полів
    #     # (num_book, lib_code_book, author, title_and_detail_description, check_ab),
    #     # а значеннями - відповідні дані про книгу?
    #     # Чи краще зберігати їх у вигляді об'єкта класу Book (dataclass), який містить ці поля як атрибути?
    #     # - Зберігати дані про книгу краще у вигляді об'єкта класу Book (dataclass),
    #     # оскільки це дозволяє краще структурувати дані і забезпечує зручний доступ до них через атрибути.
    #     # Використання dataclass також полегшує створення, оновлення і читання об'єктів,
    #     # а також покращує читабельність коду.
    #     # Словник може бути менш зручним для роботи з даними про книгу,
    #     # оскільки він не забезпечує такої ж структури і може бути менш інтуїтивно зрозумілим для розробників,
    #     # які звикли працювати з об'єктами.
    # with open(file_path_3, 'w', encoding='utf-8') as f:
    #     json.dump(books, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()