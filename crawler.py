# <랭킹>
from selenium import webdriver
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os
import time

load_dotenv()

import pymysql
conn = pymysql.connect(host=os.environ.get('IP_ADDRESS'), user=os.environ.get('USER'), password=os.environ.get('PASSWORD'), db=os.environ.get('DB_NAME'), charset='utf8')
cur = conn.cursor()

driver = webdriver.Chrome('chromedriver')

# 인터파크
url = ('http://ticket.interpark.com/TPGoodsList.asp?Ca=Eve&SubCa=Eve_O&Sort=3')
driver.get(url)

# 페이지 따왔을때 http://가없어서 추가
page_list = []
pages = driver.find_elements_by_css_selector('.fw_bold a')
for page in pages:
    page = page.get_attribute('href')
    page_list.append(page)

requests = driver.page_source
soup = BeautifulSoup(requests, 'html.parser')
trs = soup.select('body > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > div > div.con > div > table > tbody > tr')

# 데이터 가져오기
for i, tr in enumerate(trs):
    image = tr.select_one('td.RKthumb > a > img')['src']                                  # 이미지
    title = tr.select_one('td.RKtxt > span > a').text                                     # 전시제목
    location = tr.select_one('td:nth-child(3) > a').text                                  # 장소
    date = tr.select_one('td:nth-child(4)').text.replace('\n', '').replace('\t', '')      # 날짜
    StartPeriod, EndPeriod = str(date).split('~')

    # 세부 페이지
    page = page_list[i]
    driver.get(page)
    page_requests = driver.page_source
    page_soup = BeautifulSoup(page_requests, 'html.parser')

    price = page_soup.select_one("#container > div.contents > div.productWrapper > div.productMain > div.productMainTop > div > div.summaryBody > ul > li.infoItem.infoPrice > div > ul > li:nth-child(2) > span.price")   # 가격
    if price != None:
        price = price.getText()

    additionInfo = page_soup.select_one("#productMainBody > div > div:nth-child(1) > div > ul > div")   # 시간, 휴관일 등 추가 정보
    if additionInfo != None:
        additionInfo = additionInfo.getText()

    sql = "INSERT INTO art(artname, StartPeriod, EndPeriod,Price,Explanation, url, location) VALUES(%s, %s, %s, %s, %s, %s, %s)"
    val = (title, StartPeriod, EndPeriod, price, additionInfo, image, location)
    cur.execute(sql, val)

    time.sleep(2)

    # print(title, StartPeriod, EndPeriod, price, additionInfo, image, location)

conn.commit()
conn.close()
