import csv
from datetime import datetime
import re
import requests
import time
from bs4 import BeautifulSoup


ULLET_TOP_URL = 'http://www.ullet.com'
ULLET_SEARCH_URL = 'http://www.ullet.com/search.html'
ULLET_PAGE_URL = 'http://www.ullet.com/search/page/%d.html'
REQUEST_WAIT_TIME = 1


def scrapy_ullet():
    rows = []

    # 総ページ数の取得
    res = requests.get(ULLET_SEARCH_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    li_all = soup.find('ul', class_='mg_menu_tab mg_menu_tab_top_reverse').find_all('li')
    max_page_txt = li_all[len(li_all)-1].span.a.get_text()
    max_page_num = int(re.search('\d+', max_page_txt).group())

    for i in range(1, max_page_num+1):
        read_page(i, rows)

    write_csv(rows)


def read_page(page, rows):
    print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 'page%d'%page)
    
    res = requests.get(ULLET_PAGE_URL%page)
    soup = BeautifulSoup(res.text, 'html.parser')
    a_all = soup.find('div', id='ranking').find_all('a', class_='company_name')

    for a in a_all:
        rows.append(get_company_detail(ULLET_TOP_URL+a.get('href')))


def get_company_detail(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')

    # サーバー負荷軽減のため一定時間待機する
    time.sleep(REQUEST_WAIT_TIME)

    row = []
    row.append(re.search('\d+', url).group()) #コード
    row.append(soup.find('a', id='company_name0').get_text()) #企業名
    row.append(trim_indicator(soup, 0)) #売上高
    row.append(trim_indicator(soup, 1)) #純利益
    row.append(trim_indicator(soup, 2)) #営業CF
    row.append(trim_indicator(soup, 3)) #総資産
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[2].td.get_text()) #従業員数（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[3].td.get_text()) #従業員数（連結）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[4].td.get_text()) #平均年齢（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[5].td.get_text()) #平均勤続年数（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[7].td.get_text()) #業種

    return row


def trim_indicator(soup, index):
    i = soup.find('tbody').find_all('tr')[1].find_all('td')[index].get_text()
    r = re.search('.*円', i)
    if r != None:
        return r.group()
    else:
        return ""


def write_csv(rows):
    with open("ullet.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        for row in rows:
            writer.writerow(row)


if __name__ == '__main__':
    scrapy_ullet()