import random
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

PROXY_URL = 'https://www.sslproxies.org/'
BASE_URL = 'http://www.drps.ed.ac.uk/18_19_Archive_at_01-09-2018/dpt/'

ua = UserAgent()
s = requests.Session()

def main():
    proxies = get_proxies()
    proxy_idx = get_random_proxy(proxies)
    proxy = proxies[proxy_idx]
    proxy_dict = {
        "https": "https://{ip}:{port}" \
        .format(ip = proxy['ip'], port = proxy['port'])
        }

    bs = get_site_html(BASE_URL + 'cx_subindex.htm',
                       proxies=proxy_dict)
    subj_list = get_url_list(bs, 'cx_sb.+.htm')
    
    courses = set()

    for idx, subj in enumerate(subj_list):       
        bs = get_site_html(BASE_URL + subj['href'],
                           proxies=proxy_dict)
        courses_list = get_url_list(bs, 'cx[a-z]{4}[0-9]{5}.htm')

        for course in courses_list:
            if course['href'] not in courses:
                courses.add(course['href'])
        
        if (idx + 1) % 10 == 0:
            proxy_idx = get_random_proxy(proxies)
            proxy = proxies[proxy_idx]
            proxy_dict = {
                "https": "https://{ip}:{port}" \
                .format(ip = proxy['ip'], port = proxy['port'])
            }

    print(courses)


def get_proxies():
    proxies = []
    bs = get_site_html(PROXY_URL)
    proxies_table = bs.find(id='proxylisttable')
    for row in proxies_table.tbody.find_all('tr'):
        row_contents = row.find_all('td')
        proxies.append({
            'ip': row_contents[0].string,
            'port': row_contents[1].string
        })
    return proxies


def get_random_proxy(proxies):
    return random.randint(0, len(proxies) - 1)


def get_site_html(url, **kwargs):
    global s, ua
    print('Scraping from {}'.format(url))
    s.headers = {'user-agent': ua.random}
    try:
        html = s.get(url, **kwargs).text
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return BeautifulSoup(html, 'lxml')


def get_url_list(bs, regexp, tag='a'):
    return bs.find_all(tag, {'href': re.compile(regexp)})

if __name__ == '__main__':
    main()



