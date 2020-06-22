"""парсер для https://www.rusprofile.ru/"""

from connect_db import cur, con
import requests
import lxml
from bs4 import BeautifulSoup

from proxies import Proxy


def db_build():
    # Создаем таблицу для выгрузки данных, если еще не создана
    cur.execute('''CREATE TABLE if not exists DATA_COMPANIES
         (ID SERIAL PRIMARY KEY NOT NULL,
         NAME TEXT NOT NULL,
         TYPE TEXT NOT NULL,
         OGRN TEXT NOT NULL,
         OKPO TEXT NOT NULL,
         STATUS TEXT NOT NULL,
         DATE_BIRTHDAY TEXT NOT NULL,
         CAPITAL TEXT NOT NULL);'''
                )
    con.commit()


def get_html(url, proxy):  # получаем url страницы для парсинга
    response = requests.get(url,  proxies={'http': proxy})
    return response.text


def get_total_pages(html):  # определяем количество страниц для парсинга
    total_pages = 1
    soup = BeautifulSoup(html, 'lxml')
    if soup.find('div', class_='search-result-paging'):  # проверяем наличие тега с страницами
        ul = soup.find('ul', class_='paging-list')
        pages = ul.find_all('a')[-1].get('href')
        total_pages = int(pages.split('/')[-2])
    return total_pages


# получаем адреса страниц кампаний
def get_page_address(list_url, proxy):
    address = []
    for url in list_url:
        html = get_html(url, proxy)
        pages = get_total_pages(html)
        for i in range(1, pages + 1):
            if i == 1:
                url_pages = url
            else:
                url_pages = url + '/' + str(i) + '/'
            html = get_html(url_pages, proxy)
            soup = BeautifulSoup(html, 'lxml')
            divs = soup.find('div', class_='main-wrap__content')
            if pages > 1:
                ad = divs.find_all('a')[:-3]
            else:
                ad = divs.find_all('a')

            for j in ad:
                a = 'https://www.rusprofile.ru' + j.get('href')  # составляем адреса страниц кампаний с их данными
                address.append(a)

    return address


# собираем данные кампании
def get_page_data(html):
    status_company = 'Нет информации'
    capital = 'Нет информации'
    soup = BeautifulSoup(html, 'lxml')

    # название компании
    try:
        title_company = soup.find('div', class_='company-name').text
    except AttributeError:
        title_company = 'Нет информации'
    # ОГРН
    try:
        ogrn = soup.find('span', class_='copy_target', id='clip_ogrn').text
    except AttributeError:
        ogrn = 'Нет информации'
    # ОКПО
    try:
        okpo = soup.find('span', class_='copy_target', id='clip_okpo').text
    except AttributeError:
        okpo = 'Нет информации'
    # Статус компании
    if soup.find('div', class_='company-status active-yes'):
        status_company = 'Действующая организация'
    elif soup.find('div', class_='company-status deleted'):
        status_company = 'Организация ликвидирована'
    elif soup.find('div', class_='company-status reorganizated'):
        status_company = 'Организация в процессе ликвидации'
    # дата организации
    date_birthday = soup.find('dd', class_='company-info__text', itemprop='foundingDate').text

    # уставной капитал
    cap = soup.find_all('span', class_='copy_target')  # ищем все подходящие теги
    for i in cap:
        j = str(i)
        # если в теге есть включение "руб" значит это искомый капитал
        if 'руб' in j:
            capital = j.replace('<span class="copy_target">', '').replace('</span>', '')

    # номер вида деятельности
    try:
        type_ = soup.find('span', class_='bolder').text.replace('(', '')[:-1]
    except AttributeError:
        type_ = 'Нет информации'

    cur.execute("INSERT INTO DATA_COMPANIES ( NAME, TYPE, OGRN, OKPO, STATUS, DATE_BIRTHDAY, CAPITAL) VALUES ('%s','%s','%s', '%s', '%s', '%s', '%s')" % (
            title_company, type_, ogrn, okpo, status_company, date_birthday, capital))


def main():
    proxy = Proxy()
    proxy = proxy.get_proxy()
    db_build()
    url = 'https://www.rusprofile.ru/codes/89220'
    url_2 = 'https://www.rusprofile.ru/codes/429110'
    list_url = [url, url_2]
    address = get_page_address(list_url, proxy)
    print(address)
    for i in address:
        html_company = get_html(i, proxy)
        get_page_data(html_company)

    con.commit()
    con.close()


if __name__ == '__main__':
    main()
