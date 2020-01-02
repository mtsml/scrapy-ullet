import csv
from datetime import datetime
import re
import requests
import time
from bs4 import BeautifulSoup
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


ULLET_TOP_URL = 'http://www.ullet.com'
ULLET_SEARCH_URL = 'http://www.ullet.com/search.html#page/'
WEBDRIVER_TIME_OUT = 30
REQUEST_WAIT_TIME = 1


def scrapy_ullet():
    rows = []

    driver = webdriver.Chrome()
    driver.get(ULLET_SEARCH_URL)

    try:
        # ページ総数を取得する
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        li_all = soup.find('ul', class_='mg_menu_tab mg_menu_tab_top_reverse').find_all('li')
        max_page_txt = li_all[len(li_all)-1].span.a.get_text()
        max_page_num = int(re.search('\d+', max_page_txt).group())

        # for i in range(1, max_page_num+1):
        # page_btn = driver.find_element_by_link_text('P.'+str(max_page_num))
        # page_btn.click()
        print(datetime.now().strftime('%Y/%m/%d %H:%M:%S'), 'page%d' % max_page_num)
        driver.get(ULLET_SEARCH_URL+str(max_page_num))
        read_page(driver.page_source, rows)

    except Exception as e:
        print(e)
    finally:
        driver.quit()
        write_csv(rows)


def read_page(html, rows):
    soup = BeautifulSoup(html, 'html.parser')
    a_all = soup.find('div', id='ranking').find_all('a', class_='company_name')

    for a in a_all:
        rows.append(get_company_detail(ULLET_TOP_URL+a.get('href')))


def get_company_detail(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')

    # サーバー負荷軽減のため一定時間待機する
    time.sleep(REQUEST_WAIT_TIME)

    row = []
    row.append(re.search('\d+', url).group()) #コード
    row.append(soup.find('a', id='company_name0').get_text()) #企業名
    row.append(re.search('.*円', soup.find('tbody').find_all('tr')[1].find_all('td')[0].get_text()).group()) #売上高
    row.append(re.search('.*円', soup.find('tbody').find_all('tr')[1].find_all('td')[1].get_text()).group()) #純利益
    row.append(re.search('.*円', soup.find('tbody').find_all('tr')[1].find_all('td')[2].get_text()).group()) #営業CF
    row.append(re.search('.*円', soup.find('tbody').find_all('tr')[1].find_all('td')[3].get_text()).group()) #総資産
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[2].td.get_text()) #従業員数（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[3].td.get_text()) #従業員数（連結）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[4].td.get_text()) #平均年齢（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[5].td.get_text()) #平均勤続年数（単独）
    row.append(soup.find('table', class_='company_outline').tbody.find_all('tr')[7].td.get_text()) #業種

    return row


def write_csv(rows):
    with open("ullet.csv", "w", encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


if __name__ == '__main__':
    scrapy_ullet()