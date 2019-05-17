import random
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

PROXY_URL = 'https://www.sslproxies.org/'
BASE_URL = 'http://www.drps.ed.ac.uk/18_19_Archive_at_01-09-2018/dpt/'


def main():
    ua = UserAgent()
    proxies = get_proxies(ua)

    
    courses = set()
    bs = get_site_html(BASE_URL + 'cx_subindex.htm')
    subj_list = get_url_list(bs, 'cx_sb.+.htm')
    for idx, subj in enumerate(subj_list):
        bs = get_site_html(BASE_URL + subj['href'])
        courses_list = get_url_list(bs, 'cx[a-z]{4}[0-9]{5}.htm')
        for course in courses_list:
            if course['href'] not in courses:
                courses.add(course['href'])
    print(courses)

def get_proxies(ua):
    with requests.Session() as s:
        s.header = {'user-agent': ua.random}
        html = s.get(PROXY_URL).text
        bs = get_site_html(html)
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


def get_site_html(url):
    print('Scraping from {}'.format(url))
    with requests.Session() as s:
        s.headers = {'user-agent': ua.random}
        try:
            html = s.get(url).text
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        return BeautifulSoup(html, 'lxml')


def get_url_list(bs, regexp, tag='a'):
    return bs.find_all(tag, {'href': re.compile(regexp)})

if __name__ == '__main__':
    main()



