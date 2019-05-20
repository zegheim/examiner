import json
import random
import re
import requests
import sys

from bs4 import BeautifulSoup

PROXY_URL = 'https://www.sslproxies.org/'
BASE_URL = 'http://www.drps.ed.ac.uk/18_19_Archive_at_01-09-2018/dpt/'

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
    schools = bs.find('table', {'class': 'content'}).find_all('h2')

    with open('csv/courses.csv', 'w+') as f:
        f.write('schedule, course_code, course_name, period, credits\n')
        for school in schools:
            schedule = school.text[-2]
            subjects = get_url_list(school.next_sibling, 'cx_sb_[a-z]{4}.htm')
            for idx, subject in enumerate(subjects):
                bs = get_site_html(BASE_URL + subject['href'], proxies=proxy_dict)
                courses = get_url_list(bs, 'cx[a-z]{4}[0-9]{5}.htm')
                for course in courses:
                    if course.has_attr('class') is not True:
                        course_code = course.parent.find_previous_sibling('td', string=re.compile('[A-Z]{4}[0-9]{5}'))
                        period = course.parent.next_sibling
                        credit = period.next_sibling
                        f.write('{}, {}, {}, {}, {}\n'
                                .format(schedule, course_code.get_text(),
                                        course.get_text(), period.get_text(), 
                                        credit.get_text()))

                # Rotate proxies used after 10 requests
                if (idx + 1) % 10 == 0:
                    proxy_idx = get_random_proxy(proxies)
                    proxy = proxies[proxy_idx]
                    proxy_dict = {
                        "https": "https://{ip}:{port}" \
                        .format(ip = proxy['ip'], port = proxy['port'])
                }


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
    global s
    s.header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    try:
        html = strip_wsnl(s.get(url, **kwargs).text)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return BeautifulSoup(html, 'lxml')


def get_url_list(bs, regexp, tag='a'):
    return bs.find_all(tag, {'href': re.compile(regexp)})


def strip_wsnl(html):
    """remove whitespaces and newlines"""
    pat = re.compile('(^[\s]+)|([\s]+$)', re.MULTILINE)
    html = re.sub(pat, '', html)        # remove leading and trailing whitespaces
    html = re.sub('\n', ' ', html)      # convert newlines to spaces
                                        # this preserves newline delimiters
    html = re.sub('[\s]+<', '<', html)  # remove whitespaces before opening tags
    html = re.sub('>[\s]+', '>', html)  # remove whitespaces after closing tags
    return html

if __name__ == '__main__':
    with requests.Session() as s:
        raw_data = s.get('https://exams.is.ed.ac.uk/search/')
    with open('json/exams.json', 'w') as f:
        d_list = json.loads(raw_data.text)['data']
        f.write(json.dumps(d_list))
    main()



