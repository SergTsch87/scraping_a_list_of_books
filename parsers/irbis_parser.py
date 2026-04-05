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

import requests, socket
from bs4 import BeautifulSoup


# ---------- Utility functions --------------------
def is_connected():    # Для перевірки доступності інтернету перед відправленням запиту
    try:
        socket.create_connection(('www.google.com', 80), timeout=5)
        return True
    except OSError:
        return False


def main():
    pass


# для дем-ції прикладу викор-ня ф-цій цього ф-лу
if __name__ == '__main__':
    main()