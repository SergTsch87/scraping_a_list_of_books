#!/usr/bin/env python
# -*- coding: utf-8 -*-

# для MVP

# Запускає pipline

# Схема взаємодії класів MVP:
# main.py -> pipeline.py -> irbis.py -> http.py + irbis_parser.py -> models.py -> jsonl.py


# Завдання:
# 1) Збери список книг за адресою:
# https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=S&I21DBN=KNIGI&P21DBN=KNIGI&S21FMT=fullw&S21ALL=(%3C.%3EG%3D2025$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN=1&S21REF=10&S21CNR=20
# 2) Спробуй зібрати списки з наступних сторінок

# 3) Збережи його у файл у форматі JSON.
# 4) Зроби так, щоб при запуску скрипта він перевіряв наявність
#  цього файлу. Якщо файл існує, то виводив повідомлення
# "Файл вже існує". Якщо файлу немає, то виконував збір даних
# та збереження у файл. 


# YEAR = 2025
# URL_books = "https://irbis.library.kr.ua/cgi-bin/irbis64r_72/cgiirbis_64.exe?C21COM=S&I21DBN=KNIGI&P21DBN=KNIGI&S21FMT=fullw&S21ALL=(%3C.%3EG%3D{YEAR}$%3C.%3E)&FT_REQUEST=&FT_PREFIX=&Z21ID=&S21STN=1&S21REF=10&S21CNR=20"


def main():
    pass


if __name__ == '__main__':
    main()