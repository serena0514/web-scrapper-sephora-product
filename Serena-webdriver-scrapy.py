# author Serena Zeng
# 1/27/2021
# scrape items from sephora moisturer website and save items into database
# one static table and one dynamic table

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import schedule
import sqlite3
import pandas as pd

SCROLL_PAUSE_TIME = 0.001
IMPLICIT_WAIT_TIME = 1
REFRESH_TIME = 3 ##time to refresh the table, in seconds
AUTO_OR_NOT = True
column_names = ['ID', 'product_name', 'review_star', 'review_count', 'price', 'img_url', 'link', 'timeStamp']
last_refreshed_time = ' '
data_refresh = []

def main():
    path = '/Users/jiahuizeng/Desktop/web-scraping/sophera-scraping/chromedriver'
    url = 'https://www.sephora.com/shop/moisturizing-cream-oils-mists'
    #connect to databse
    data = crawl(path, url)
    df = dataframe(data)
    make_db_static(df)
    make_db_dynamic(df)

    data_refresh = data
    schedule.every(REFRESH_TIME).seconds.do(refresh_table, path, url)
    while (AUTO_OR_NOT): 
        schedule.run_pending()
        time.sleep(1)
    
    #print(last_refreshed_time)


def make_db_static(df):
    conn = sqlite3.connect('sephora.db')
    c = conn.cursor()
    #static databse
    new_df = df[['ID', 'product_name', 'review_star', 'review_count', 'price', 'img_url']].copy()
    new_df.to_sql(name = 'sephora_1', con=conn, if_exists='replace')
    new_df.to_csv('sephora_1.csv',sep ='\t', encoding='utf-8')
    #print(new_df)
    c.execute(''' SELECT * FROM sephora_1 LIMIT 3;''')


def make_db_dynamic(df):
    conn = sqlite3.connect('sephora.db')
    c = conn.cursor()
    new_df2 = df[['ID', 'product_name','timeStamp']].copy()
    new_df2.to_sql(name = 'sephora_2', con=conn, if_exists='replace')
    #c.execute('''SELECT * FROM sephora_2 LIMIT 3;''')

    new_df2.to_csv('sephora_dynamic_initial.csv',sep ='\t', encoding='utf-8')
    result2 = c.fetchall()
    print(result2)    
    conn.commit()
    conn.close()

def refresh_table(path, url):
    print('refresh_table')
    data2 = crawl(path, url)
    for data in data2:
        data_refresh.append(data)
    #print('data_refresh: \n ',data_refresh)
    ##put into database
    conn = sqlite3.connect('sephora.db')
    c = conn.cursor()
    #print('df: \n', df2)
    df_refresh = pd.DataFrame(data_refresh, columns= column_names)
    df_refresh.to_csv('sephora_refresh.csv',sep ='\t', encoding='utf-8') ##test right 

    new_df3 = df_refresh[['ID', 'product_name','timeStamp']].copy()
    new_df3.to_sql(name = 'sephora_2', con=conn, if_exists='replace')

    new_df3.to_csv('sephora_dynamic.csv',sep ='\t', encoding='utf-8')
    #result2 = c.fetchall()
    #print(result2) 

    conn.commit()
    conn.close()

def dataframe(data):
    df = pd.DataFrame(data, columns = column_names)
    #print(df, "\n")
    #df.to_csv(file_name, sep ='\t', encoding='utf-8')
    return df

##scrape data online and save it to a dataframe and a csv file 
def crawl(path, url): 
    print("inside crawl")
    driver = webdriver.Chrome(path)
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    driver.get(url)
    #last_height = driver.execute_script("return document.body.scrollHeight")
    #elems = driver.find_elements_by_class_name("css-dkxsdo")
    elems = driver.find_elements_by_class_name("css-12egk0t")
    #elems = driver.find_elements_by_class_name("css-1n99v7w")
    timeStamp = time.ctime(time.time())
    last_refreshed_time = timeStamp
    i= 0 
    data = []
    for elem in elems:
        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
        product_a_tag = elem.find_element(By.TAG_NAME, 'a')
        link = product_a_tag.get_attribute('href')
        img = elem.find_element(By.TAG_NAME, 'img')
        img_url = img.get_attribute('src')
        product_name = product_a_tag.get_attribute('aria-label')
        price = elem.find_element(By.CLASS_NAME, 'css-0').text
        review_star = elem.find_element(By.CLASS_NAME,'css-jp4jy6').get_attribute('aria-label')
        review_count = elem.find_element(By.CLASS_NAME,'css-1dk1ux').text
        print(i, ' ')
        time.sleep(SCROLL_PAUSE_TIME)
        #elem.click()
        #print(elem.text,'\n','link: ', link, '\n img_url: ', img_url, '\n')
        #print('product_name: ', product_name, '\n price: ', price, '\n')
        #print('review_star: ', review_star, '\n review_count: ', review_count, '\n')
        data.append([i,product_name, review_star, review_count, price, img_url, link, timeStamp])
        i = i+1
    driver.quit()
    return data

main()

