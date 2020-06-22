import requests
import lxml
from bs4 import BeautifulSoup


class Proxy(object):
    proxy_url = 'https://www.ip-adress.com/proxy-list'
    proxy_list = []

    def __init__(self):
        html = requests.get(self.proxy_url)
        soup = BeautifulSoup(html.text, 'lxml')
        tr = soup.find('tbody').find_all('a')
        td = soup.find('tbody').find_all('td')
        port = []
        for i in td:
            if ':' in i.text:
                port.append(i.text[-5:])
        for index, i in enumerate(tr):
            m = i.text + port[index]
            self.proxy_list.append(m)
             
    def get_proxy(self):
        for i in self.proxy_list:
            url = 'http://' + i
            try:
                r = requests.get('http://ya.ru', proxies={'http': url})
                if r.status_code == 200:
                    return url
            except requests.exceptions.ConnectionError:
                continue

